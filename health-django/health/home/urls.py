from django.urls import path
import home.views
from django.contrib.auth.views import LogoutView

urlpatterns = [ 
    path('home/', home.views.home_page, name='home'),
    path('', home.views.home_page, name='home'),
]
