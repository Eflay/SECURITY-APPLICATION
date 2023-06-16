from django.db import models
from account.models import User
import uuid


class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(
        User, null=False, on_delete=models.CASCADE, related_name='patient_folder')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.fields.CharField(max_length=200)
    content = models.fields.TextField(max_length=5000)
    folder = models.ForeignKey(Folder, null=False, on_delete=models.CASCADE)
    patient_sign = models.TextField(null=True)
    doctor_sign = models.TextField(null=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_file_id')
    doctor = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='doctor_file_id')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PendingFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.fields.CharField(max_length=200)
    content = models.fields.TextField(max_length=5000)
    file_clone = models.OneToOneField(
        File, null=True, on_delete=models.CASCADE)
    action = models.TextField(null=False, blank=False, default="modify")
    doctor_sign = models.TextField(null=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_pending_id')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_pending_id')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
