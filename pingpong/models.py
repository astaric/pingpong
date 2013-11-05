from django.db import models
from django.utils.translation import ugettext_lazy as _

GENDER_CHOICES = (
    (0, _("Male")),
    (1, _("Female")),
)


class Player(models.Model):
    class Meta:
        verbose_name = _("player")
        verbose_name_plural = _("players")

    name = models.CharField(_("name"), max_length=50)
    surname = models.CharField(_("surname"), max_length=50)

    gender = models.IntegerField(_("gender"), choices=GENDER_CHOICES, null=True)

    club = models.CharField(_("club"), max_length=50, blank=True)
    category = models.ForeignKey('Category', verbose_name=_("category"), related_name='players', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.fill_gender()

        super(Player, self).save(*args, **kwargs)

    def fill_gender(self):
        if self.category is None:
            return

        if self.gender is None:
            self.gender = self.category.gender

    def __unicode__(self):
        return self.full_name()

    def full_name(self):
        return u"{} {}".format(self.name, self.surname)

    full_name.admin_order_field = 'surname'


class Category(models.Model):
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    name = models.CharField(_("name"), max_length=10)
    description = models.CharField(max_length=50, blank=True)

    gender = models.IntegerField(_("gender"), choices=GENDER_CHOICES)
    min_age = models.IntegerField(_("min age"), blank=True, null=True)
    max_age = models.IntegerField(_("max age"), blank=True, null=True)

    def __unicode__(self):
        return self.name


class Table(models.Model):
    name = models.CharField(max_length=50)
    display_order = models.IntegerField()

    def __unicode__(self):
        return self.name
