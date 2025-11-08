from django.contrib import admin
from .models import RegistroUsuario, Prestamos, PagosRealizados

# Registra tus modelos aqui.
admin.site.register(RegistroUsuario)
admin.site.register(Prestamos)
admin.site.register(PagosRealizados)