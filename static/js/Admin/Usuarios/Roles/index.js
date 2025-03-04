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
                "data": null, // Columna personalizada
                "render": function(data, type, row) {
                    return `
                        <a href="#" class="btn btn-primary btn-sm" title="Gestionar Roles y Permisos">
                            <i class="fas fa-user-cog"></i> Detalles
                        </a>
                    `;
                }
            }
        ],
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.11.5/i18n/es-MX.json"
        }
    });
});
