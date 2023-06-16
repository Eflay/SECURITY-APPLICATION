from django import forms
from .models import Accord

class DoctorAddPatientForm(forms.Form):
    email = forms.CharField(label="Adresse mail du patient", max_length=254)

class AccordCreateForm(forms.ModelForm):
    class Meta:
        model = Accord
        fields = ['protected_symetric_key']
