from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, IntegerField, CharField, Form
from django.forms.models import ModelForm, modelformset_factory, BaseModelFormSet
from django.utils.translation import ugettext_lazy as _

from pingpong.bracket.helpers import create_brackets

from pingpong.models import Player, GroupMember, Double, Category, Match


class CategoryAddForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'type']


class CategoryEditForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class DoubleEditForm(ModelForm):
    player1 = ModelChoiceField(required=False, queryset=Player.objects.order_by('surname'))
    player2 = ModelChoiceField(required=False, queryset=Player.objects.order_by('surname'))

    class Meta:
        model = Double
        fields = ['player1', 'player2']

    seed = IntegerField(required=False)


class BasePlayersFormSet(BaseModelFormSet):
    category = None

    def save(self, commit=True):
        instances = super(BasePlayersFormSet, self).save(False)
        if commit:
            for instance in instances:
                if instance.category_id is None:
                    instance.category = self.category
                instance.save()
        return instances

    def seeds(self):
        seeds = [f for f in self.forms if f.cleaned_data.get('seed', None)]
        seeds.sort(key=lambda x: x.cleaned_data['seed'])
        return [f.instance for f in seeds]


PlayerFormSet = modelformset_factory(Player, extra=3, fields=['name', 'surname', 'club'],
                                     formset=BasePlayersFormSet, can_delete=True)
DoubleFormSet = modelformset_factory(Double, extra=3, form=DoubleEditForm,
                                     formset=BasePlayersFormSet, can_delete=True)


class NumberOfGroupsForm(Form):
    number = IntegerField(label=_("Number of groups"), required=True)

    def as_int(self):
        return self.cleaned_data['number']


class SelectLeadersForm(ModelForm):
    class Meta:
        model = Player
        fields = ()

    leader = CharField(required=False)


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
            instances[0].group.match.update(status=Match.COMPLETE)

GroupScoresFormset = modelformset_factory(GroupMember, form=GroupScoresForm, formset=BaseGroupScoresFormset, extra=0)
