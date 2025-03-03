document.addEventListener("DOMContentLoaded", function () {
    cargarUsuarios(1); // Carga la primera página

    function cargarUsuarios(page) {
        fetch(`/Blyss/usuarios/ajax/?page=${page}`)
            .then(response => response.json())
            .then(data => {
                let tabla = document.getElementById("tabla-usuarios");
                tabla.innerHTML = "";

                data.usuarios.forEach(usuario => {
                    let estadoBtn = usuario.is_active
                        ? `<button class="btn btn-danger btn-sm btn-toggle" data-id="${usuario.id}" data-state="bloquear">
                            <i class="fas fa-lock"></i> Bloquear
                           </button>`
                        : `<button class="btn btn-success btn-sm btn-toggle" data-id="${usuario.id}" data-state="desbloquear">
                            <i class="fas fa-unlock"></i> Desbloquear
                           </button>`;

                    let fila = `
                        <tr>
                            <td>${usuario.nombre_completo}</td>
                            <td>${usuario.correo}</td>
                            <td>${usuario.telefono}</td>
                            <td class="text-center">${estadoBtn}</td>
                            <td class="text-center">
                                <button class="btn btn-info btn-sm btn-detalles" data-id="${usuario.id}">
                                    <i class="fas fa-info-circle"></i> Ver Detalles
                                </button>
                            </td>
                        </tr>
                    `;
                    tabla.innerHTML += fila;
                });

                actualizarPaginacion(data);
                agregarEventosBotones();
                agregarEventosDetalles();
            })
            .catch(error => console.error("Error al cargar usuarios:", error));
    }

    function agregarEventosDetalles() {
        document.querySelectorAll(".btn-detalles").forEach(button => {
            button.addEventListener("click", function () {
                let userId = this.getAttribute("data-id");
                window.location.href = `/Blyss/admin/usuarios/view/${userId}/`;
            });
        });
    }

    function agregarEventosBotones() {
        document.querySelectorAll(".btn-toggle").forEach(button => {
            button.addEventListener("click", function () {
                let userId = this.getAttribute("data-id");

                fetch("/Blyss/usuarios/cambiar_estado/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: `user_id=${userId}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let newState = data.is_active ? "bloquear" : "desbloquear";
                        this.className = data.is_active ? "btn btn-danger btn-sm btn-toggle" : "btn btn-success btn-sm btn-toggle";
                        this.innerHTML = data.is_active 
                            ? `<i class="fas fa-lock"></i> Bloquear` 
                            : `<i class="fas fa-unlock"></i> Desbloquear`;
                        this.setAttribute("data-state", newState);
                    } else {
                        console.error("Error al cambiar estado:", data.error);
                    }
                })
                .catch(error => console.error("Error en la petición:", error));
            });
        });
    }

    function actualizarPaginacion(data) {
        let paginacion = document.getElementById("pagination-container");
        paginacion.innerHTML = "";

        if (data.has_previous) {
            paginacion.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="cargarUsuarios(1)">&laquo; Primero</a></li>`;
            paginacion.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="cargarUsuarios(${data.previous_page_number})">Anterior</a></li>`;
        }

        paginacion.innerHTML += `<li class="page-item disabled"><span class="page-link">Página ${data.current_page} de ${data.total_pages}</span></li>`;

        if (data.has_next) {
            paginacion.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="cargarUsuarios(${data.next_page_number})">Siguiente</a></li>`;
            paginacion.innerHTML += `<li class="page-item"><a class="page-link" href="#" onclick="cargarUsuarios(${data.total_pages})">Último &raquo;</a></li>`;
        }
    }

    function getCSRFToken() {
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                return cookie.substring("csrftoken=".length, cookie.length);
            }
        }
        return "";
    }

    window.cargarUsuarios = cargarUsuarios; // Permite llamarla desde HTML
});
