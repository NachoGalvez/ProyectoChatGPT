from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('guardar_ramos_y_actividades/', views.guardar_ramos_y_actividades, name='guardar_ramos_y_actividades'),
    path('ingresar_ramos/', views.ingresar_ramos, name='ingresar_ramos'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout')
]