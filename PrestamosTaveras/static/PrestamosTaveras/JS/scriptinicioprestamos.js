function calcular() {
    var cantidad_sol = parseFloat(document.getElementById('cantidad').value) || 0;
    var cuotas_sol = parseFloat(document.getElementById('cuotas').value) || 0;

    if (cuotas_sol !== 0) {
        var monto = cantidad_sol / cuotas_sol;
        monto = Math.round(cantidad_sol / cuotas_sol) + Math.round(monto * 0.30);

        document.getElementById('monto').value = monto;
    } else {
        document.getElementById('monto').value = "";
    }
}
document.addEventListener('input', calcular)

function soloNumeros(input) {
    input.value = input.value.replace(/[^0-9]/g, '');
}

function guionesTelefono(input) {
    input.value = input.value.replace(/\D/g, '');

    if (input.value.length > 3) {
        input.value = input.value.slice(0, 3) + '-' + input.value.slice(3);
    }

    if (input.value.length > 7) {
        input.value = input.value.slice(0, 7) + '-' + input.value.slice(7);
    }
}

function mostrarModal() {
    document.getElementById('modalDireccion').style.display = 'block';
    document.getElementById('modalOverlay').style.display = 'block';

    setTimeout(function() {
        document.getElementById('calle').focus();
    }, 0)

    const formulario = document.getElementById('modalFormulario');

    formulario.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            
            var direccionInput = document.getElementById('direccion');

            var calleValor = document.getElementById('calle').value;
            var casaValor = document.getElementById('casa').value;
            var sectorValor = document.getElementById('sector').value;
            var ciudadValor = document.getElementById('ciudad').value;

            direccionInput.value = calleValor + ' ' + casaValor + ', ' + sectorValor + ' ' + ciudadValor;

            cerrarModal()
        }
    });
}

function cerrarModal() {
    var modalDireccion = document.getElementById('modalDireccion');
    var direccionInput = document.getElementById('direccion');

    var calleValor = document.getElementById('calle').value;
    var casaValor = document.getElementById('casa').value;
    var sectorValor = document.getElementById('sector').value;
    var ciudadValor = document.getElementById('ciudad').value;

    direccionInput.value = calleValor + ' ' + casaValor + ', ' + sectorValor + ' ' + ciudadValor;

    modalDireccion.style.display = 'none';

document.getElementById('modalOverlay').style.display = 'none';
}

function mostrarError(inputId, mensaje) {
    var inputElement = document.getElementById(inputId);

    inputElement.value = mensaje;

    inputElement.style.border = '1px solid #dc3545'
    inputElement.style.color = '#dc3545'
    inputElement.style.fontWeight = 'bold'

    inputElement.addEventListener('focus', function() {
        inputElement.value = '';

        inputElement.style.border = ''
        inputElement.style.color = ''
        inputElement.style.fontWeight = ''
    }, {once: true});
}
 
function mostrarError(inputId, mensaje) {
    var inputElement = document.getElementById(inputId);

    inputElement.value = mensaje;
    inputElement.type = 'text';

    inputElement.style.border = '1px solid #dc3545';
    inputElement.style.color = '#dc3545';
    inputElement.style.fontSize = '12px';
    inputElement.style.fontWeight = 'bold';

    inputElement.addEventListener('focus', function() {
        inputElement.value = '';
        inputElement.type = 'password';

        inputElement.style.border = '';
        inputElement.style.color = '';
        inputElement.style.fontSize = '';
        inputElement.style.fontWeight = '';
    }, {once: true});
}

function mostrar_ocultar(contrasena, icono_mostrar) {
    var input_contrasena = document.getElementById("contrasena");
    var icono_mostrar = document.getElementById("icono_mostrar");

    input_contrasena.type = input_contrasena.type === "password" ? "text" : "password";

    icono_mostrar.className = input_contrasena.type === "password" ? "fa-solid fa-eye-slash" : "fa-solid fa-eye";
}

function mostrar_ocultar_(contrasena_, icono_mostrar_) {
    var input_contrasena = document.getElementById("contrasena_");
    var icono_mostrar = document.getElementById("icono_mostrar_");

    input_contrasena.type = input_contrasena.type === "password" ? "text" : "password";

    icono_mostrar.className = input_contrasena.type === "password" ? "fa-solid fa-eye-slash" : "fa-solid fa-eye";
}

function mostrar_ocultar__(contrasena__, icono_mostrar__) {
    var input_contrasena = document.getElementById("contrasena__");
    var icono_mostrar = document.getElementById("icono_mostrar__");

    input_contrasena.type = input_contrasena.type === "password" ? "text" : "password";

    icono_mostrar.className = input_contrasena.type === "password" ? "fa-solid fa-eye-slash" : "fa-solid fa-eye";
}