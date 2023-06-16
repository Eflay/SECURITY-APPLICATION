from django.urls import path
import account.views
from django.contrib.auth.views import LogoutView


urlpatterns = [ 
    path('login/', account.views.login_page, name='login'),
    path('register/', account.views.register_page, name='register'), 
    path('logout/', LogoutView.as_view(), name='logout'),
]