from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='turing_index'),
    path('about/', views.about, name='turing_about'),
    path('css/', views.stylesheet, name='stylesheet_css'),
]