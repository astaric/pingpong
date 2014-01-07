from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, Min, Q
from django.db.models.query import QuerySet
from django.utils import timezone

from pingpong.models import Category, Player, Table, Match, Group


class Bracket(models.Model):
    category = models.ForeignKey(Category)
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
        return self.get_query_set().with_two_players()

    def available_pairs(self):
        return (self.filter(winner_goes_to__winner_set__player_id__isnull=False)
                    .annotate(known_players=Count('winner_goes_to__winner_set', distinct=True),
                              minimal_status=Min('player__double_members__bracketslot__status'))
                    .filter(Q(minimal_status=2) | Q(minimal_status__isnull=True), known_players=2))


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
    player = models.ForeignKey(Player, blank=True, null=True)
    table = models.ForeignKey(Table, blank=True, null=True)
    score = models.IntegerField(null=True, blank=True)

    match_start = models.DateTimeField(null=True, blank=True)
    match_end = models.DateTimeField(null=True, blank=True)

    winner_goes_to = models.ForeignKey('BracketSlot', null=True, blank=True, related_name='winner_set')
    loser_goes_to = models.ForeignKey('BracketSlot', null=True, blank=True, related_name='loser_set')

    objects = BracketSlotManager()

    def save(self, *args, **kwargs):
        self.set_status()
        super(BracketSlot, self).save(*args, **kwargs)

        if self.player_id:
            for match in Match.objects.filter(player1_bracket_slot=self):
                if match.player1_id != self.player_id:
                    match.player1_id = self.player_id
                    match.save()
            for match in Match.objects.filter(player2_bracket_slot=self):
                if match.player2_id != self.player_id:
                    match.player2_id = self.player_id
                    match.save()
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
        if self.player_id is None:
            return
        other = BracketSlot.objects.exclude(id=self.id)\
                                   .filter(winner_goes_to=self.winner_goes_to)\
                                   .select_related('winner_goes_to', 'loser_goes_to')[0]
        if other.no_player:
            other.winner_goes_to.player_id = self.player_id
            other.winner_goes_to.save()

        if self.score is not None and other.score is not None:
            first, last = (self, other) if self.score > other.score else (other, self)
            if first.winner_goes_to is not None:
                first.winner_goes_to.player_id = first.player_id
                first.winner_goes_to.save()
            if last.loser_goes_to is not None:
                last.loser_goes_to.player_id = last.player_id
                last.loser_goes_to.save()

    def label(self):
        try:
            transition = '%s%s' % (self.transition.group.name, self.transition.place)
        except GroupToBracketTransition.DoesNotExist:
            transition = '&nbsp;'
        try:
            player = self.player.full_name() if self.player is not None else '&nbsp;'
        except Player.DoesNotExist:
            player = '&nbsp;'

        return transition, player

    def empty(self):
        return self.transition is None and self.player is None

    def get_admin_url(self):
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.module_name), args=(self.id,))

    def __unicode__(self):
        return '%s' % self.id


class GroupToBracketTransition(models.Model):

    group = models.ForeignKey(Group)
    place = models.IntegerField()

    slot = models.OneToOneField(BracketSlot, related_name='transition')
