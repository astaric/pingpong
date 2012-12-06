from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

from .managers import PlayerManager, CategoryManager

GENDERS = (
    (0, _("Male")),
    (1, _("Female")),
)


class Player(models.Model):
    class Meta:
        verbose_name = _("player")
        verbose_name_plural = _("players")

    name = models.CharField(_("name"), max_length=50)
    surname = models.CharField(_("surname"), max_length=50)

    gender = models.IntegerField(_("gender"), choices=GENDERS)
    age = models.IntegerField(_("age"))

    club = models.CharField(_("club"), max_length=50, blank=True)
    category = models.ForeignKey('Category', verbose_name=_("category"), blank=True, null=True)

    objects = PlayerManager()

    def save(self, *args, **kwargs):
        self.fill_category()

        super(Player, self).save(*args, **kwargs)

    def fill_category(self):
        if self.category is not None:
            return
        try:
            self.category = Category.objects.all().matching_player(self).get()
        except Category.DoesNotExist:
            pass

    def __unicode__(self):
        return "{} {}".format(self.name, self.surname)


class PlayerByGroup(Player):
    class Meta:
        proxy = True
        verbose_name = _("player by group")
        verbose_name_plural = _("players by groups")


class Category(models.Model):
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    name = models.CharField(_("name"), max_length=50)

    gender = models.IntegerField(_("gender"), choices=GENDERS)
    min_age = models.IntegerField(_("min age"), blank=True, null=True)
    max_age = models.IntegerField(_("max age"), blank=True, null=True)

    objects = CategoryManager()

    def __unicode__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey('Category')

    def __unicode__(self):
        return '{} - {}'.format(self.category, self.name)


class GroupMember(models.Model):
    player = models.ForeignKey('Player')
    group = models.ForeignKey('Group')

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
    category = models.ForeignKey(Category)
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
    player = models.ForeignKey(Player)
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
