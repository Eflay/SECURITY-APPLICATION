from django.db import models
import uuid
from account.models import User

class Accord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, null=False, on_delete=models.CASCADE,
                                related_name='patient', limit_choices_to={'role': 'PATIENT'})
    doctor = models.ForeignKey(User, null=False, on_delete=models.CASCADE,
                               related_name='doctor',  limit_choices_to={'role': 'DOCTOR'})
    # Chiffer avec la clé public du médecin
    protected_symetric_key = models.TextField()
    doctor_ask_delete = models.BooleanField(default=False, null=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PendingAccord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, null=False, on_delete=models.CASCADE,
                                related_name='pendingPatient', limit_choices_to={'role': 'PATIENT'})
    doctor = models.ForeignKey(User, null=False, on_delete=models.CASCADE,
                               related_name='pendingDoctor',  limit_choices_to={'role': 'DOCTOR'})
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
