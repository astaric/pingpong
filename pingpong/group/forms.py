# coding=utf-8
from django.core.exceptions import ValidationError
from django.forms import CharField, Form, IntegerField
from django.forms.models import modelformset_factory, ModelForm, BaseModelFormSet
from pingpong.bracket.helpers import create_brackets

from pingpong.models import Player, GroupMember


class SelectLeadersForm(ModelForm):
    class Meta:
        model = Player
        fields = ()

    leader = CharField(required=False)


class NumberOfGroupsForm(Form):
    number = IntegerField(label="Število skupin", required=True)

    def as_int(self):
        return self.cleaned_data['number']


class BaseLeaderFormSet(BaseModelFormSet):
    @property
    def leaders(self):
        leaders = [f for f in self.forms if f.cleaned_data['leader']]
        leaders.sort(key=lambda x: x.cleaned_data['leader'])
        return [f.instance for f in leaders]

    def create_groups(self, category, number_of_groups):
        leader = lambda x: x.cleaned_data['leader']
        forms = sorted(self.forms, key=leader)
        leaders = [f.instance for f in forms if leader(f)]
        category.create_groups(leaders, number_of_groups)
        create_brackets(category)


SelectLeadersFormSet = modelformset_factory(Player, SelectLeadersForm, formset=BaseLeaderFormSet, extra=0)


class GroupScoresForm(ModelForm):
    class Meta:
        model = GroupMember
        fields = ('id', 'place')

GroupScoresFormset = modelformset_factory(GroupMember, form=GroupScoresForm, extra=0)
