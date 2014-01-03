from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm, CharField
from django.forms.models import modelformset_factory, BaseModelFormSet
import re

from pingpong.models import Table, Match


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

UpcomingMatchesFromset = modelformset_factory(Match, UpcomingMatchModelForm, formset=BaseUpcomingMatchesFromset, extra=0)


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

CurrentMatchesFromset = modelformset_factory(Match, form=CurrentMatchForm, extra=0)


class SetScoreForm(ModelForm):
    class Meta:
        model = Match
        fields = ('player1_score', 'player2_score')
