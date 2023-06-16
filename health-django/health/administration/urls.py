from django.urls import path
import administration.views

urlpatterns = [
    path('administration/revoke/', administration.views.revoke_page, name='revoke_page'),
    path('administration/', administration.views.home_page_admin, name='home_page_admin'),
    path('administration/patient_delete', administration.views.delete_user, name='delete_user'),
    path('administration/ask-delete/<uuid:pat_id>', administration.views.confirm_delete_patient, name='patient-ask-delete'),
]
