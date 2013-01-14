from django.db import models
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from ..registration import models as player_models


class Group(models.Model):
    name = models.CharField(max_length=10)
    category = models.ForeignKey(player_models.Category)

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
                BracketSlot.objects.filter(id=slot.winner_goes_to_id).update(player=self.player_id)
        except BracketSlot.DoesNotExist:
            pass


class Bracket(models.Model):
    category = models.ForeignKey(player_models.Category)
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=50)

    levels = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s - %s' % (self.category.name, self.name)


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

    winner_goes_to = models.ForeignKey('BracketSlot', null=True, blank=True, related_name='+')
    loser_goes_to = models.ForeignKey('BracketSlot', null=True, blank=True, related_name='+')

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
            self._players = sorted([bracket.player for bracket in self.bracketslot_set.all()],
                                   key=lambda x: x.id) or ['', '']

        return self._players

    def player1(self):
        return self.players[0]

    def player2(self):
        return self.players[1]

    def occupied(self):
        return self.players != ['', '']

    def __unicode__(self):
        return self.name
