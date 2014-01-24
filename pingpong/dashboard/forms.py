import re

from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm, CharField, IntegerField
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.utils import timezone

from pingpong.models import Table, Match, GroupMember


class UpcomingMatchModelForm(ModelForm):
    table = ModelChoiceField(required=False, queryset=Table.objects.exclude(all_matches__status=Match.PLAYING))

    class Meta:
        model = Match
        fields = ['table']

    def save(self, commit=True):
        if not self.cleaned_data['table']:
            return

        if self.instance.group is not None:
            self.instance.group.assign_table(self.cleaned_data['table'])
        else:
            self.instance.table = self.cleaned_data['table']
            self.instance.save()


class BaseUpcomingMatchesFromset(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return

        tables = set()
        duplicate_tables = {}
        for form in self.forms:
            table = form.cleaned_data['table']
            if table is not None and table in tables:
                duplicate_tables.setdefault(table, []).append(form)
            tables.add(table)

        for table, forms in duplicate_tables.items():
            pass

        if duplicate_tables:
            raise ValidationError([ValidationError("Multiple matches are assigned to table %s." % table)
                                   for table in duplicate_tables])


UpcomingMatchesFromset = modelformset_factory(
    Match,
    form=UpcomingMatchModelForm,
    formset=BaseUpcomingMatchesFromset,
    extra=0
)


class CurrentMatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ()

    score = CharField(required=False)

    def clean_score(self):
        score = self.cleaned_data.get('score', None)
        if score:
            match = re.match(r'(\d+)[^\d]+(\d+)', score)
            if match:
                scores = map(int, match.groups())
                self.instance.set_score(*scores)
            else:
                raise ValidationError('Invalid score.')


CurrentMatchesFromset = modelformset_factory(
    Match,
    form=CurrentMatchForm, extra=0
)


class SetScoreForm(ModelForm):
    class Meta:
        model = Match
        fields = ('player1_score', 'player2_score')


class SetTableForm(ModelForm):
    class Meta:
        model = Match
        fields = ('table',)


class GroupScoresForm(ModelForm):
    class Meta:
        model = GroupMember
        fields = ('id', 'place')


class BaseGroupScoresFormset(BaseModelFormSet):
    def clean(self):
        used_places = set()
        for form in self.forms:
            place = form.cleaned_data.get('place')
            if place is not None:
                if place < 1 or place > len(self.forms):
                    raise ValidationError('Place should be between 1 and %s' % len(self.forms))

                if place in used_places:
                    raise ValidationError('More than one member is assigned to place %s' % place)

                used_places.add(place)

    def save(self, commit=True):
        instances = super(BaseGroupScoresFormset, self).save(commit)

        if commit and instances and all(f.cleaned_data['place'] for f in self.forms):
            Match.objects\
                .filter(group=instances[0].group)\
                .update(end_time=timezone.now(), status=Match.COMPLETE)


GroupScoresFormset = modelformset_factory(
    GroupMember,
    form=GroupScoresForm,
    formset=BaseGroupScoresFormset,
    extra=0
)
