from django import forms
from .models import RegistroUsuario, Prestamos, PagosRealizados

class RegistroUsuarioForm(forms.ModelForm):
    class Meta:
        model = RegistroUsuario
        fields = [
            'nombre_apellido',
            'cedula',
            'telefono',
            'direccion',
            'correo_electronico',
            'contrasena'
        ]

class PrestamosForm(forms.ModelForm):
    class Meta:
        model = Prestamos
        fields = [
            'cantidad_prestada',
            'cuotas',
            'monto_cuotas',
            'total_pagar',
            'usuario'
        ]

class PagosRealizadosForm(forms.ModelForm):
    class Meta:
        model = PagosRealizados
        fields = [
            'nombre_apellido',
            'cedula',
            'monto_pagado',
            'cuotas_pagadas',
            'redito',
            'fecha',
            'usuario'
        ]