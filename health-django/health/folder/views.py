import uuid
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from folder.models import File, PendingFile
from accord.models import Accord
from account.models import User, History
from django.core.exceptions import PermissionDenied
from folder.models import Folder
from folder.forms import FileCreateForm
from django.contrib import messages
import logging
from datetime import datetime

logger = logging.getLogger('folder')


def get_accord(user_request, user_2, message):
    accord = Accord.objects.filter(
            doctor_id=user_request, patient_id=user_2).first()
    if not accord:
        logger.warning(
            f"User id : {user_request.id} tried to {message}, targeted user id : {user_2}")
        raise PermissionDenied()
    
    return accord



@login_required(redirect_field_name=None)
def show_file(request, id):
    if request.method == 'GET':
        accord = None

        file = File.objects.select_related('folder').filter(id=id)[0]
        if request.user.role == "DOCTOR":   
            accord = get_accord(request.user, file.folder.patient.id, "view file " + str(id))

        if file.folder.patient.id == request.user.id or accord != None:
            return render(request, 'folder/file.html', context={'file': file, 'accord': accord})
        else:
            return HttpResponseForbidden()
        
    return HttpResponse(status=405)


@login_required(redirect_field_name=None)
def folder(request, pat_id):
    if request.method == 'GET':
        accord = None

        if request.user.role == "DOCTOR":
            accord = get_accord(request.user, pat_id, 'view folder')
        elif request.user == pat_id:
            return HttpResponseForbidden()

        folder = Folder.objects.select_related('patient').get(patient=pat_id)
        files = File.objects.filter(folder_id=folder.id)

        pending_file = PendingFile.objects.filter(patient=folder.patient)


        return render(request, 'folder/folder.html', context={"files": files, 'pendingfiles': pending_file, 'accord': accord, 'folder': folder})

    return HttpResponse(status=405)



@login_required(redirect_field_name=None)
def file_create(request, pat_id):
    if request.method == 'GET':
        form = FileCreateForm()

        accord = None
        if request.user.role == 'DOCTOR':
            accord = get_accord(request.user, pat_id, ' get view file create ')
            return render(request, 'folder/file-create.html', context={"form": form, 'accord': accord})
        
        elif request.user.role == 'PATIENT':
            return render(request, 'folder/file-create.html', context={"form": form})
    
    elif request.method == 'POST':
        if request.user.role == 'DOCTOR':
            
            get_accord(request.user, pat_id, ' tried to create a file ')
            form = FileCreateForm(request.POST)

            patient = User.objects.get(id=pat_id)
            pending_file = PendingFile.objects.create(
                name=form.data['name'],
                content=form.data['content'],
                doctor_sign=form.data['doctor_sign'],
                doctor=request.user,
                action='create', 
                file_clone=None,
                patient=patient)
            
            pending_file.save()
            logger.warning(f"User {request.user.email} request to create a file {pending_file.id} for patient {patient.email}")

            return redirect('folder', pat_id)
        
        elif request.user.role == 'PATIENT':
            form = FileCreateForm(request.POST)
            folder = Folder.objects.get(patient_id=request.user)
            file = File.objects.create(
                name=form.data['name'],
                content=form.data['content'],
                patient_sign=form.data['patient_sign'],
                folder_id=folder.id,
                patient=request.user)
            
            file.save()
            logger.warning(f"User {request.user.email} created a new file {file.id}")
            return redirect('folder', request.user.id)
        
    return HttpResponseForbidden()


@login_required(redirect_field_name=None)
def file_delete(request, id):
    if request.method == 'GET':
        file = File.objects.get(id=id)
        folder = Folder.objects.get(id=file.folder_id)

        accord = None
        if request.user.role == "DOCTOR":
            accord = get_accord(request.user, folder.patient_id, 'tried to delete file' + str(id))

        elif request.user.id != file.patient.id:
            return HttpResponseForbidden()
        
        form = FileCreateForm(instance=file)
        form.fields['name'].widget.attrs['disabled'] = True
        form.fields['content'].widget.attrs['readonly'] = True

        if PendingFile.objects.filter(file_clone=id).count() == 1:
            messages.info(request,
                          "This file is locked, it has been modified and the new version has not yet been approved.")
            return redirect('home')
        
        return render(request, 'folder/file-delete.html', context={'file': file, 'form': form, 'accord': accord})
    
    elif request.method == 'POST':
        file = File.objects.get(id=id)
        if request.user.role == 'DOCTOR':
            get_accord(request.user, file.patient, 'delete file, file id' + str(id))
            
            if PendingFile.objects.filter(file_clone=id).count() == 1:
                messages.info(request,
                          "This file is locked, it has been modified and the new version has not yet been approved.")
                return redirect('home')
            
            form = FileCreateForm(request.POST, instance=file)
            file_pending = PendingFile.objects.create(
                file_clone=file,
                name=file.name,
                content=form.data['content'],
                action="delete",
                doctor_sign=request.POST.get('doctor_sign'),
                doctor_id=request.user.id,
                patient_id=file.patient_id
                )
            
            file_pending.save()
            logger.warning(f"User {request.user.email} request to delete a file {file_pending.id} for patient {file.patient.email}")
            return redirect('home')
        elif request.user.role == 'PATIENT':
            if request.user.id == file.patient.id:
                file.delete()
                logger.warning(f"User {request.user.email} deleted a file {file.id}")
                return redirect('folder', request.user.id)
        
        return HttpResponseForbidden()


@login_required(redirect_field_name=None)
def file_modify(request, id):
    if request.method == 'GET':
        file = File.objects.filter(id=id).select_related('folder').first()
        form = FileCreateForm(instance=file)
        accord = None
        if request.user.role == "DOCTOR":
            accord = get_accord(request.user, file.folder.patient_id, 'modify file' + str(id))
        elif request.user.id != file.folder.patient.id:
            return HttpResponseForbidden()
        
        if PendingFile.objects.filter(file_clone=id).count() == 1 :
            messages.info(request,
                "This file is locked, it has been modified and the new version has not yet been approved.")
            return redirect('home')

        return render(request, 'folder/file-update.html', context={'form': form, 'accord': accord})

    elif request.method == 'POST':
        file = File.objects.filter(id=id).select_related('folder').first()
        form = FileCreateForm(request.POST, instance=file)

        if PendingFile.objects.filter(file_clone=id).count() == 1:
            messages.info(request,
                "This file is locked, it has been modified and the new version has not yet been approved.")
            return redirect('home')

        if request.user.role == 'DOCTOR':
            get_accord(request.user, file.folder.patient, 'modify file' + str(id))
            file_pending = PendingFile.objects.create(
                file_clone=file,
                name=file.name,
                content=form.data['content'],
                doctor_sign=form.data['doctor_sign'],
                doctor=request.user,
                patient=file.folder.patient)
            
            file_pending.save()
            logger.warning(f"User {request.user.email} request to modify a file {file_pending.id} for patient {file.folder.patient.email}")
            return redirect('home')
        elif request.user.role == 'PATIENT':
            # Edouard fix pour verif le form
            if request.user.id == file.folder.patient.id:
                folder = Folder.objects.get(id=file.folder.id)
                file.content = request.POST.get('content')
                file.patient_sign = request.POST.get('patient_sign')
                file.save()
                logger.warning(f"User {request.user.email} modified a file {file.id}")
                return redirect('folder', folder.patient_id)
            else:
                return HttpResponseForbidden()
            


@login_required(redirect_field_name=None)
def file_sign(request, id):
    if request.method == 'GET':

        file_pending = PendingFile.objects.select_related('doctor').filter(
            id=id, patient=request.user).first()
        
        date_time = datetime.now()
        
        try:
            old_pub_key = History.objects.filter(doctor=file_pending.doctor, created_at__range=(file_pending.created_at, date_time)).last()
        except:
            old_pub_key = None

        form = FileCreateForm(
            initial={'name': file_pending.name, 'content': file_pending.content})

        return render(request, 'folder/file-sign.html', context={'form': form, 'file_pending': file_pending, 'old_pub_key': old_pub_key})

    elif request.method == 'POST':

        pending_file = PendingFile.objects.filter(
            id=id, patient=request.user).select_related('file_clone').first()
        
        if pending_file:

            if request.POST.get('action') == 'giveup':
                pending_file.delete()
                logger.warning(f"User {request.user.email} gave up on signing a file {pending_file.id}")
                return redirect('folder', request.user.id)
    
            if pending_file.file_clone != None:
                file = File.objects.filter(id=pending_file.file_clone.id).first()
                if pending_file.action == 'delete':
                    logger.warning(f"User {request.user.email} approved file deletion of {file.id} by {pending_file.doctor.email}")
                    file.delete()
                    pending_file.delete()
                    return redirect('folder', request.user.id)
                
                elif pending_file.action == 'modify':
                    file.content = pending_file.content
                    file.doctor = pending_file.doctor
                    file.doctor_sign = pending_file.doctor_sign
                    file.patient_sign = request.POST.get(
                        "patient_sign")
                    file.save()
                    pending_file.delete()
                    logger.warning(f"User {request.user.email} approved file modification {file.id} by {pending_file.doctor.email}")
                    return redirect('folder', request.user.id)
            else:

                docteur = User.objects.get(id=pending_file.doctor_id)
                folder = Folder.objects.get(patient_id=pending_file.patient)
                file = File.objects.create(name=pending_file.name,
                                        content=pending_file.content,
                                        doctor_sign=pending_file.doctor_sign,
                                        patient=request.user,
                                        patient_sign=request.POST.get('patient_sign'),
                                        folder_id=folder.id,
                                        doctor=docteur)
                file.save()
                pending_file.delete()
                logger.warning(f"User {request.user.email} approved file creation {file.id} by {pending_file.doctor.email}")
                return redirect('folder', request.user.id)
        else:
            return HttpResponseForbidden()

