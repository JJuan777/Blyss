$(document).ready(function() {
    $('#usuariosTable').DataTable({
        "ajax": {
            "url": "/Blyss/api/usuarios-staff/",
            "type": "GET",
            "dataSrc": "data"
        },
        "columns": [
            { "data": "nombre_completo" },
            { "data": "correo" },
            { "data": "telefono" },
            { 
                "data": "last_login",
                "className": "text-center",  // Centrar el texto
                "render": function(data, type, row) {
                    return data ? data : "Nunca"; // Si no ha iniciado sesión, mostrar "Nunca"
                }
            }
        ],
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.11.5/i18n/es-MX.json"
        }
    });
});
