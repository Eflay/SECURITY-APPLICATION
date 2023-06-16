from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from account.models import User, History
from folder.models import Folder, File, PendingFile
from accord.models import Accord
from . import forms
from django.contrib import messages
from django.contrib.auth import authenticate
import json, logging

logger = logging.getLogger('change_password')

@login_required(redirect_field_name=None)
def change_password(request):
    user = request.user

    if request.method == "GET":
        form = forms.ChangePassword(user)
        if user.role == "PATIENT":
            if PendingFile.objects.filter(patient=user.id):
                messages.error(request, "You have files awaiting approval! Please approve them or not before changing your password.")
                return redirect('home')
            
            id_folder = Folder.objects.filter(patient=request.user.id)[0]

            files_query = File.objects.filter(folder=id_folder).values('id','name', 'content')
            files = forms.FileSerializer(list(files_query), many=True).data
            files = json.dumps(files)

            pending_files_query = PendingFile.objects.filter(file_clone__folder=id_folder).values('id','name', 'content')
            pending_files = forms.FileSerializer(list(pending_files_query), many=True).data
            pending_files = json.dumps(pending_files)
            
            accords_query = Accord.objects.filter(patient=user.id).select_related('doctor').values('id','protected_symetric_key', 'doctor__public_key')
            accords = forms.AccordSerializer(list(accords_query), many=True).data
            accords = json.dumps(accords)
        
            return render(request, 'change_password/change-password.html', context={'form': form, 'Files' : files,'PendingFiles':pending_files, 'Accords' : accords})
        
        if user.role == "DOCTOR":
            accords_query = Accord.objects.filter(doctor=user.id).select_related('doctor').values('id','protected_symetric_key', 'doctor__public_key')
            accords = forms.AccordSerializer(list(accords_query), many=True).data
            accords = json.dumps(accords)

            return render(request, 'change_password/change-password.html', context={'form': form, 'Accords' : accords})
        return render(request, 'change_password/change-password.html',context={'form': form})
    
    elif request.method == 'POST':
        form = forms.ChangePassword(request.POST)
        email = request.POST["email"].lower()
   
        old_password = request.POST["old_password"]
        
        user = authenticate(
            email=email,
            password=old_password,
        )
        
        if user is not None:
            new_password1 = request.POST['new_password1']
            new_password2 = request.POST['new_password2']
        
            if new_password1 == new_password2:
                if user.role == 'DOCTOR':
                    old_doctor = History.objects.create(public_key=user.public_key, doctor=user)
                    old_doctor.save()
                
                user = User.objects.get(id=request.user.id)
                
                user.set_password(new_password1)
                user.protected_symetric_key = request.POST['Protected_symetric_key']
                user.protected_private_key = request.POST['protected_private_key']
                user.public_key = request.POST['public_key']
                if user.role == 'PATIENT' : 
                    files = request.POST["files"]
                    files = json.loads(files)
                    for file_update in files:
                        print(file_update)
                        file = File.objects.get(id=file_update['id'], patient=user)
                        file.name = file_update['name']
                        file.content = file_update['content']
                        file.save()

                    pending_files = request.POST["pendingFile"]
                    pending_files = json.loads(pending_files)
                    for file_update in pending_files:
                        print(file_update)
                        file = PendingFile.objects.get(id=file_update['id'], patient=user)
                        file.name = file_update['name']
                        file.content = file_update['content']
                        file.save()

                if user.role == 'PATIENT' or user.role == 'DOCTOR' : 
                    accords = request.POST["accords"]
                    accords = json.loads(accords)
                    for accord_update in accords:
                        if user.role == 'PATIENT':
                            accord = Accord.objects.get(id=accord_update['id'], patient=user)
                        elif user.role == 'DOCTOR':
                            accord = Accord.objects.get(id=accord_update['id'], doctor=user)
                        accord.protected_symetric_key = accord_update['protected_symetric_key']
                        accord.save()

                user.save()
                logger.warning(f"User {request.user.email} changed his password")

        return redirect('home')

