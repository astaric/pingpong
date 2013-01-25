from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import PlayerManager, CategoryManager

GENDERS = (
    (0, _("Male")),
    (1, _("Female")),
    (2, ""),
    (3, ""),
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

    part_of_double = models.ForeignKey('Player', blank=True, null=True, related_name='double_members')

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

    @classmethod
    def double_from_players(cls, players):
        if len(players) != 2:
            raise ValueError("Invalid number of players")
        player1, player2 = players
        player = Player()
        player.name = unicode(player1)
        player.surname = unicode(player2)
        player.age = min(player1.age, player2.age)
        player.gender = min(player1.gender, player2.gender) + 2
        player.save()

        player1.part_of_double = player
        player1.save()
        player2.part_of_double = player
        player2.save()

        return player

    def __unicode__(self):
        return u"{} {}".format(self.name, self.surname)

    def full_name(self):
        return '%s %s' % (self.name, self.surname)


class Category(models.Model):
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    name = models.CharField(_("name"), max_length=10)
    description = models.CharField(max_length=50, blank=True)

    gender = models.IntegerField(_("gender"), choices=GENDERS)
    min_age = models.IntegerField(_("min age"), blank=True, null=True)
    max_age = models.IntegerField(_("max age"), blank=True, null=True)

    objects = CategoryManager()

    def __unicode__(self):
        return self.name
