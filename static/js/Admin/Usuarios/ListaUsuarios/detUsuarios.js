document.addEventListener("DOMContentLoaded", function () {
    let btnActualizar = document.getElementById("btnActualizar");

    if (!btnActualizar) {
        console.error("❌ Botón de actualización no encontrado.");
        return;
    }

    let usuarioId = btnActualizar.getAttribute("data-user-id");

    if (!usuarioId) {
        alert("❌ Error: No se encontró el ID del usuario.");
        return;
    }

    // Evento para actualizar datos cuando se presiona el botón
    btnActualizar.addEventListener("click", function () {
        let datosActualizados = {};

        // Recorrer todos los campos editables y obtener sus valores
        document.querySelectorAll(".editable").forEach(input => {
            datosActualizados[input.dataset.field] = input.value;
        });

        // Obtener el estado del checkbox (activo/inactivo)
        let isActive = document.getElementById("is_active").checked ? "true" : "false";
        datosActualizados["is_active"] = isActive;

        // Llamar a la función para enviar los datos al backend
        actualizarUsuario(usuarioId, datosActualizados);
    });

    function actualizarUsuario(userId, datos) {
        fetch("/Blyss/usuarios/actualizar/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken()
            },
            body: new URLSearchParams({
                "user_id": userId,
                ...datos
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("✅ Usuario actualizado correctamente.");
            } else {
                alert("❌ Error al actualizar: " + data.error);
            }
        })
        .catch(error => {
            console.error("❌ Error en la petición:", error);
            alert("❌ Error al comunicarse con el servidor.");
        });
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
});
