from django.urls import path
import folder.views



urlpatterns = [
    path('file/<uuid:id>', folder.views.show_file, name='show_file'),
    path('file/create/<uuid:pat_id>', folder.views.file_create, name="file-create"),
    path('file/modify/<uuid:id>', folder.views.file_modify, name="file-modify"),
    path('file/delete/<uuid:id>', folder.views.file_delete, name="file-delete"),
    path('file/sign/<uuid:id>', folder.views.file_sign, name="file-sign"),
    path('folder/<uuid:pat_id>', folder.views.folder, name='folder'),
]
