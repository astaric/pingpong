from itertools import cycle, chain
import string
from collections import defaultdict

from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from pingpong.helpers import berger_tables, shuffled


GENDER_CHOICES = (
    (0, _("Male")),
    (1, _("Female")),
)


class Player(models.Model):
    class Meta:
        verbose_name = _("player")
        verbose_name_plural = _("players")

    name = models.CharField(_("name"), max_length=50)
    surname = models.CharField(_("surname"), max_length=50)

    gender = models.IntegerField(_("gender"), choices=GENDER_CHOICES, null=True)

    club = models.CharField(_("club"), max_length=50, blank=True)
    category = models.ForeignKey('Category', verbose_name=_("category"), related_name='players', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.fill_gender()

        super(Player, self).save(*args, **kwargs)

    def fill_gender(self):
        if self.category is None:
            return

        if self.gender is None:
            self.gender = self.category.gender

    def __unicode__(self):
        return self.full_name()

    def full_name(self):
        return u"{} {}".format(self.name, self.surname)

    full_name.admin_order_field = 'surname'


class Category(models.Model):
    SINGLE = 0
    DOUBLE = 1
    TYPE_CHOICES = (
        (SINGLE, _("Single")),
        (DOUBLE, _("Double")),
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    name = models.CharField(_("name"), max_length=10)
    description = models.CharField(_("description"), max_length=50, blank=True)

    type = models.IntegerField(_("type"), choices=TYPE_CHOICES, default=0)

    gender = models.IntegerField(_("gender"), choices=GENDER_CHOICES, null=True)
    min_age = models.IntegerField(_("min age"), blank=True, null=True)
    max_age = models.IntegerField(_("max age"), blank=True, null=True)

    def create_groups(self, leaders=(), number_of_groups=0):
        Group.objects.filter(category=self).delete()

        if number_of_groups == 0:
            number_of_groups = len(leaders)

        if number_of_groups == 0:
            raise ValueError("You have to specify leaders or non zero number of groups.")

        groups = [Group.objects.create(name=string.ascii_uppercase[i], category=self)
                  for i in range(number_of_groups)]
        has_leader = {group: False for group in groups}
        clubs = {group: set() for group in groups}
        members = []

        leader_ids = set(l.id for l in leaders)
        other_players = list(shuffled(self.players.exclude(id__in=leader_ids)))
        first_skipped_player = None
        group_iterator = iter(cycle(groups))
        group = next(group_iterator)
        for player in chain(leaders, other_players):
            if player in leaders or player == first_skipped_player or player.club not in clubs[group]:
                is_leader = not has_leader[group]
                if is_leader:
                    has_leader[group] = True
                members.append(GroupMember(player=player, group=group, leader=is_leader))
                if player.club:
                    clubs[group].add(player.club)
                first_skipped_player = None
                group = next(group_iterator)
            else:
                if first_skipped_player is None:
                    first_skipped_player = player
                other_players.append(player)

        GroupMember.objects.bulk_create(members)
        group_members = defaultdict(list)
        for member in GroupMember.objects.filter(group__category=self).select_related('group'):
            group_members[member.group].append(member)

        matches = []
        for group in groups:
            for p1, p2 in berger_tables(len(group_members[group])):
                matches.append(Match(player1=group_members[group][p1].player,
                                     player2=group_members[group][p2].player,
                                     group=group,
                                     status=Match.PENDING))

            # Create a dummy match that will be used to assign table to the group.
            matches.append(Match(group=group, status=Match.READY))
        Match.objects.bulk_create(matches)

    def __unicode__(self):
        return self.name


class Table(models.Model):
    name = models.CharField(max_length=50)
    display_order = models.IntegerField()

    def __unicode__(self):
        return self.name

    _players = None

    @property
    def players(self):
        if self._players is None:
            if self.bracketslot_set.exists():
                self._players = sorted([bracket.player for bracket in self.bracketslot_set.all()],
                                       key=lambda x: x.id if hasattr(x, 'id') else '')
            elif self.group_set.exists():
                group = self.group_set.all()[0]
                self._players = group.category.description, group.name
            else:
                self._players = ('', '')

        return self._players

    def player1(self):
        return self.players[0]

    def player2(self):
        return self.players[1]

    def occupied(self):
        return self.players != ('', '')

    def match_started(self):
        if self.bracketslot_set.exists():
            return self.bracketslot_set.all()[0].match_start.strftime('%H:%M')
        else:
            return ''

    def current_matches(self):
        return self.all_matches.filter(status=Match.PLAYING)


class Match(models.Model):
    PENDING = 0
    READY = 1
    PLAYING = 2
    COMPLETE = 3
    DOUBLE = 4

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (READY, 'Ready'),
        (PLAYING, 'Playing'),
        (COMPLETE, 'Complete'),
        (COMPLETE, 'Double'),
    )

    class Meta:
        verbose_name = _("Match")
        verbose_name_plural = _("Matches")

    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    group = models.ForeignKey('Group', null=True)

    player1 = models.ForeignKey(Player, null=True, related_name='match_as_player1')
    player1_score = models.IntegerField(null=True)
    player1_bracket_slot = models.ForeignKey('bracket.BracketSlot', null=True, related_name='+')

    player2 = models.ForeignKey(Player, null=True, related_name='match_as_player2')
    player2_score = models.IntegerField(null=True)
    player2_bracket_slot = models.ForeignKey('bracket.BracketSlot', null=True, related_name='+')

    table = models.ForeignKey(Table, blank=True, null=True, related_name='all_matches')

    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    def set_score(self, player1_score, player2_score):
        self.player1_score = player1_score
        self.player2_score = player2_score

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.status == Match.PENDING:
            if self.player1_id and self.player2_id:
                self.status = Match.READY
        elif self.status == Match.READY or self.status == Match.DOUBLE:
            if self.table_id is not None:
                self.start_time = now()
                self.status = Match.PLAYING
        elif self.status == Match.PLAYING:
            if self.player1_score is not None and self.player2_score is not None:
                if self.player1_bracket_slot_id:
                    self.player1_bracket_slot.score = self.player1_score
                    self.player1_bracket_slot.save()
                if self.player2_bracket_slot_id:
                    self.player2_bracket_slot.score = self.player2_score
                    self.player2_bracket_slot.save()
                self.end_time = now()
                self.status = Match.COMPLETE
        super(Match, self).save(force_insert, force_update, using, update_fields)

    @staticmethod
    def ready_group_matches():
        group_matches = Match.objects.filter(status=Match.READY, group__isnull=False)
        return group_matches.select_related('group', 'group__category')

    @staticmethod
    def ready_bracket_matches():
        bracket_matches = Match.objects.filter(status=Match.READY, group__isnull=True)
        return bracket_matches.select_related('player1', 'player1__category', 'player1_bracket_slot__bracket',
                                              'player2')

    @staticmethod
    def ready_doubles_matches():
        occupied_with_singles = Double.objects.filter(
            Q(player1__match_as_player1__status__lt=Match.COMPLETE) |
            Q(player1__match_as_player2__status__lt=Match.COMPLETE) |
            Q(player2__match_as_player1__status__lt=Match.COMPLETE) |
            Q(player2__match_as_player2__status__lt=Match.COMPLETE)).values('id')

        return Match.objects.filter(status=Match.DOUBLE).exclude(
            Q(player1__isnull=True) | Q(player2__isnull=True) |
            Q(player1__in=occupied_with_singles) |
            Q(player2__in=occupied_with_singles)).select_related('player1', 'player1__double',
                                                                 'player1__category',
                                                                 'player2', 'player2__double',
                                                                 'player1_bracket_slot__bracket')
        # TODO: Filter blocking players in the same query
        #     d1, d2 = m.player1.double, m.player2.double
        #     required_players = [d1.player1_id, d1.player2_id, d2.player1_id, d2.player2_id]
        #     blocking_matches = Match.objects.filter(Q(player1__in=required_players) | Q(player2__in=required_players),
        #                                             status__lt=Match.COMPLETE)
        #     if not blocking_matches.exists():
        #         skip

    @staticmethod
    def current_matches():
        return Match.objects.filter(status=Match.PLAYING, group__isnull=True)

    def description(self):
        if self.group is not None:
            return unicode(self.group)
        else:
            b = self.player1_bracket_slot.bracket.name[0]
            l = self.player1_bracket_slot.level
            c = self.player1.category.name
            return mark_safe('%s <b>%s</b> %s %s : %s' % (b, l, c, self.player1, self.player2))

    def __unicode__(self):
        return u'%s %s' % (self.player1, self.player2)


class Double(Player):
    player1 = models.ForeignKey(Player, related_name='+')
    player2 = models.ForeignKey(Player, related_name='+')

    def save(self, *args, **kwargs):
        self.name = '%s. %s' % (self.player1.name[0], self.player1.surname)
        self.surname = '%s. %s' % (self.player2.name[0], self.player2.surname)
        super(Double, self).save(*args, **kwargs)


class Group(models.Model):
    STATUS = (
        (0, ''),
        (1, 'playing'),
        (2, 'completed')
    )

    name = models.CharField(max_length=10)
    category = models.ForeignKey(Category)

    table = models.ForeignKey(Table, blank=True, null=True)
    status = models.IntegerField(choices=STATUS, default=0)

    @property
    def members(self):
        return GroupMember.objects.filter(group=self) \
            .order_by('place', '-leader', 'player__surname') \
            .select_related('group', 'group__category', 'player')

    @property
    def match(self):
        return Match.objects.filter(group=self, player1=None, player2=None)

    def assign_table(self, table):
        Match.objects.filter(group=self).update(table=table,
                                                status=Match.PLAYING,
                                                start_time=now())

    def __unicode__(self):
        return u'{} - Skupina {}'.format(self.category, self.name)


class GroupMember(models.Model):
    player = models.ForeignKey(Player)
    group = models.ForeignKey(Group, related_name='members')

    place = models.IntegerField(blank=True, null=True)
    leader = models.BooleanField(default=False)

    @classmethod
    def for_category(cls, category):
        return cls.objects.filter(group__category=category) \
            .order_by('group', 'place', '-leader', 'player__surname') \
            .prefetch_related('group', 'group__category', 'player')

    @classmethod
    def for_group(cls, group):
        return cls.objects.filter(group=group) \
            .order_by('-leader', 'player__surname') \
            .prefetch_related('player')

    def __unicode__(self):
        return unicode(self.player)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        from pingpong.bracket.models import BracketSlot

        super(GroupMember, self).save(force_insert, force_update, using, update_fields)

        for match in Match.objects.filter(Q(player1=self.player) | Q(player2=self.player), group=self.group_id):
            match.table = None
            match.status = Match.COMPLETE
            match.save()
        for slot in BracketSlot.objects.filter(transition__group=self.group_id, transition__place=self.place):
            slot.player_id = self.player_id
            slot.save()
