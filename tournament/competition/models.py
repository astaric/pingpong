from django.db import models
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from ..registration import models as player_models


class Group(models.Model):
    name = models.CharField(max_length=50)
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
            bracket_slot = BracketSlot.objects.get(transition__group_id=self.group_id, transition__place=self.place)
            bracket_slot.player_id = self.player_id
            bracket_slot.save()
        except BracketSlot.DoesNotExist:
            pass


class Bracket(models.Model):
    category = models.ForeignKey(player_models.Category)
    name = models.CharField(max_length=50)

    def __str__(self):
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

    player = models.ForeignKey(player_models.Player, blank=True, null=True)
    table = models.CharField(max_length=50, blank=True)
    score = models.IntegerField(null=True)

    winner_goes_to = models.ForeignKey('BracketSlot', null=True, related_name='+')
    loser_goes_to = models.ForeignKey('BracketSlot', null=True, related_name='+')

    def label(self):
        label = []
        if self.transition is not None:
            label.append('%s%s' % (self.transition.group.name, self.transition.place))
        if self.player is not None:
            label.append(self.player.full_name())
        return " ".join(label)

    def __str__(self):
        return '%s' % self.id

    def get_admin_url(self):
        return urlresolvers.reverse("admin:%s_%s_change" %
                                    (self._meta.app_label, self._meta.module_name), args=(self.id,))


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
    ORIENTATIONS = ((0, _("Potrait")), (1, _('Landscape')))

    name = models.CharField(max_length=50)

    orientation = models.IntegerField(choices=ORIENTATIONS, default=1)
    x = models.IntegerField()
    y = models.IntegerField()
