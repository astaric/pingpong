from django.db import models
from pingpong.models import Category, Table, Player


class Group(models.Model):
    name = models.CharField(max_length=10)
    category = models.ForeignKey(Category)

    table = models.ForeignKey(Table, blank=True, null=True)

    @property
    def members(self):
        return GroupMember.objects.filter(group=self)\
                                  .order_by('place', '-leader', 'player__surname')\
                                  .select_related('group', 'group__category', 'player')

    def __unicode__(self):
        return u'Skupina {}'.format(self.name)


class GroupMember(models.Model):
    player = models.ForeignKey(Player)
    group = models.ForeignKey(Group)

    place = models.IntegerField(blank=True, null=True)
    leader = models.BooleanField(default=False)

    @classmethod
    def for_category(cls, category):
        return cls.objects.filter(group__category=category)\
                          .order_by('group', 'place', '-leader', 'player__surname')\
                          .prefetch_related('group', 'group__category', 'player')

    def __unicode__(self):
        return unicode(self.player)
