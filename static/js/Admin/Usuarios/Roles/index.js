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
                "data": "id",
                "className": "text-center", // Centrar contenido de la columna
                "render": function(data, type, row) {
                    return `
                        <a href="/Blyss/admin/usuarios/roles/view/${data}/" class="btn btn-primary btn-sm" title="Gestionar Roles y Permisos">
                            <i class="fas fa-user-cog"></i>
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
