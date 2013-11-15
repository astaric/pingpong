from django.core.exceptions import ValidationError
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

    _players = None

    @property
    def players(self):
        if self._players is None:
            if self.bracketslot_set.exists():
                self._players = sorted([bracket.player for bracket in self.bracketslot_set.all()],
                                       key=lambda x: x.id if hasattr(x, 'id') else '')
            elif self.group_set.exists():
                group = self.group_set.all()[0]
                self._players = group.category.description, group.name
            else:
                self._players = ('', '')

        return self._players

    def player1(self):
        return self.players[0]

    def player2(self):
        return self.players[1]

    def occupied(self):
        return self.players != ('', '')

    def match_started(self):
        if self.bracketslot_set.exists():
            return self.bracketslot_set.all()[0].match_start.strftime('%H:%M')
        else:
            return ''


class Match(models.Model):
    PENDING = 0
    READY = 1
    PLAYING = 2
    COMPLETE = 3

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (READY, 'Ready'),
        (PLAYING, 'Playing'),
        (COMPLETE, 'Complete'),
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    group = models.ForeignKey('group.Group', null=True)

    player1 = models.ForeignKey(Player, null=True, related_name='+')
    player1_score = models.IntegerField(null=True)
    player1_bracket_slot = models.ForeignKey('bracket.BracketSlot', null=True, related_name='+')

    player2 = models.ForeignKey(Player, null=True, related_name='+')
    player2_score = models.IntegerField(null=True)
    player2_bracket_slot = models.ForeignKey('bracket.BracketSlot', null=True, related_name='+')

    table = models.ForeignKey(Table, blank=True, null=True, related_name='matches')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.status == Match.PENDING:
            if self.player1_id and self.player2_id:
                self.status = Match.READY
        elif self.status == Match.READY:
            if self.table_id is not None:
                self.status = Match.PLAYING
        elif self.status == Match.PLAYING:
            if self.player1_score is not None and self.player2_score is not None:
                if self.player1_bracket_slot:
                    self.player1_bracket_slot.score = self.player1_score
                    self.player1_bracket_slot.save()
                if self.player2_bracket_slot:
                    self.player2_bracket_slot.score = self.player2_score
                    self.player2_bracket_slot.save()
                self.table = None
                self.status = Match.COMPLETE

        super(Match, self).save(force_insert, force_update, using, update_fields)



    def __unicode__(self):
        return '%s %s' % (self.player1, self.player2)


