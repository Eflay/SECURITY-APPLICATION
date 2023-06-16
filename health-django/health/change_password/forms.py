from django import forms
from account.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import  PasswordChangeForm
from rest_framework import serializers
from folder.models import File
from accord.models import Accord


class ChangePassword(PasswordChangeForm):

    class Meta:
      model = get_user_model()
      fields = ('email','password','protected_symetric_key', "public_key", "protected_private_key")
      
      widgets = {
            'protected_symetric_key': forms.HiddenInput(),
            'protected_private_key': forms.HiddenInput(),
            'public_key': forms.HiddenInput()
        }


class FileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex')
    class Meta:
        model = File
        fields = ('id', 'name', 'content')


class AccordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex')
    public_key = serializers.CharField(source='doctor__public_key')

    class Meta:
        model = Accord
        fields = ('id','protected_symetric_key','public_key')
