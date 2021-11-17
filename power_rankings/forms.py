from django.forms import ModelForm, Textarea
from django.forms.formsets import BaseFormSet
from .models import Team

class power_ranks(ModelForm):
    class Meta:
        model = Team
        fields = ['rank','comments']
        widgets = {
            'comments': Textarea(attrs={'cols': 80, 'rows': 20}),
        }



