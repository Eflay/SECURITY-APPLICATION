from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'
    
    DOCTOR = 'DOCTOR'
    PATIENT = 'PATIENT'

    ROLE_CHOICES = (
        (PATIENT , 'Patient'),
        (DOCTOR , 'Doctor'),
    )
    
    email = models.EmailField(unique=True, null=False)
    protected_symetric_key = models.TextField(null=False)
    public_key = models.TextField(null=False)
    protected_private_key = models.TextField(null=False)
    updated_at = models.DateTimeField(auto_now=True)
    username = models.CharField( max_length=150,unique=False,null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, verbose_name='Role')
    enabled = models.BooleanField(null=False, blank=False, default=False)

class History(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    public_key = models.TextField(null=False, editable=False)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_history', editable=False)
    created_at = models.DateTimeField(auto_now_add=True)