from django.urls import path
from .views import (
    MachineListView,
    MachineDetailView,
    ExampleCreateView,
    MachineCreateView,
    MachineUpdateView,
    MachineUpdateViewFile,
    MachineDeleteView,
    ExampleDeleteView,
)
from . import views

urlpatterns = [
    path('', views.index, name='turing_index'),
    path('about/', views.about, name='turing_about'),
    path('css/', views.stylesheet, name='stylesheet_css'),
    path('css2/', views.stylesheet, name='stylesheet_sim_css'),
    # path('machines/', MachineListView.as_view(), name='machines'),
    path('machines/', views.machine_list, name='machines'),
    path('machine/<int:pk>/', MachineDetailView.as_view(), name='machine-detail'),
    # path('simulation/<int:exampleId>/', views.simulation, name='simulation-view'),
    path('example/<int:pk>/simulation/', views.simulation, name='simulation-view'),
    path('example/<int:machineId>/new/', ExampleCreateView.as_view(), name='example-create'),
    path('machine/new/', MachineCreateView.as_view(), name='machine-create'),
    path('machine/<int:pk>/update', MachineUpdateView.as_view(), name='machine-update'),
    path('machine/<int:object_id>/download_instr/', views.download_instruction, name='download-instr'),
    path('machine/<int:object_id>/upload_instr/', views.upload_instruction, name='upload-instr'),
    path('machine/<int:pk>/update_file', MachineUpdateViewFile.as_view(), name='machine_instr-update'),
    path('machine/<int:pk>/delete', MachineDeleteView.as_view(), name='machine-delete'),
    path('example/<int:pk>/delete', ExampleDeleteView.as_view(), name='example-delete'),
]