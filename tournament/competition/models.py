from django.utils import timezone

from django.db import models
from django.db.models import Count, Max
from django.db.models.query import QuerySet
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from ..registration import models as player_models


class Group(models.Model):
    STATUS = (
        (0, ''),
        (1, 'playing'),
        (2, 'completed')
    )

    name = models.CharField(max_length=10)
    category = models.ForeignKey(player_models.Category)

    table = models.ForeignKey('Table', blank=True, null=True)
    status = models.IntegerField(choices=STATUS, default=0)

    def member_list(self):
        return GroupMember.objects.filter(group=self).order_by('place', '-leader', 'player__surname').select_related('group', 'group__category', 'player')

    def save(self, *args, **kwargs):
        self.update_status()
        super(Group, self).save(*args, **kwargs)

    def update_status(self):
        if self.table is None:
            return
        else:
            self.status = 1

    def __unicode__(self):
        return '{} - {}'.format(self.category, self.name)


class GroupMember(models.Model):
    player = models.ForeignKey(player_models.Player)
    group = models.ForeignKey('Group', related_name='members')

    place = models.IntegerField(blank=True, null=True)
    leader = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(GroupMember, self).save(*args, **kwargs)

        self.add_to_bracket()
        self.update_group_status()

    def add_to_bracket(self):
        if self.place is None:
            return
        try:
            BracketSlot.objects.filter(player=self.player_id).update(player=None)
            slot = BracketSlot.objects.get(transition__group_id=self.group_id, transition__place=self.place)
            slot.player_id = self.player_id
            slot.save()
            slot2 = BracketSlot.objects.exclude(id=slot.id).get(winner_goes_to=slot.winner_goes_to)
            if slot2.no_player:
                slot.status = 2
                slot.save()
                BracketSlot.objects.filter(id=slot.winner_goes_to_id).update(player=self.player_id)
        except BracketSlot.DoesNotExist:
            pass

    def update_group_status(self):
        if self.place is None:
            return
        try:
            group = Group.objects.get(id=self.group_id)
            if group.status < 2:
                group.table = None
                group.status = 2
                group.save()
        except Group.DoesNotExist:
            pass

    @staticmethod
    def with_same_group_as(member):
        if isinstance(member, GroupMember):
            member_group = member.group_id
        else:
            member_group = GroupMember.objects.filter(id=member).values_list('group_id', flat=True)
        return GroupMember.objects.filter(group_id=member_group)


class Bracket(models.Model):
    category = models.ForeignKey(player_models.Category)
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=50)

    levels = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s - %s' % (self.category.name, self.name)


class BracketSlotQuerySet(QuerySet):
    def with_two_players(self):
        subquery = BracketSlot.objects.exclude(player=None)\
                                      .values('winner_goes_to_id')\
                                      .annotate(icount=Count('id'))\
                                      .filter(icount=2)\
                                      .values('winner_goes_to_id')
        return self.filter(winner_goes_to_id__in=subquery)

class BracketSlotManager(models.Manager):
    def get_query_set(self):
        return BracketSlotQuerySet(self.model)

    def with_two_players(self):
        return self.all().with_two_players()

    def available_matches(self):

        return self.raw(
            '''SELECT s.*
                 FROM competition_bracketslot s
           INNER JOIN competition_bracket b ON b.id = s.bracket_id
           INNER JOIN registration_category c ON c.id = b.category_id
           INNER JOIN competition_bracketslot s2 ON s2.winner_goes_to_id = s.winner_goes_to_id
                WHERE c.gender < 2
                  AND s2.player_id IS NOT NULL
                  AND s.status = 0
             GROUP BY s.id
               HAVING COUNT(s2.id) = 2''',
            [0]
        )
        return self.filter(bracket__category__gender__lt=2)

    def available_pair_matches(self):
        return self.raw(
            '''SELECT s.*
                 FROM competition_bracketslot s
           INNER JOIN competition_bracket b ON b.id = s.bracket_id
           INNER JOIN registration_category c ON c.id = b.category_id
           INNER JOIN registration_player p ON p.id = s.player_id
           INNER JOIN competition_bracketslot s2 ON s2.winner_goes_to_id = s.winner_goes_to_id
           INNER JOIN registration_player p3 ON p3.part_of_double_id = p.id
           LEFT JOIN competition_bracketslot s3 ON s3.player_id = p3.id
                WHERE c.gender >= 2
                  AND s.status = 0
                  AND s2.player_id IS NOT NULL
             GROUP BY s.id
               HAVING COUNT(DISTINCT s2.id) = 2
                  AND coalesce(MIN(s3.status), 2) = 2'''
        )

class BracketSlot(models.Model):
    STATUS = (
        (0, ''),
        (1, 'playing'),
        (2, 'completed')
    )

    bracket = models.ForeignKey(Bracket)
    level = models.IntegerField()
    status = models.IntegerField(choices=STATUS, default=0)

    no_player = models.BooleanField(default=False)
    player = models.ForeignKey(player_models.Player, blank=True, null=True)
    table = models.ForeignKey('Table', blank=True, null=True)
    score = models.IntegerField(null=True, blank=True)

    match_start = models.DateTimeField(null=True, blank=True)
    match_end = models.DateTimeField(null=True, blank=True)

    winner_goes_to = models.ForeignKey('BracketSlot', null=True, blank=True, related_name='winner_set')
    loser_goes_to = models.ForeignKey('BracketSlot', null=True, blank=True, related_name='loser_set')

    objects = BracketSlotManager()

    def save(self, *args, **kwargs):
        self.set_status()
        super(BracketSlot, self).save(*args, **kwargs)
        self.advance_player()

    def set_status(self):
        if self.table_id is not None and self.status != 1:
            self.status = 1
            self.match_start = timezone.now()

        if self.score is not None and self.status != 2:
            self.table = None
            self.status = 2
            self.match_end = timezone.now()

        if self.level == 0 and self.player_id is not None:
            self.status = 2

    def advance_player(self):
        if self.score is None:
            return

        other = BracketSlot.objects.exclude(id=self.id)\
                                   .get(winner_goes_to=self.winner_goes_to)\
                                   .select_related('winner_goes_to', 'loser_goes_to')
        if other.score is not None:
            first, last = (self, other) if self.score > other.score else (other, self)
            if other.winner_goes_to is not None:
                other.winner_goes_to.player_id = first.player_id
                other.winner_goes_to.save()
            if other.loser_goes_to is not None:
                other.loser_goes_to.player_id = last.player_id
                other.loser_goes_to.save()

    def label(self):
        return (
            '%s%s' % (self.transition.group.name, self.transition.place) if self.transition is not None else '&nbsp;',
            self.player.full_name() if self.player is not None else '&nbsp;',
        )

    def empty(self):
        return self.transition is None and self.player is None

    def get_admin_url(self):
        return urlresolvers.reverse("admin:%s_%s_change" %
                                    (self._meta.app_label, self._meta.module_name), args=(self.id,))

    def __unicode__(self):
        return '%s' % self.id


class GroupToBracketTransition(models.Model):
    class Meta:
        unique_together = (
            ('group', 'place'),
            ('slot',)
        )

    group = models.ForeignKey(Group)
    place = models.IntegerField()

    slot = models.OneToOneField(BracketSlot, related_name='transition')


class SetScore(models.Model):
    match = models.ForeignKey(BracketSlot)

    set = models.IntegerField()
    score = models.IntegerField()


class Table(models.Model):
    name = models.CharField(max_length=50)
    sort_order = models.IntegerField()

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
                self._players = ('','')

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

    def __unicode__(self):
        return self.name
