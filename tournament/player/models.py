from django.db import models
from django.utils.translation import ugettext_lazy as _

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
    category = models.ForeignKey("Category", blank=True, null=True)

    def __unicode__(self):
        return "{} {}".format(self.name, self.surname)


class Category(models.Model):
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    name = models.CharField(_("category|name"), max_length=50)

    gender = models.IntegerField(_("category|gender"), choices=Player.GENDERS)
    min_age = models.IntegerField(_("category|minage"))
    max_age = models.IntegerField(_("category|maxage"))

    def __unicode__(self):
        return self.name