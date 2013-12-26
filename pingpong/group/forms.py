# coding=utf-8
from django.forms import CharField, Form, IntegerField
from django.forms.models import modelformset_factory, ModelForm, BaseModelFormSet

from pingpong.models import Player, GroupMember


class SelectLeadersForm(ModelForm):
    class Meta:
        model = Player
        fields = ()

    leader = CharField(required=False)


class BaseLeaderFormSet(BaseModelFormSet):
    def leaders(self):
        leaders = [f for f in self.forms if f.cleaned_data['leader']]
        leaders.sort(key=lambda x: x.cleaned_data['leader'])
        return [f.instance for f in leaders]


SelectLeadersFormSet = modelformset_factory(Player, SelectLeadersForm, formset=BaseLeaderFormSet, extra=0)


class NumberOfGroupsForm(Form):
    number = IntegerField(label="Število skupin", required=True)


class GroupScoresForm(ModelForm):
    class Meta:
        model = GroupMember
        fields = ('id', 'place')

GroupScoresFormset = modelformset_factory(GroupMember, form=GroupScoresForm, extra=0)
