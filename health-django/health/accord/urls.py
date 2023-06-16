from django.urls import path
import accord.views

urlpatterns = [
    path('accord/', accord.views.create_accord, name='accord'),
    path('accord/delete_request/<uuid:doctor_id>',
         accord.views.delete_request_accord, name='accord-request-delete'),
    path('accord/delete/<uuid:doctor_id>',
         accord.views.delete_accord, name='accord-delete'),
    path('accord/update/<uuid:doctor_id>',
         accord.views.confirm_accord, name='accord-update'),
    path('request-access/', accord.views.request_access,
         name='ask-accord'),
    path('patient/', accord.views.listing_accord_user, name='patient'),
    path('accord/ask-delete/<uuid:pat_id>',
         accord.views.delete_accord_request, name='accord-ask-delete'),
]

