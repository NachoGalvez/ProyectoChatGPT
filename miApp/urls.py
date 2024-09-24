from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('guardar_ramos_y_actividades/', views.guardar_ramos_y_actividades, name='guardar_ramos_y_actividades'),
]