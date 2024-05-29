from django.contrib import admin
from .models import Cliente, Tarea, MensajeWhatsApp

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Tarea)
admin.site.register(MensajeWhatsApp)