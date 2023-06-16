from django import forms
from folder.models import File

class FileCreateForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'content', 'patient_sign', 'doctor_sign']