from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('guardar_ramos_y_actividades/', views.guardar_ramos_y_actividades, name='guardar_ramos_y_actividades'),
    path('ingresar_ramos/', views.ingresar_ramos, name='ingresar_ramos'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('mostrar_ramos/', views.mostrar_ramos, name='mostrar_ramos'),
    path('eliminar_ramo/<int:ramo_id>/', views.eliminar_ramo, name='eliminar_ramo'),
    path('eliminar_actividad/<int:actividad_id>/', views.eliminar_actividad, name='eliminar_actividad'),
    path('preferencias/', views.preferencias, name='preferencias'),
    path('eliminar_preferencia/<str:pref>/', views.eliminar_preferencia, name='eliminar_preferencia'),
    path('generar-calendario/', views.pagina_generar_calendario, name='pagina_generar_calendario')
]