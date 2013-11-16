from django.db import models
from django.db.models import Q
from pingpong.models import Category, Table, Player, Match


class Group(models.Model):
    STATUS = (
        (0, ''),
        (1, 'playing'),
        (2, 'completed')
    )

    name = models.CharField(max_length=10)
    category = models.ForeignKey(Category)

    table = models.ForeignKey('Table', blank=True, null=True)

    table = models.ForeignKey(Table, blank=True, null=True)
    status = models.IntegerField(choices=STATUS, default=0)

    @property
    def members(self):
        return GroupMember.objects.filter(group=self)\
                                  .order_by('place', '-leader', 'player__surname')\
                                  .select_related('group', 'group__category', 'player')

    def __unicode__(self):
        return u'{} - Skupina {}'.format(self.category, self.name)


class GroupMember(models.Model):
    player = models.ForeignKey(Player)
    group = models.ForeignKey(Group, related_name='members')

    place = models.IntegerField(blank=True, null=True)
    leader = models.BooleanField(default=False)

    @classmethod
    def for_category(cls, category):
        return cls.objects.filter(group__category=category)\
                          .order_by('group', 'place', '-leader', 'player__surname')\
                          .prefetch_related('group', 'group__category', 'player')

    @classmethod
    def for_group(cls, group):
        return cls.objects.filter(group=group)\
                          .order_by('-leader', 'player__surname')\
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