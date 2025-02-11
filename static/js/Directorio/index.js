document.addEventListener("DOMContentLoaded", function () {
    cargarDirecciones(); // Cargar direcciones al inicio

    document.getElementById("formNuevaDireccion").addEventListener("submit", function (event) {
        event.preventDefault();
    
        let form = this;
    
        // Si el formulario no es válido, detener el envío
        if (!form.checkValidity()) {
            event.stopPropagation();
            form.classList.add("was-validated");
            return;
        }
    
        let datos = {
            estado: document.getElementById("estado").value,
            cp: document.getElementById("cp").value,
            municipio: document.getElementById("municipio").value,
            ciudad: document.getElementById("ciudad").value,
            colonia: document.getElementById("colonia").value,
            calle: document.getElementById("calle").value,
            numero_exterior: document.getElementById("numero_exterior").value,
            numero_interior: document.getElementById("numero_interior").value || "",
            referencias: document.getElementById("referencias").value || ""
        };
    
        fetch("/Blyss/api/agregar_direccion/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken") // CSRF Protection en caso de estar activado
            },
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: "success",
                    title: "¡Dirección Creada!",
                    text: "✅ La dirección ha sido agregada correctamente.",
                    confirmButtonColor: "#3085d6",
                    confirmButtonText: "OK"
                }).then(() => {
                    document.getElementById("formNuevaDireccion").reset();
                    let modal = bootstrap.Modal.getInstance(document.getElementById("modalNuevaDireccion"));
                    modal.hide();
                    cargarDirecciones(); // Recargar direcciones dinámicamente
                });
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: "❌ " + data.message,
                    confirmButtonColor: "#d33"
                });
            }
        })
        .catch(error => {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "❌ Error al agregar la dirección: " + error,
                confirmButtonColor: "#d33"
            });
        });
    });
    
    // Obtener CSRF Token en caso de que Django lo necesite
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }    
    
    // Obtener CSRF Token en caso de que Django lo necesite
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
});

// Función para obtener direcciones y mostrarlas en cards
function cargarDirecciones() {
    fetch("/Blyss/api/direcciones/")
        .then(response => response.json())
        .then(data => {
            let container = document.querySelector("#direccion-lista");
            container.innerHTML = "";

            if (data.direcciones.length === 0) {
                container.innerHTML = `<div class="alert alert-warning text-center">No tienes direcciones registradas.</div>`;
                return;
            }

            let row = document.createElement("div");
            row.className = "row";

            data.direcciones.forEach(direccion => {
                let col = document.createElement("div");
                col.className = "col-12 mb-3"; // Ocupa todo el ancho

                col.innerHTML = `
                <div class="card border-0 shadow-sm rounded-4 p-3 position-relative bg-light">
                    <button class="btn btn-outline-dark btn-sm position-absolute top-0 end-0 m-3 rounded-circle" onclick="editarDireccion(${direccion.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    
                    <div class="d-flex align-items-center">
                        <div class="icon-box me-3">
                            <i class="fas fa-map-marker-alt fa-2x text-primary"></i>
                        </div>
                        <div class="w-100">
                            <h5 class="fw-bold text-dark mb-2">${direccion.calle} #${direccion.numero_exterior}</h5>
                            <p class="text-muted small mb-0">
                                <strong>Colonia:</strong> ${direccion.colonia} • <strong>Ciudad:</strong> ${direccion.ciudad}, ${direccion.municipio}
                            </p>
                            <p class="text-muted small mb-0">
                                <strong>Estado:</strong> ${direccion.estado} - <strong>CP:</strong> ${direccion.cp}
                            </p>
                            <p class="text-muted small mb-0">
                                <strong>Número Interior:</strong> ${direccion.numero_interior || 'N/A'}
                            </p>
                            <p class="text-muted small">
                                <strong>Referencias:</strong> ${direccion.referencias || 'Sin referencias'}
                            </p>
                        </div>
                    </div>
                </div>
                `;

                row.appendChild(col);
            });

            container.appendChild(row);
        })
        .catch(error => console.error("Error al obtener direcciones:", error));
}


// Redirigir a la página de edición
function editarDireccion(idDireccion) {
    window.location.href = `/Blyss/Directorio/view/${idDireccion}/`;
}

// Obtener CSRF Token en caso de que Django lo necesite
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
