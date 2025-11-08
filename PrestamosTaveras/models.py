from django.db import models
from django.contrib.auth.models import User

User.add_to_class('reset_token', models.CharField(max_length=255, null=True, blank=True))

class RegistroUsuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre_apellido = models.CharField(max_length=75)
    cedula = models.CharField(max_length=13)
    telefono = models.CharField(max_length=12)
    direccion = models.CharField(max_length=100)
    correo_electronico = models.EmailField(max_length=80)
    contrasena = models.CharField(max_length=80)
    imagen_cedula = models.CharField(max_length=255, null=True, blank=True)
    reset_token = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombre_apellido
    
class Prestamos(models.Model):
    id_prestamo = models.AutoField(primary_key=True)
    cantidad_prestada = models.IntegerField()
    cuotas = models.IntegerField()
    monto_cuotas = models.IntegerField()
    total_pagar = models.IntegerField()
    # aprobado = models.BooleanField(default=False)
    usuario = models.ForeignKey(RegistroUsuario, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.cantidad_prestada)
    
class PagosRealizados(models.Model):
    id_pago = models.AutoField(primary_key=True)
    nombre_apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=13)
    monto_pagado = models.IntegerField()
    cuotas_pagadas = models.IntegerField()
    redito = models.IntegerField()
    fecha = models.DateField(max_length=10)
    usuario = models.ForeignKey(RegistroUsuario, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.monto_pagado)