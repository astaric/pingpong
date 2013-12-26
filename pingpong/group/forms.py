from django.core.exceptions import ValidationError
from django.forms import CharField
from django.forms.models import modelformset_factory, ModelForm, BaseModelFormSet
from pingpong.models import Player, GroupMember


class SelectLeadersForm(ModelForm):
    class Meta:
        model = Player
        fields = ()

    leader = CharField(required=False)


class BaseLeaderFormSet(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        has_leaders = False
        for form in self.forms:
            if form.cleaned_data['leader']:
                has_leaders = True
        if not has_leaders:
            raise ValidationError("You have to select at least one leader.")

    def leaders(self):
        leaders = [f for f in self.forms if f.cleaned_data['leader']]
        leaders.sort(key=lambda x: x.cleaned_data['leader'])
        return [f.instance for f in leaders]


SelectLeadersFormSet = modelformset_factory(Player, SelectLeadersForm, formset=BaseLeaderFormSet, extra=0)


class GroupScoresForm(ModelForm):
    class Meta:
        model = GroupMember
        fields = ('id', 'place')

GroupScoresFormset = modelformset_factory(GroupMember, form=GroupScoresForm, extra=0)
