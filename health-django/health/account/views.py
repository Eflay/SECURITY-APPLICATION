from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.contrib import messages
from . import forms
from folder.models import Folder
import logging

logger = logging.getLogger('account')

def login_page(request):
    if request.method == 'GET':
        form = forms.LoginForm()
        return render(request, 'account/login.html', context={'form': form})
    elif request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'].lower(),
                password=form.cleaned_data['password'],
            )
            if user is not None:
                if not user.enabled:
                    form = forms.LoginForm()
                    logger.warning(f"User {user.email} tried to login, but is account is disabled")
                    messages.info(request, "Your account is not already activated.")
                    return render(request, 'account/login.html', context={'form': form})

                login(request, user)
                logger.warning(f"User {user.email} logged in")
                return redirect('home')
            else:
                messages.info(request, "Bad credentials.")
                logger.warning(
                    f"ip: {get_client_ip(request)}, description:'Failed login' email:{form.cleaned_data['email']}")
                
        return render(request, 'account/login.html', context={'form': form})

    return HttpResponse(status=405)

def register_page(request):
    if request.user.is_anonymous :
        if request.method == 'GET':
            form = forms.RegisterForm()
            return render(request, 'account/register.html', context={'form': form})
        elif request.method == 'POST':
            form = forms.RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.email = form.cleaned_data['email'].lower()
                
                if form.cleaned_data['role'] == 'PATIENT':
                    user.enabled = True
                    user.save()
                    folder = Folder.objects.create(patient_id=user.id)
                    folder.save()

                user.save()
                logger.warning(f"Account {user.email} created")

                    
                if not user.enabled:
                    messages.add_message(
                        request, messages.INFO, "Your account will be activated by an administrator.")
                
                return redirect(settings.LOGIN_REDIRECT_URL)

            return render(request, 'account/register.html', context={'form': form})
    
    return HttpResponse(status=405)


def get_client_ip(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[-1].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')

    return ip_addr
