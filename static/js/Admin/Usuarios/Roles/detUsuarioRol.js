document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("btn-actualizar-rol").addEventListener("click", function () {
        const selectRol = document.getElementById("select-rol");
        const rolId = selectRol.value;
        const usuarioId = document.getElementById("usuario-id").value; // Obtener usuario_id del input oculto

        if (!usuarioId) {
            alert("Error: ID de usuario no definido.");
            return;
        }

        fetch("/Blyss/usuario/rol/actualizar/", {  // Ruta absoluta sin {% url %}
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `usuario_id=${usuarioId}&rol_id=${rolId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Rol actualizado correctamente.");
            } else {
                alert("Error al actualizar el rol.");
            }
        })
        .catch(error => console.error("Error:", error));
    });

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const usuarioId = document.getElementById("usuario-id").value;

    if (usuarioId) {
        cargarPermisos(usuarioId);
    }

    document.getElementById("btn-actualizar-rol").addEventListener("click", function () {
        const selectRol = document.getElementById("select-rol");
        const rolId = selectRol.value;

        if (!usuarioId) {
            alert("Error: ID de usuario no definido.");
            return;
        }

        fetch("/Blyss/usuario/rol/actualizar/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `usuario_id=${usuarioId}&rol_id=${rolId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Rol actualizado correctamente.");
                cargarPermisos(usuarioId); // Recargar permisos
            } else {
                alert("Error al actualizar el rol.");
            }
        })
        .catch(error => console.error("Error:", error));
    });

    document.getElementById("btn-nuevo-permiso").addEventListener("click", function () {
        fetch(`/Blyss/usuario/${usuarioId}/permisos_disponibles/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let opciones = `<option value="" disabled selected>Selecciona un permiso</option>`; // Placeholder
                    data.permisos.forEach(permiso => {
                        opciones += `<option value="${permiso.id}">${permiso.descripcion}</option>`;
                    });

                    if (data.permisos.length === 0) {
                        Swal.fire("Atención", "No hay permisos disponibles para asignar.", "info");
                        return;
                    }

                    Swal.fire({
                        title: "Asignar Nuevo Permiso",
                        html: `<select id="select-permiso" class="swal2-input">${opciones}</select>`,
                        showCancelButton: true,
                        confirmButtonText: "Asignar",
                        cancelButtonText: "Cancelar",
                        preConfirm: () => {
                            const selectElement = document.getElementById("select-permiso");
                            if (selectElement.value === "") {
                                Swal.showValidationMessage("Debes seleccionar un permiso");
                            }
                            return selectElement.value;
                        }
                    }).then((result) => {
                        if (result.isConfirmed) {
                            const permisoId = result.value;

                            fetch("/Blyss/usuario/asignar_permiso/", {
                                method: "POST",
                                headers: {
                                    "X-CSRFToken": getCSRFToken(),
                                    "Content-Type": "application/x-www-form-urlencoded"
                                },
                                body: `usuario_id=${usuarioId}&permiso_id=${permisoId}`
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    Swal.fire("Éxito", "Permiso asignado correctamente.", "success");
                                    cargarPermisos(usuarioId); // Recargar permisos
                                } else {
                                    Swal.fire("Error", data.message, "error");
                                }
                            })
                            .catch(error => console.error("Error:", error));
                        }
                    });
                } else {
                    console.error("Error al obtener permisos disponibles.");
                }
            })
            .catch(error => console.error("Error:", error));
    });

    function cargarPermisos(usuarioId) {
        fetch(`/Blyss/usuario/${usuarioId}/permisos/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const tbody = document.querySelector("#tabla-permisos tbody");
                    tbody.innerHTML = "";

                    data.permisos.forEach(permiso => {
                        const fila = document.createElement("tr");
                        fila.innerHTML = `
                            <td>${permiso.id}</td>
                            <td>${permiso.descripcion}</td>
                            <td>${permiso.fecha}</td>
                            <td class="text-center">
                                <button class="btn btn-danger btn-quitar-permiso" data-permiso-id="${permiso.id}">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </td>
                        `;
                        tbody.appendChild(fila);
                    });

                    document.querySelectorAll(".btn-quitar-permiso").forEach(button => {
                        button.addEventListener("click", function () {
                            const permisoId = this.getAttribute("data-permiso-id");
                            quitarPermiso(usuarioId, permisoId);
                        });
                    });
                } else {
                    console.error("Error al obtener permisos.");
                }
            })
            .catch(error => console.error("Error:", error));
    }

    function quitarPermiso(usuarioId, permisoId) {
        Swal.fire({
            title: "¿Estás seguro?",
            text: "Esta acción eliminará el permiso del usuario.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "Sí, quitar",
            cancelButtonText: "Cancelar"
        }).then((result) => {
            if (result.isConfirmed) {
                fetch("/Blyss/usuario/quitar_permiso/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: `usuario_id=${usuarioId}&permiso_id=${permisoId}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire("Eliminado", "Permiso eliminado correctamente.", "success");
                        cargarPermisos(usuarioId);
                    } else {
                        Swal.fire("Error", data.message, "error");
                    }
                })
                .catch(error => console.error("Error:", error));
            }
        });
    }

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
    }
});
