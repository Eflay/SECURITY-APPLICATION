from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from accord.models import User
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger('administration')

@login_required(redirect_field_name=None)
def revoke_page(request):
    if request.user.is_staff:
        if request.method == 'GET':
            doctors = User.objects.filter(role="DOCTOR", enabled=True)
            return render(request, 'admin/revoke_page.html', context={'doctors': doctors})
        
        elif request.method == 'POST':
            enabled = request.POST
            for doctor_mail in enabled.getlist("doctor"):
                doct = User.objects.get(email=doctor_mail, role="DOCTOR")
                doct.enabled = False
                doct.save()
                logger.warning(
                    f"User {request.user.email} revoke access to doctor {doctor_mail}")
          
            doctors = User.objects.filter(role="DOCTOR", enabled=True)
            return render(request, 'admin/revoke_page.html', context={'doctors': doctors})
    else:
        return HttpResponseForbidden()
    
    return HttpResponse(status=405)


@login_required
def home_page_admin(request):
    if request.user.is_staff:
        if request.method == 'GET':
            doctors = User.objects.filter(role="DOCTOR", enabled=False)
            return render(request, 'admin/home_page.html', context={'doctors': doctors})

        elif request.method == 'POST':
            enabled = request.POST
            for doctor_mail in enabled.getlist("doctor"):
                doct = User.objects.get(email=doctor_mail, role="DOCTOR")
                doct.enabled = True
                doct.save()
                logger.warning(
                    f"User {request.user.email} add access to doctor {doctor_mail}")
            
            doctors = User.objects.filter(role="DOCTOR", enabled=False)
            return render(request, 'admin/home_page.html', context={'doctors': doctors})
        else:
            return HttpResponse(status=405)
    else:
        return HttpResponseForbidden()

@login_required(redirect_field_name=None)
def delete_user(request):
    if request.method == 'GET':
        if request.user.is_staff:
            patients = User.objects.filter(role="PATIENT")
            
            return render(request, 'admin/delete_user.html', context={'patients': patients})
        else:
            return HttpResponseForbidden()

    return HttpResponse(status=405)


@login_required(redirect_field_name=None)
def confirm_delete_patient(request, pat_id):
    if request.user.is_staff:    
        if request.method == 'GET':
            patient = User.objects.get(id=pat_id, role='PATIENT')
            return render(request, 'admin/confirm_delete_patient.html', context={'patient': patient})
        elif request.method == 'POST':
            patient = User.objects.get(id=pat_id, role='PATIENT')
            if patient:
                patient.delete()
                logger.warning(f"User {request.user.email} delete user {pat_id}")
            return redirect("home")

    return HttpResponseForbidden()