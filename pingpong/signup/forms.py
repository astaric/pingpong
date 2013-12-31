from django.forms import ModelChoiceField, IntegerField
from django.forms.models import ModelForm, modelformset_factory, BaseModelFormSet

from pingpong.models import Double, Player, Category


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'type']


class SimpleCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class SimpleDoubleForm(ModelForm):
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
DoubleFormSet = modelformset_factory(Double, extra=3, form=SimpleDoubleForm,
                                     formset=BasePlayersFormSet, can_delete=True)
