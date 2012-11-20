from collections import defaultdict
import random

from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

class PlayerQuerySet(QuerySet):
    def matching_category(self, category):
        filters = {'gender': category.gender}
        if category.min_age is not None:
            filters["age__gte"] = category.min_age
        if category.max_age is not None:
            filters["age__lte"] = category.max_age

        return self.filter(**filters)

class PlayerManager(models.Manager):
    def get_query_set(self):
        return PlayerQuerySet(self.model)

class Player(models.Model):
    class Meta:
        verbose_name = _("player")
        verbose_name_plural = _("players")

    GENDERS = ( (0, _("Male") ), (1, _("Female") ), )

    name = models.CharField(_("player|name"), max_length=50)
    surname = models.CharField(_("player|surname"), max_length=50)

    gender = models.IntegerField(_("player|gender"), choices=GENDERS)
    age = models.IntegerField(_("player|age"))

    club = models.CharField(_("player|club"), max_length=50, blank=True)
    category = models.ForeignKey('Category', verbose_name=_("player|category"), blank=True, null=True)

    group = models.ForeignKey('Group', blank=True, null=True, verbose_name=_("player|group"))
    group_member_no = models.IntegerField(_("player|placeingroup"), blank=True, null=True)
    group_leader = models.BooleanField(_("player|groupleader"), default=False)

    objects = PlayerManager()

    def save(self, *args, **kwargs):
        if self.category is None:
            try:
                self.category = Category.objects.all().matching_player(self).get()
            except Category.DoesNotExist:
                pass
        super(Player, self).save(*args, **kwargs)

    def __unicode__(self):
        return "{} {}".format(self.name, self.surname)

class PlayerByGroup(Player):
    class Meta:
        proxy = True
        verbose_name = _("player by group")
        verbose_name_plural = _("players by groups")


class CategoryQuerySet(QuerySet):
    def matching_player(self, player):
        return self.filter(gender=player.gender)\
                   .exclude(min_age__gt=player.age)\
                   .exclude(max_age__lt=player.age)

class CategoryManager(models.Manager):
    def get_query_set(self):
        return CategoryQuerySet(self.model)

class Category(models.Model):
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    name = models.CharField(_("category|name"), max_length=50)

    gender = models.IntegerField(_("category|gender"), choices=Player.GENDERS)
    min_age = models.IntegerField(_("category|minage"), blank=True, null=True)
    max_age = models.IntegerField(_("category|maxage"), blank=True, null=True)

    objects = CategoryManager()


    def __unicode__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey('Category')

    @staticmethod
    def create_from_leaders(leaders):
        categories = set(map(lambda x:x["category"], leaders.values('category')))
        Player.objects.filter(category__in=categories)\
                      .update(group=None, group_member_no=None, group_leader=False)
        Group.objects.filter(category__in=categories).delete()

        for category in categories:
            qs = leaders.filter(category=category)
            groups = []
            for i, leader in enumerate(qs):
                group = Group(name=_("Group %s") % "ABCDEFGHIJKL"[i], category_id=category)
                group.save()
                leader.group=group
                leader.group_leader=True
                leader.save()
                groups.append(group)

            members = defaultdict(list)
            available_players = list(Player.objects.filter(category=category, group_leader=False))
            while available_players:
                rnd = random.randint(0, len(available_players)-1)
                player = available_players[rnd]
                if any(other.club == player.club for other in members[groups[0]] if other.club):
                    continue
                player.group=groups[0]
                player.save()
                groups = groups[1:] + groups[0:1]
                del available_players[rnd]

    def __unicode__(self):
        return '{} - {}'.format(self.category, self.name)
