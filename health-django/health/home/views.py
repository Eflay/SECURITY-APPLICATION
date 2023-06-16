from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from account.models import User
import logging

logger = logging.getLogger('home')


@login_required(redirect_field_name=None)
def home_page(request):
    if request.method == 'GET':
        if request.user.is_staff:
            return redirect('home_page_admin')
        if request.user.role == "PATIENT":
            return render(request, 'home_page_patient.html')
        elif request.user.role == "DOCTOR":
            return render(request, 'home_page_doctor.html')
            
    return HttpResponse(status=405)
