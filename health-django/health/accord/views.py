from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import User
from accord.models import Accord, PendingAccord
from accord.forms import DoctorAddPatientForm, AccordCreateForm
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect

import logging

logger = logging.getLogger('accord')

@login_required(redirect_field_name=None)
def create_accord(request):
    if request.method == 'GET':
        if request.user.role == 'PATIENT':
            doctors = User.objects.filter(role="DOCTOR", enabled=True)
            pending_ask = PendingAccord.objects.select_related('doctor').filter(patient=request.user.id)

            return render(request, 'accord/accord-create.html', context={'doctors': doctors, 'pending_ask': pending_ask})
        else:
            return HttpResponseForbidden()

    return HttpResponse(status=405)


@login_required(redirect_field_name=None)
def delete_request_accord(request, doctor_id):
    if request.method == 'POST':
        if request.user.role == 'PATIENT':
            PendingAccord.objects.filter(
                patient=request.user.id, doctor=doctor_id).delete()
            logger.warning(
                f"User {request.user.email} delete request from doctor id : {doctor_id}")
            return redirect('accord')

    return HttpResponse(status=405)


@login_required(redirect_field_name=None)
def confirm_accord(request, doctor_id):

    doctor = User.objects.get(id=doctor_id, role='DOCTOR', enabled=True)

    if request.user.role == "PATIENT":    
        if request.method == 'GET':
            form = AccordCreateForm()
            return render(request, 'accord/accord-update.html', context={"doctor": doctor, 'form': form})
        elif request.method == 'POST':
            if 0 == Accord.objects.filter(doctor_id=doctor, patient_id=request.user.id).count():
                accord = Accord.objects.create(doctor=doctor, patient=request.user,
                    protected_symetric_key=request.POST.get('protected_symetric_key'))
                accord.save()

                # Delete pending access request if it exist
                PendingAccord.objects.filter(patient=request.user.id, doctor=doctor).delete()
                logger.warning(f"User {request.user.email} add doctor to his folder {doctor_id}")
                return redirect('home')
            else:
                messages.error(request, "Vous avez déja fourni l'accord au docteur " + doctor.last_name + " " + doctor.first_name)
                return redirect('home')


    return HttpResponseForbidden()


@login_required(redirect_field_name=None)
def delete_accord(request, doctor_id):
    if request.method == 'POST':
        if request.user.role == 'PATIENT':
            result = Accord.objects.filter(
                patient=request.user.id, doctor=doctor_id).delete()
            # Result[0] = number of deleted row
            if result[0] == 1:
                logger.warning(
                    f"User {request.user.email} revoked doctor {doctor_id}")
            else:
                logger.critical(
                    f"User {request.user.email} tried to delete a non-existent doctor {doctor_id}")
            
            return redirect('accord')
    else:
        return HttpResponseForbidden()
    return HttpResponse(status=405)


@login_required(redirect_field_name=None)
def request_access(request):
    if request.user.role == 'DOCTOR':
        if request.method == 'GET':
            form = DoctorAddPatientForm()
            return render(request, 'accord/accord-doctor.html', {"form": form})
        elif request.method == 'POST':
            form = DoctorAddPatientForm(request.POST)
            if form.is_valid():
                user = User.objects.filter(email=form.cleaned_data['email'].lower()).first()
                print(PendingAccord.objects.filter(
                    doctor=request.user, patient=user).count())
                if user:
                    if(PendingAccord.objects.filter(doctor=request.user, patient=user).count() == 0 and
                        Accord.objects.filter(doctor=request.user, patient=user).count() == 0):

                        PendingAccord.objects.create(doctor=request.user, patient=user)
                        logger.warning(
                            f"User {request.user.email} asked access to {form.cleaned_data['email']} folder")
                else:
                    logger.warning(
                        f"User {request.user.email} tried to add a non-existent patient {form.cleaned_data['email']}")
            
            messages.info(
                request, "If the account exists, the user will receive your request.")
            form = DoctorAddPatientForm()
            return render(request, 'accord/accord-doctor.html', {"form": form})
    else:
        return HttpResponseForbidden()
    return HttpResponse(status=405)


@login_required(redirect_field_name=None)
def listing_accord_user(request):
    if request.method == 'GET':
        if request.user.role == "PATIENT":
            accords = Accord.objects.filter(patient=request.user)
            return render(request, 'accord/patient.html', context={"doctors": accords})
        elif request.user.role == "DOCTOR":
            accords = Accord.objects.filter(doctor=request.user)
            return render(request, 'accord/patient.html', context={"patients": accords})
        else:
            return HttpResponseForbidden()

    return HttpResponse(status=405)


@login_required(redirect_field_name=None)
def delete_accord_request(request, pat_id):
    if request.method == 'POST' and request.user.role == "DOCTOR":
        accord = Accord.objects.filter(doctor=request.user,
                                       patient=pat_id, doctor_ask_delete=False).update(doctor_ask_delete=True)

        if accord:
            messages.error(request, "The deletion request has been registered ")
            logger.warning(
                f"User {request.user.email} asked to delete accord with patient {pat_id}")
            return redirect('home')
        else:
            messages.error(
                request, "The deletion request is already in progress")
            return redirect('home')
    else:
        return HttpResponseForbidden()


