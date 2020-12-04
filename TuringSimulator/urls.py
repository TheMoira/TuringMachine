from django.urls import path
from .views import MachineListView, MachineDetailView
from . import views

urlpatterns = [
    path('', views.index, name='turing_index'),
    path('about/', views.about, name='turing_about'),
    path('css/', views.stylesheet, name='stylesheet_css'),
    path('machines/', MachineListView.as_view(), name='machines'),
    path('machine/<int:pk>/', MachineDetailView.as_view(), name='machines'),
]