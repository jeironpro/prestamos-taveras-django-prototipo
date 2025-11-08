import pyotp
import secrets
import os
import cv2
import pytesseract
import re
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import RegistroUsuario, Prestamos, PagosRealizados
from .forms import RegistroUsuarioForm, PagosRealizadosForm
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.db.models import Sum, Value, F, Q
from django.db.models.functions import Coalesce
from datetime import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str
from django.utils.encoding import force_bytes
from .tokens import generate_token
from django.conf import settings
from django.core.files.storage import default_storage

# Configuración de Tesseract OCR
# Asegúrate de haber instalado Tesseract y ajusta la ruta si es diferente en tu sistema.
# En Windows, la ubicación por defecto suele ser:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

otp_storage ={}

def generar_otp():
    totp = pyotp.TOTP(pyotp.random_base32())
    return totp.now()

def enviar_correo_otp(email, otp):
    mensaje = f"Tu código de verificación es: {otp}"
    send_mail(
        'Código de Verificación',
        mensaje,
        'jeironprogrammer@gmail.com',
        [email], 
        fail_silently=False,
    )

def solicitar_prestamo(id_usuario, email, cliente, cantidad, cuotas, monto_cuotas):
    cuerpo_correo = render_to_string('solicitud_prestamo.html', {
        'cliente': cliente,
        'cantidad': cantidad,
        'cuotas': cuotas,
        'monto_cuotas': monto_cuotas,
        'email': email,
        'id_usuario': id_usuario,
    })

    mensaje = EmailMessage('Solicitud de Préstamo', cuerpo_correo, email, ['jeironprogrammer@gmail.com'])
    mensaje.content_subtype = 'html'
    mensaje.send()

def enviar_aprobar_prestamo(email, cliente):
    cuerpo_correo = render_to_string('aprobar_prestamo.html', {
        'cliente': cliente,
        'email': email,
    })

    mensaje = EmailMessage('Aprobación de Préstamo', cuerpo_correo, 'jeironprogrammer@gmail.com', [email])
    mensaje.content_subtype = 'html'
    mensaje.send()

def enviar_denegar_prestamo(email, cliente):
    cuerpo_correo = render_to_string('denegar_prestamo.html', {
        'cliente': cliente,
        'email': email,
    })

    mensaje = EmailMessage('Préstamo Denegado', cuerpo_correo, 'jeironprogrammer@gmail.com', [email])
    mensaje.content_subtype = 'html'
    mensaje.send()

def index(request):
    if request.method == "POST":
        correo_electronico = request.POST['correo_electronico']
        contrasena = request.POST['contrasena']

        usuario = authenticate(request, username=correo_electronico, password=contrasena)

        request.session['correo_electronico'] = correo_electronico

        if usuario.is_superuser:
            login(request, usuario)
            return redirect('admin')
        if usuario is not None and not usuario.is_superuser and (usuario.is_active and usuario.is_staff):
            login(request, usuario)
            otp = generar_otp()
            otp_storage[correo_electronico] = otp
            enviar_correo_otp(correo_electronico, otp)
            return redirect('verificacionOTP')
        else:
            messages.error(request, "El correo electronico o la contrasena son incorrectos")
            return redirect('index')
    return render(request, 'PrestamosTaveras/index.html')

def registro_usuario(request):
    if request.method == "POST":
        usuario = RegistroUsuarioForm(request.POST)
        nombre_apellido = request.POST['nombre_apellido']
        cedula = request.POST['cedula']
        telefono = request.POST['telefono']
        direccion = request.POST['direccion']
        correo_electronico = request.POST['correo_electronico']
        contrasena = request.POST['contrasena']
        contrasena_ = request.POST['contrasena_']

        if User.objects.filter(email=correo_electronico).exists():
            messages.error(request, "El correo electronico esta registrado")
            return redirect('registrousuario')
        
        if ' ' not in nombre_apellido:
            messages.error(request, 'Por favor, introduce un espacio entre tu nombre y apellido')
            return redirect('registrousuario')
        
        if RegistroUsuario.objects.filter(cedula=cedula):
            messages.error(request, 'La cedula esta registrada')
            return redirect('registrousuario')
        
        if RegistroUsuario.objects.filter(correo_electronico=correo_electronico):
            messages.error(request, "El correo electronico esta registrado")
            return redirect('registrousuario')
        
        if contrasena != contrasena_:
            messages.error(request, "Las contrasena no coinciden")
            return redirect('registrousuario')
        
        if len(contrasena) and len(contrasena_) < 8:
            messages.error(request, 'La contrasena debe tener un minimo de 8 caracteres')
            return redirect('registrousuario')
        
        if contrasena == nombre_apellido:
            messages.error(request, 'La contrasena no puede ser igual al nombre y apellido')
            return redirect('registrousuario')
        
        if contrasena == cedula:
            messages.error(request, 'La contrasena no puede ser igual a la cedula')
            return redirect('registrousuario')
        
        if contrasena == telefono:
            messages.error(request, 'La contrasena no puede ser igual al telefono')
            return redirect('registrousuario')
        
        if contrasena == direccion:
            messages.error(request, 'La contrasena no puede ser igual a la direccion')
            return redirect('registrousuario')
        
        if contrasena == correo_electronico:
            messages.error(request, 'La contrasena no puede ser igual al correo electronico')
            return redirect('registrousuario')
        
        if contrasena == contrasena_:
        
            if usuario.is_valid():
                usuario.save()

            nombre_apellido = nombre_apellido.split()
            nombre = nombre_apellido[0]
            apellido = ' '.join(nombre_apellido[1:])

            usuario_auth = User.objects.create_user(nombre_apellido, correo_electronico, contrasena)
            usuario_auth.first_name = nombre
            usuario_auth.last_name = apellido
            usuario_auth.is_active = False
            usuario_auth.save()
            
            messages.success(request, "Tu cuenta se ha creado sastifactoriamente!!! Por favor, revise su correo electronico para poder activar su cuenta.")

            subject = "Bienvendo/a Prestamos Taveras"
            message = "Hola " + usuario_auth.first_name + "!!! \n" + "Gracias por registrarse en nuestra aplicacion.\nLe hemos enviado un correo electrónico de confirmación, por favor confirme su dirección de correo electrónico. \n\nPrestamos Taveras"        
            from_email = settings.EMAIL_HOST_USER
            to_list = [usuario_auth.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
            current_site = get_current_site(request)
            email_subject = "Confirma Tu Correo"
            message2 = render_to_string('email_confirmacion.html',{
                
                'name': usuario_auth.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(usuario_auth.pk)),
                'token': generate_token.make_token(usuario_auth)
            })
            email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [usuario_auth.email],
            )
            email.fail_silently = True
            email.content_subtype = 'html'
            email.send()
            return redirect('index')
    return render(request, 'PrestamosTaveras/registrarme.html')

def activador(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario_auth = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        usuario_auth = None

    if usuario_auth is not None and generate_token.check_token(usuario_auth,token):
        usuario_auth.is_active = True
        usuario_auth.is_staff = True
        usuario_auth.save()
        messages.success(request, "Tu cuenta ha sido activada!!!")
        return redirect('index')
    else:
        messages.success(request, "Su cuenta no esta activada. Asegurese de activarla antes de iniciar sesion.")
        return redirect('index')
    
def eliminarregistro(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario_auth = User.objects.get(pk=uid)
        usuario = RegistroUsuario.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        usuario_auth = None

    if (usuario_auth and usuario) is not None and generate_token.check_token(usuario_auth,token):
        usuario_auth.delete()
        usuario.delete()
        messages.success(request, "El registro ha sido eliminado!!!")
        return redirect('index')

def olvidastetucontrasena(request):
    if request.method == 'POST':
        correo_electronico = request.POST['correo_electronico']

        if RegistroUsuario.objects.filter(correo_electronico=correo_electronico):
            user = User.objects.get(email=correo_electronico)
            usuario = RegistroUsuario.objects.get(correo_electronico=correo_electronico)
        else:
            messages.error(request, 'El correo electronico no esta registrado')
            return redirect('olvidastetucontrasena')
        
        nombre_apellido = usuario.nombre_apellido

        token = secrets.token_urlsafe(16)
        usuario.reset_token = token
        user.reset_token = token
        usuario.save()
        user.save()
        
        enlace_verificacion = f'http://127.0.0.1:8000/recuperartucontrasena/{token}'
        send_mail(
            'Solicitud Restablecer Contrasena',
            f'Estimado {nombre_apellido}, realizaste una solicitud para restablecer tu contrasena. Haz click en este enlace para restablecer tu contrasena: {enlace_verificacion}',
            'jeironprogrammer@gmail.com',
            [correo_electronico]
        )
        messages.success(request, 'Correo de restablecimiento de contrasena: Enviado')
        return redirect('/')
        
    return render(request, 'PrestamosTaveras/olvidastetucontrasena.html')  

def recuperartucontrasena(request, token):
    try:
        usuario = RegistroUsuario.objects.get(reset_token=token)
        user = User.objects.get(reset_token=token)
    except usuario.DoesNotExist:
        messages.error(request, 'Enlace invalido')
        return redirect('/')
    
    if request.method == 'POST':
        contrasena = request.POST['contrasena']
        contrasena_ = request.POST['contrasena_']

        if contrasena != contrasena_:
            return redirect('recuperartucontrasena')
        if len(contrasena) and len(contrasena_) < 8:
            return redirect('recuperartucontrasena')
        else:
            usuario.contrasena = contrasena
            user.set_password(contrasena)
            usuario.save()
            user.save()

            usuario.reset_token = None
            usuario.save()

            messages.success(request, 'Contrasena restablecida')
            return redirect('/')

    return render(request, 'PrestamosTaveras/recuperarcontrasena.html')

def verificacionOTP(request):
    if request.method == 'POST':
        correo_electronico = request.session.get('correo_electronico', '')
        entered_otp = request.POST['otp']

        stored_otp = otp_storage.get(correo_electronico, '')

        if stored_otp and entered_otp == stored_otp:
            return redirect('inicioprestamos')
        else:
            messages.error(request, 'Codigo invalido')
            return redirect('/')
    return render(request, 'PrestamosTaveras/verificacionOTP.html')

def manualdeuso(request):
    pdf = open('', 'rb')

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="manualdeuso_alphainventory.pdf"'
    
    return response

@login_required(login_url='index')
def inicioprestamos(request):
    usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    prestamo = Prestamos.objects.filter(usuario=request.user.id)
    cuotaspagadas = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('cuotas_pagadas'))
    cuotas_pagadas = cuotaspagadas['cuotas_pagadas__sum'] or 0
    totalpagar = Prestamos.objects.filter(usuario=request.user.id).values_list('total_pagar', flat=True).first()
    total_pagar = totalpagar or 0
    montopagado = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('monto_pagado'))
    monto_pagado = montopagado['monto_pagado__sum'] or 0
    restante_pagar = total_pagar - monto_pagado

    context = {
        'usuario':usuario,
        'prestamo':prestamo,
        'cuotas_pagadas':cuotas_pagadas,
        'restante_pagar':restante_pagar
    }
    return render(request, 'PrestamosTaveras/inicioprestamos.html', context)

@login_required(login_url='index')
def solicitarprestamo(request):
    usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    prestamo = Prestamos.objects.filter(usuario=request.user.id)
    cuotaspagadas = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('cuotas_pagadas'))
    cuotas_pagadas = cuotaspagadas['cuotas_pagadas__sum'] or 0
    totalpagar = Prestamos.objects.filter(usuario=request.user.id).values_list('total_pagar', flat=True).first()
    total_pagar = totalpagar or 0
    montopagado = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('monto_pagado'))
    monto_pagado = montopagado['monto_pagado__sum'] or 0
    restante_pagar = total_pagar - monto_pagado
    verificar_id_prestamo =  Prestamos.objects.filter(usuario=request.user.id).values_list('id_prestamo', flat=True)
    verificar_id_prestamo = verificar_id_prestamo or 0

    if request.method == 'POST':
        cantidad = request.POST['cantidad']
        cuotas = request.POST['cuotas']
        monto_cuotas = request.POST['monto']
        correo_electronico = request.POST['correo_electronico']
        direccion = request.POST['direccion']
        telefono = request.POST['telefono']

        idprestamo = Prestamos.objects.filter(usuario=request.user.id).values_list('id_prestamo', flat=True)
        id_prestamo = idprestamo or 0
        verificar_correo = RegistroUsuario.objects.filter(correo_electronico=correo_electronico)
        verificar_direccion = RegistroUsuario.objects.filter(direccion=direccion, id_usuario=request.user.id)
        verificar_telefono = RegistroUsuario.objects.filter(telefono=telefono, id_usuario=request.user.id)
        nombre_apellido = RegistroUsuario.objects.filter(id_usuario=request.user.id).values_list('nombre_apellido', flat=True).first()

        id_usuario = request.user.id

        if id_prestamo == 0 and int(cantidad) > 10000:
            messages.error(request, 'Este no es el monto inicial')
            return redirect('solicitarprestamo')
        if not verificar_correo:
            messages.error(request, 'Este no es su correo electronico')
            return redirect('solicitarprestamo')
        if not verificar_direccion:
            messages.error(request, 'Esta no es su direccion')
            return redirect('solicitarprestamo')
        if not verificar_telefono:
            messages.error(request, 'Este no es su numero de telefono')
            return redirect('solicitarprestamo')
        else:
            solicitar_prestamo(id_usuario, correo_electronico, nombre_apellido, cantidad, cuotas, monto_cuotas)
            messages.success(request, 'Solicitud enviada')
            return redirect('inicioprestamos')

    context = {
        'usuario':usuario,
        'prestamo':prestamo,
        'cuotas_pagadas':cuotas_pagadas,
        'restante_pagar':restante_pagar,
        'verificar_id_prestamo':verificar_id_prestamo
    }
    return render(request, 'PrestamosTaveras/solicitarunprestamo.html', context)

def aprobacionprestamo(request):
    if request.method == 'GET':
        id_usuario = request.GET.get('id_usuario')
        correo_electronico = request.GET.get('email')
        cliente = request.GET.get('cliente')
        cantidad = request.GET.get('cantidad')
        cuotas = request.GET.get('cuotas')
        monto_cuotas = request.GET.get('monto')
        total_pagar = (int(cuotas) * int(monto_cuotas))

        usuario = RegistroUsuario.objects.get(id_usuario=id_usuario)

        solicitud=Prestamos.objects.create(
            cantidad_prestada=cantidad,
            cuotas=cuotas,
            monto_cuotas=monto_cuotas,
            total_pagar=total_pagar,
            usuario=usuario
        )

        solicitud.save()

        enviar_aprobar_prestamo(correo_electronico, cliente)

        return redirect('admin')

def denegarprestamo(request):
    if request.method == 'GET':
        id_usuario = request.GET.get('id_usuario')
        correo_electronico = request.GET.get('email')
        cliente = request.GET.get('cliente')

        usuario = RegistroUsuario.objects.get(id_usuario=id_usuario)

        prestamo = Prestamos.objects.filter(usuario=usuario)
        
        prestamo.delete()

        enviar_denegar_prestamo(correo_electronico, cliente)

        return redirect('admin')

@login_required(login_url='index')
def misdatos(request):
    usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    prestamo = Prestamos.objects.filter(usuario=request.user.id)
    cuotaspagadas = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('cuotas_pagadas'))
    cuotas_pagadas = cuotaspagadas['cuotas_pagadas__sum'] or 0
    totalpagar = Prestamos.objects.filter(usuario=request.user.id).values_list('total_pagar', flat=True).first()
    total_pagar = totalpagar or 0
    montopagado = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('monto_pagado'))
    monto_pagado = montopagado['monto_pagado__sum'] or 0
    restante_pagar = total_pagar - monto_pagado

    context = {
        'usuario':usuario,
        'prestamo':prestamo,
        'cuotas_pagadas':cuotas_pagadas,
        'restante_pagar':restante_pagar
    }
    return render(request, 'PrestamosTaveras/misdatos.html', context)

@login_required(login_url='index')
def pagos(request):
    usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    prestamo = Prestamos.objects.filter(usuario=request.user.id)
    cuotaspagadas = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('cuotas_pagadas'))
    cuotas_pagadas = cuotaspagadas['cuotas_pagadas__sum'] or 0
    totalpagar = Prestamos.objects.filter(usuario=request.user.id).values_list('total_pagar', flat=True).first()
    total_pagar = totalpagar or 0
    montopagado = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('monto_pagado'))
    monto_pagado = montopagado['monto_pagado__sum'] or 0
    restante_pagar = total_pagar - monto_pagado
    pagos = PagosRealizados.objects.filter(usuario=request.user.id)

    context = {
        'usuario':usuario,
        'prestamo':prestamo,
        'cuotas_pagadas':cuotas_pagadas,
        'restante_pagar':restante_pagar,
        'pagos':pagos
    }
    return render(request, 'PrestamosTaveras/pagos.html', context)

@login_required(login_url='index')
def configuraciones(request):
    usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    prestamo = Prestamos.objects.filter(usuario=request.user.id)
    cuotaspagadas = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('cuotas_pagadas'))
    cuotas_pagadas = cuotaspagadas['cuotas_pagadas__sum'] or 0
    totalpagar = Prestamos.objects.filter(usuario=request.user.id).values_list('total_pagar', flat=True).first()
    total_pagar = totalpagar or 0
    montopagado = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('monto_pagado'))
    monto_pagado = montopagado['monto_pagado__sum'] or 0
    restante_pagar = total_pagar - monto_pagado

    context = {
        'usuario':usuario,
        'prestamo':prestamo,
        'cuotas_pagadas':cuotas_pagadas,
        'restante_pagar':restante_pagar
    }
    return render(request, 'PrestamosTaveras/configuraciones.html', context)

def cerrar_sesion(request):
    logout(request)
    return redirect('/')

@login_required(login_url='index')
def cambiarcontrasena(request):
    usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    prestamo = Prestamos.objects.filter(usuario=request.user.id)
    cuotaspagadas = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('cuotas_pagadas'))
    cuotas_pagadas = cuotaspagadas['cuotas_pagadas__sum'] or 0
    totalpagar = Prestamos.objects.filter(usuario=request.user.id).values_list('total_pagar', flat=True).first()
    total_pagar = totalpagar or 0
    montopagado = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('monto_pagado'))
    monto_pagado = montopagado['monto_pagado__sum'] or 0
    restante_pagar = total_pagar - monto_pagado

    cambiarcontrasena = User.objects.get(id=request.user.id)
    cambiarcontrasena_ = RegistroUsuario.objects.get(id_usuario=request.user.id)

    if request.method == "POST":
        Acontrasena = request.POST['contrasena']
        Ncontrasena = request.POST['contrasena_']
        Ccontrasena = request.POST['contrasena__']


        if Ncontrasena != Ccontrasena:
            messages.error(request, "Las contrasenas no coinciden")
            return redirect('cambiarcontrasena')
        if RegistroUsuario.objects.filter(id_usuario=request.user.id, contrasena=Acontrasena):
            if Ncontrasena == Ccontrasena:
                cambiarcontrasena.set_password(Ncontrasena)
                cambiarcontrasena_.contrasena = Ncontrasena
                cambiarcontrasena.save()
                cambiarcontrasena_.save()
                messages.success(request, "Su contrasena se restablecio correctamente")
                return redirect('cerrar_sesion')
        else:
            messages.error(request, "La contrasena introducida no es tu antigua contrasena")
            return redirect('cambiarcontrasena')

    context = {
        'usuario':usuario,
        'prestamo':prestamo,
        'cuotas_pagadas':cuotas_pagadas,
        'restante_pagar':restante_pagar
    }
    return render(request, 'PrestamosTaveras/cambiarcontrasena.html', context)

@login_required(login_url='index')
def cambiarcorreoelectronico(request):
    usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    prestamo = Prestamos.objects.filter(usuario=request.user.id)
    cuotaspagadas = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('cuotas_pagadas'))
    cuotas_pagadas = cuotaspagadas['cuotas_pagadas__sum'] or 0
    totalpagar = Prestamos.objects.filter(usuario=request.user.id).values_list('total_pagar', flat=True).first()
    total_pagar = totalpagar or 0
    montopagado = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('monto_pagado'))
    monto_pagado = montopagado['monto_pagado__sum'] or 0
    restante_pagar = total_pagar - monto_pagado

    cambiarcorreoelectronico = User.objects.get(id=request.user.id)
    cambiarcorreoelectronico_ = RegistroUsuario.objects.get(id_usuario=request.user.id)

    if request.method == "POST":
        Ncorreo_electronico = request.POST['correo_electronico']
        Ccorreo_electronico = request.POST['correo_electronico_']

        if Ncorreo_electronico != Ccorreo_electronico:
            messages.error(request, "Los correos electronicos no coinciden")
            return redirect('cambiarcorreoelectronico')
        if RegistroUsuario.objects.filter(id_usuario=request.user.id):
            if Ncorreo_electronico == Ccorreo_electronico:
                cambiarcorreoelectronico.email = Ncorreo_electronico
                cambiarcorreoelectronico_.correo_electronico = Ncorreo_electronico
                cambiarcorreoelectronico.save()
                cambiarcorreoelectronico_.save()
                messages.success(request, "Su correo electronico se restablecio correctamente")
                return redirect('cerrar_sesion')
        else:
            return redirect('cambiarcorreoelectronico')

    context = {
        'usuario':usuario,
        'prestamo':prestamo,
        'cuotas_pagadas':cuotas_pagadas,
        'restante_pagar':restante_pagar
    }
    return render(request, 'PrestamosTaveras/cambiarcorreoelectronico.html', context)

@login_required(login_url='index')
def modificardireccion(request):
    usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    prestamo = Prestamos.objects.filter(usuario=request.user.id)
    cuotaspagadas = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('cuotas_pagadas'))
    cuotas_pagadas = cuotaspagadas['cuotas_pagadas__sum'] or 0
    totalpagar = Prestamos.objects.filter(usuario=request.user.id).values_list('total_pagar', flat=True).first()
    total_pagar = totalpagar or 0
    montopagado = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('monto_pagado'))
    monto_pagado = montopagado['monto_pagado__sum'] or 0
    restante_pagar = total_pagar - monto_pagado

    modificardireccion = RegistroUsuario.objects.get(id_usuario=request.user.id)

    if request.method == "POST":
        calle = request.POST['calle']
        casa = request.POST['casa']
        sector = request.POST['sector']
        ciudad = request.POST['ciudad']

        direccion = f"{calle} {casa}, {sector} {ciudad}"
        if RegistroUsuario.objects.filter(direccion=direccion).exists:
            messages.error(request, 'Esta es su direccion actual')
            return redirect('modificardireccion')
        if RegistroUsuario.objects.filter(id_usuario=request.user.id):
            if direccion:
                modificardireccion.direccion = direccion
                modificardireccion.save()
                messages.success(request, "Su direccion se modifico correctamente")
                return redirect('misdatos')
        else:
            return redirect('modificardireccion')

    context = {
        'usuario':usuario,
        'prestamo':prestamo,
        'cuotas_pagadas':cuotas_pagadas,
        'restante_pagar':restante_pagar
    }
    return render(request, 'PrestamosTaveras/modificardireccion.html', context)

@login_required(login_url='index')
def modificartelefono(request):
    usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    prestamo = Prestamos.objects.filter(usuario=request.user.id)
    cuotaspagadas = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('cuotas_pagadas'))
    cuotas_pagadas = cuotaspagadas['cuotas_pagadas__sum'] or 0
    totalpagar = Prestamos.objects.filter(usuario=request.user.id).values_list('total_pagar', flat=True).first()
    total_pagar = totalpagar or 0
    montopagado = PagosRealizados.objects.filter(usuario=request.user.id).aggregate(Sum('monto_pagado'))
    monto_pagado = montopagado['monto_pagado__sum'] or 0
    restante_pagar = total_pagar - monto_pagado

    modificartelefono = RegistroUsuario.objects.get(id_usuario=request.user.id)

    if request.method == "POST":
        telefono = request.POST['telefono']
        telefono_ = request.POST['telefono_']

        if telefono != telefono_:
            messages.error(request, "Los numeros de telefonos no coinciden")
            return redirect('modificartelefono')
        if RegistroUsuario.objects.filter(id_usuario=request.user.id):
            if telefono == telefono_:
                modificartelefono.telefono = telefono_
                modificartelefono.save()
                messages.success(request, "Su telefono se modifico correctamente")
                return redirect('misdatos')
        else:
            return redirect('modificardireccion')

    context = {
        'usuario':usuario,
        'prestamo':prestamo,
        'cuotas_pagadas':cuotas_pagadas,
        'restante_pagar':restante_pagar
    }
    return render(request, 'PrestamosTaveras/modificartelefono.html', context)

@login_required(login_url='index')
def eliminarcuenta(request):
    registro_usuario = RegistroUsuario.objects.filter(id_usuario=request.user.id)
    usuario = User.objects.filter(id=request.user.id)
    if request.method == 'POST':
        registro_usuario.delete()
        usuario.delete()
        return redirect('index')
    
def not_superuser(usuario):
    return not usuario.is_superuser

@login_required(login_url='index')
def administrador(request):
    prestamos_activos = Prestamos.objects.count()
    total_prestado = Prestamos.objects.aggregate(suma_cantidad_prestada=Coalesce(Sum('cantidad_prestada'), Value(0)))['suma_cantidad_prestada']
    ganancias = Prestamos.objects.aggregate(suma_ganancias=Coalesce(Sum(F('total_pagar') - F('cantidad_prestada')), Value(0)))['suma_ganancias']
    cobrados = PagosRealizados.objects.aggregate(suma_monto_pagado=Coalesce(Sum('monto_pagado'), Value(0)))['suma_monto_pagado']
    reditos = PagosRealizados.objects.aggregate(suma_redito=Coalesce(Sum('redito'), Value(0)))['suma_redito']

    total_prestado_ganancias = int(total_prestado) + int(ganancias)

    cobradas = 0
    ganancias_restantes = ganancias
    total_cobrados_cobradas = int(cobrados) + int(cobradas)

    if cobrados >= total_prestado:
        cobradas = cobrados - total_prestado
        cobrados = total_prestado
        ganancias_restantes = ganancias - cobradas
        total_cobrados_cobradas = cobrados + cobradas

    context = {
        'prestamos_activos':prestamos_activos,
        'total_prestado':total_prestado,
        'ganancias':ganancias,
        'cobrados':cobrados,
        'cobradas':cobradas,
        'ganancias_restantes':ganancias_restantes,
        'total_prestado_ganancias':total_prestado_ganancias,
        'total_cobrados_cobradas':total_cobrados_cobradas,
        'reditos':reditos,
    }
    return render(request, 'PrestamosTaveras/administrador.html', context)

@login_required(login_url='index')
def pagosadministrador(request):
    usuarios = RegistroUsuario.objects.values_list('nombre_apellido', flat=True)
    usuario = None

    if request.method == 'POST':
        pago_realizado = PagosRealizadosForm(request.POST)
        nombre_apellido = request.POST['nombre_apellido']
        cedula = request.POST['cedula']
        monto_pagado = request.POST['monto_pagado']
        monto_pagado = float(monto_pagado) if monto_pagado else 0
        cuotas_pagadas = request.POST['cuotas_pagadas']
        redito = request.POST['redito']
        fecha = request.POST['fecha']
        fecha_actual = datetime.now().date()
        usuario = RegistroUsuario.objects.filter(nombre_apellido=nombre_apellido).values_list('id_usuario', flat=True).first()

        if not RegistroUsuario.objects.filter(cedula=cedula) and cedula != '':
            messages.error(request, 'Esta cedula no esta registrado')
            return redirect('pagosadministrador')
        if not PagosRealizados.objects.filter(monto_pagado=monto_pagado, usuario=usuario) and monto_pagado == str:
            messages.error(request, 'Este no es el monto que debe pagar el usuario')
            return redirect('pagosadministrador')
        if cuotas_pagadas == 0 and redito == 0:
            messages.error(request, 'El cliente debe pagar una cuota o redito')
            return redirect('pagosadministrador')
        if fecha == fecha_actual:
            messages.error(request, 'Selecciona la fecha actual')
            return redirect('pagosadministrador')
        if pago_realizado.is_valid():
            pago_realizado.save()

            return redirect('/admin/')
        
    context = {
        'usuarios':usuarios,
        'usuario':usuario,
    }
    return render(request, 'PrestamosTaveras/pagos_administrador.html', context)

@login_required(login_url='index')
def clientes(request):
    clientes = RegistroUsuario.objects.all()

    context = {
        'clientes':clientes,
    }
    return render(request, 'PrestamosTaveras/clientes.html', context)

@login_required(login_url='index')
def buscador_cliente(request):
    if request.method == 'POST':
        nombre_apellido_cedula = request.POST['buscador_cliente']
        cliente = RegistroUsuario.objects.filter(Q(nombre_apellido__icontains=nombre_apellido_cedula) | Q(cedula=nombre_apellido_cedula))

        return render(request, 'PrestamosTaveras/clientes.html', {'buscador_cliente':cliente})
    else:
        return redirect('clientes')

@login_required(login_url='index')
def eliminarcliente(request):
    if request.method == 'POST':
        id_cliente = request.POST['id_cliente']
        cliente = RegistroUsuario.objects.filter(id_usuario=id_cliente)
        usuario = User.objects.filter(id=id_cliente)
        usuario.delete()
        cliente.delete()

        return redirect('clientes')

@login_required(login_url='index')
def cedulas(request):
    clientes = RegistroUsuario.objects.all()

    if request.method == 'POST':
        numero_cedula = request.POST['numero_cedula']
        img_cedula = request.FILES['cedula']

        imagen_cedula_temporal = 'cedula' + os.path.splitext(img_cedula.name)[1]

        with default_storage.open(imagen_cedula_temporal, 'wb') as destination:
            for chunk in img_cedula.chunks():
                destination.write(chunk)

        imagen_cedula = cv2.imread(imagen_cedula_temporal)

        texto = pytesseract.image_to_string(imagen_cedula)

        patron = re.compile(r'\b\d{3}-\d{7}-\d\b')

        numeros_coincidentes = [match.group() for match in re.finditer(patron, texto)]

        if numero_cedula == numeros_coincidentes[0]:
            messages.success(request, 'El numero de cedula coincide con el de la imagen')
            os.remove(imagen_cedula_temporal)
            pass
        if numero_cedula != numeros_coincidentes[0]:
            messages.error(request, 'El numero de cedula no coincide con el de la imagen')
            return redirect('cedulas')
        if numero_cedula and img_cedula:
            usuario = RegistroUsuario.objects.get(cedula=numero_cedula)

            tiempo = datetime.now()
            hora_actual = tiempo.strftime('%Y%H%M%S')

            if img_cedula.name != "":
                nuevoNombre = hora_actual + "_" + img_cedula.name

                carpeta_img = os.path.join(settings.BASE_DIR, 'PrestamosTaveras/static/PrestamosTaveras/img/')

                if not os.path.exists(carpeta_img):
                    os.makedirs(carpeta_img)

                with open('PrestamosTaveras/static/PrestamosTaveras/img/' + nuevoNombre, 'wb') as file:
                    for chunk in img_cedula.chunks():
                        file.write(chunk)

                if usuario:
                    usuario.imagen_cedula = nuevoNombre
                    usuario.save()

                    return redirect('cedulas')
                else:
                    messages.error(request, 'Usuario no encontrado')
                    return redirect('cedulas')
            else:
                messages.error(request, 'Nombre de imagen vacio')
                return redirect('cedulas')
        else:
            messages.error(request, 'Numero de cedula o imagen no proporcionados')
            return redirect('cedulas')
        
    context = {
        'clientes':clientes,
    }
    
    return render(request, 'PrestamosTaveras/cedulas.html', context)

@login_required(login_url='index')
def buscador_cedula(request):
    if request.method == 'POST':
        nombre_apellido_cedula = request.POST['buscador_cliente']
        cliente = RegistroUsuario.objects.filter(Q(nombre_apellido__icontains=nombre_apellido_cedula) | Q(cedula=nombre_apellido_cedula))

        return render(request, 'PrestamosTaveras/cedulas.html', {'buscador_cedula':cliente})
    else:
        return redirect('cedulas')
