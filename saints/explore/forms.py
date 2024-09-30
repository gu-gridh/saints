from django import forms
from .models import CultType


class CultTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CultTypeForm, self).__init__(*args, **kwargs)
        if self.instance.level == "Subcategory":
            self.fields['parent'].queryset = CultType.objects.filter(
                                                level__exact="Intermediate")
        elif self.instance.level == "Intermediate":
            self.fields['parent'].queryset = CultType.objects.filter(
                                                level__exact="Type of Evidence")
        elif self.instance.level == "Type of Evidence":
            self.fields['parent'].disabled = True
        else:
            self.fields['parent'].queryset = CultType.objects.filter(
                                                level__in=["Type of Evidence",
                                                           "Intermediate"])
