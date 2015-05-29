from django.forms import ModelForm, ModelMultipleChoiceField
from cmdb.models import *

class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = '__all__' # Or a list of the fields that you want to include in your form

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(ServiceForm, self).save(commit=False)

        if commit:
            m.save()
        return m

