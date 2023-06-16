from django.urls import path
import change_password.views
from django.contrib.auth import views as auth_views

urlpatterns = [ 
    path('change-password', change_password.views.change_password, name='change_password')
]

