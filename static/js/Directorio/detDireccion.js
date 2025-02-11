document.getElementById("formEditarDireccion").addEventListener("submit", function(event) {
    event.preventDefault(); // Evitar recarga de página

    let form = this;

    // Validación de Bootstrap
    if (!form.checkValidity()) {
        event.stopPropagation();
        form.classList.add("was-validated");
        return;
    }

    let idDireccion = document.getElementById("id_direccion").value;

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

    fetch(`/Blyss/api/actualizar_direccion/${idDireccion}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                icon: "success",
                title: "¡Actualizado!",
                text: "✅ La dirección se ha actualizado correctamente.",
                confirmButtonColor: "#3085d6",
                confirmButtonText: "OK"
            }).then(() => {
                window.location.href = "/Blyss/Directorio/"; // Redirige al listado
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
            text: "❌ Error al actualizar dirección: " + error,
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

document.getElementById("btnEliminar").addEventListener("click", function () {
    let idDireccion = document.getElementById("id_direccion").value;

    // Mostrar confirmación antes de eliminar
    Swal.fire({
        title: "¿Estás seguro?",
        text: "⚠ Esta acción eliminará la dirección permanentemente.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar"
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/Blyss/api/eliminar_direccion/${idDireccion}/`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: "success",
                        title: "¡Eliminado!",
                        text: "✅ Dirección eliminada correctamente.",
                        confirmButtonColor: "#3085d6",
                        confirmButtonText: "OK"
                    }).then(() => {
                        window.location.href = "/Blyss/Directorio/";  // Redirige a la lista de direcciones
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
                    text: "❌ Error al eliminar dirección: " + error,
                    confirmButtonColor: "#d33"
                });
            });
        }
    });
});

// Función para obtener el CSRF Token en caso de que Django lo necesite
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
