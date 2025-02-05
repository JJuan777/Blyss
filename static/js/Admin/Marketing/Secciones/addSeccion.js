document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("seccionForm").addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(this);
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        Swal.fire({
            title: "¿Guardar nueva sección?",
            text: "Confirma que deseas agregar esta sección.",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Sí, guardar",
            cancelButtonText: "Cancelar"
        }).then((result) => {
            if (result.isConfirmed) {
                fetch("/Blyss/admin/marketing/secciones/agregar/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            title: "¡Guardado!",
                            text: "La sección se ha agregado correctamente.",
                            icon: "success",
                            timer: 2000,
                            showConfirmButton: false
                        }).then(() => {
                            window.location.href = "/Blyss/admin/marketing/secciones/";
                        });
                    } else {
                        Swal.fire({
                            title: "Error",
                            text: data.error,
                            icon: "error",
                            confirmButtonText: "OK"
                        });
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    Swal.fire({
                        title: "Error",
                        text: "Ocurrió un error inesperado.",
                        icon: "error",
                        confirmButtonText: "OK"
                    });
                });
            }
        });
    });
});
