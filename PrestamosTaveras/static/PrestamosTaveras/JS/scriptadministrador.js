function NombreApellidoCedula(input) {
    let input_buscador = event.target.value;
    input_buscador = input.value.replace(/[^0-9a-zA-Z\s]/g, '');

    input.maxLength = (/\d/.test(input_buscador)) ? 13 : 100;

    let input_modificado = '';
    for (let i = 0; i < input_buscador.length; i++) {
        if (i === 3 && i !== input_buscador.length && ! isNaN(input_buscador[i])) {
            input_modificado += '-';
        }
        if (i === 10 && i !== input_buscador.length && ! isNaN(input_buscador[i])) {
            input_modificado += '-';
        }
        input_modificado += input_buscador[i];
    }
    input.value = input_modificado;
}

function agregarGuionesCedula(input) {
    input.value = input.value.replace(/[^0-9]/g, '');

    if (input.value.length > 3) {
        input.value = input.value.slice(0, 3) + '-' + input.value.slice(3);
    }

    if (input.value.length > 11) {
        input.value = input.value.slice(0, 11) + '-' + input.value.slice(11);
    }
}

function soloNumeros(input) {
    let valor = input.value;
    valor = valor.replace(/[^0-9]/g, '');

    if (valor.length >= 4) {
        valor = Number(valor).toLocaleString('es-DO');
        valor = valor.replace('.', ',');
    }
    input.value = valor;
}

function nuevaAccion(newAction) {
    document.getElementById('formulario_buscador_cliente').action = newAction;
    document.getElementById('formulario_buscador_cliente').submit();
}

function mostrarModal() {
    document.getElementById('modalCedula').style.display = 'block';
    document.getElementById('modalOverlay').style.display = 'block';
}

function cerrarModal() {
    var modalDireccion = document.getElementById('modalCedula');
    var direccionInput = document.getElementById('direccion');

    modalDireccion.style.display = 'none';

document.getElementById('modalOverlay').style.display = 'none';
}

function guardarSeleccion() { 
    let select = document.getElementById('nombre_apellido'); 
    let opcionSeleccionada = select.options[select.selectedIndex].value; 
    localStorage.setItem('opcionSeleccionada', opcionSeleccionada); 
    document.getElementById('formulario-completo').submit();
} 

function enviarFormulario()  { 
    guardarSeleccion(); 
    document.getElementById('formulario-completo').submit(); 
    localStorage.removeItem('opcionSeleccionada')
}; 

let opcionGuardada = localStorage.getItem('opcionSeleccionada'); 

if (opcionGuardada) { 
    document.getElementById('nombre_apellido').value = opcionGuardada; 
}