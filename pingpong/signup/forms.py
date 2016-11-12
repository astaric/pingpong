from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, IntegerField, CharField, Form
from django.forms.models import ModelForm, modelformset_factory, BaseModelFormSet
from django.utils.translation import ugettext_lazy as _

from pingpong.bracket.helpers import create_brackets, create_pair_brackets

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
    player1 = ModelChoiceField(required=False, queryset=Player.objects
                               .filter(category__type=Category.SINGLE)
                               .order_by('surname'))
    player2 = ModelChoiceField(required=False, queryset=Player.objects
                               .filter(category__type=Category.SINGLE)
                               .order_by('surname'))

    class Meta:
        model = Double
        fields = ['player1', 'player2']


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


class PlayerSeedForm(ModelForm):
    class Meta:
        model = Player
        fields = ()

    seed = CharField(required=False)


class BaseLeaderFormSet(BaseModelFormSet):
    @property
    def seeds(self):
        seed = lambda x: x.cleaned_data['seed']
        forms = sorted(self.forms, key=seed)
        return [f.instance for f in forms if seed(f)]

    def create_groups(self, category, number_of_groups):
        category.create_groups(self.seeds, number_of_groups)
        create_brackets(category)

    def create_bracket(self, category):
        create_pair_brackets(category, self.seeds)


PlayerSeedsFormset = modelformset_factory(Player, PlayerSeedForm, formset=BaseLeaderFormSet, extra=0)
