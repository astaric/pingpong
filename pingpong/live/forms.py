from django.forms import ModelChoiceField, ModelForm
from django.forms.models import modelformset_factory

from pingpong.models import Table, Match


class UpcomingMatchModelForm(ModelForm):
    table = ModelChoiceField(required=False, queryset=Table.objects.filter(all_matches__isnull=True))

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


UpcomingMatchesFromset = modelformset_factory(Match, UpcomingMatchModelForm, extra=0)
