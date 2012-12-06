from django.db import models, IntegrityError

from ..player import models as player_models


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
            transition = GroupToBracketTransition.objects.get(group=self.group_id, place=self.place)
            Match.objects.create(bracket=transition.bracket, player=self.player)
        except (GroupToBracketTransition.DoesNotExist, IntegrityError):
            pass


class Bracket(models.Model):
    category = models.ForeignKey(player_models.Category)
    level = models.IntegerField()

    winner_goes_to = models.ForeignKey('Bracket', blank=True, null=True, related_name='+')
    winner_order = models.IntegerField(default=0)

    loser_goes_to = models.ForeignKey('Bracket', blank=True, null=True, related_name='+')
    loser_order = models.IntegerField(default=0)


class Match(models.Model):
    class Meta:
        unique_together = (('bracket', 'player'),)

    bracket = models.ForeignKey(Bracket)
    order = models.IntegerField(default=0)

    table = models.CharField(max_length=50, blank=True)
    player = models.ForeignKey(player_models.Player)
    score = models.IntegerField(null=True)


class GroupToBracketTransition(models.Model):
    class Meta:
        unique_together = (('group', 'place'),)

    group = models.ForeignKey(Group)
    place = models.IntegerField()

    bracket = models.ForeignKey(Bracket)
    order = models.IntegerField(default=0)


class SetScore(models.Model):
    match = models.ForeignKey(Match)

    set = models.IntegerField()
    score = models.IntegerField()
