
from django.contrib import admin
from django.urls import path
from pageApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.loginlubricentro, name='login'),
    path('clientes/', views.clientes, name='clientes'),
    path('guardar_cliente/', views.guardar_cliente, name='guardar_cliente'),
    path('editar_cliente/', views.editar_cliente, name='editar_cliente'),
    path('guardar_tarea/', views.guardar_tarea, name='guardar_tarea'),
    path('detalles_cliente/', views.detalles_cliente, name='detalles_cliente'),
    path('tareas_cliente/', views.tareas_cliente, name='tareas_cliente'),
    path('planilla_correctiva/', views.planilla_correctiva,
         name='planilla_correctiva'),
    path('planilla_preventiva/', views.planilla_preventiva,
         name='planilla_preventiva'),
    path('planilla/', views.planilla_personal, name='planilla'),
    path('eliminar_item_correctiva/', views.eliminar_item_correctiva,
         name='eliminar_item_correctiva'),
    path('eliminar_item_preventiva/', views.eliminar_item_preventiva,
         name='eliminar_item_preventiva'),
    path('eliminar_tarea_cliente/', views.eliminar_tarea_cliente,
         name='eliminar_tarea_cliente'),
     path('eliminar_cliente/', views.eliminar_cliente,
         name='eliminar_cliente'),
    path('obtener_nombres_mecanicos/', views.obtener_nombres_mecanicos,
         name='obtener_nombres_mecanicos'),
     path('buscar_cliente/', views.buscar_cliente, name='buscar_cliente'),
     path('get_username/', views.get_username, name='get_username'),
     path('guardar_estado_toggle/', views.guardar_estado_toggle, name='guardar_estado_toggle'),
     path('obtener_estado_toggle/<int:cliente_id>/', views.obtener_estado_toggle, name='obtener_estado_toggle'),
     path('enviar_mensajes_pendientes/', views.enviar_mensajes_pendientes, name='enviar_mensajes_pendientes'),
     path('comprobar_mensajes_pendientes/', views.comprobar_mensajes_pendientes, name='comprobar_mensajes_pendientes'),
     path('logout/', views.signout, name='logout'),

]
