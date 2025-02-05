document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-section").forEach(button => {
        button.addEventListener("click", function () {
            const sectionId = this.getAttribute("data-id");
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

            if (!csrfToken) {
                console.error("CSRF Token no encontrado.");
                return;
            }

            // Mostrar alerta de confirmación con SweetAlert2
            Swal.fire({
                title: "¿Estás seguro?",
                text: "Esta acción no se puede deshacer.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/Blyss/secciones/eliminar/${sectionId}/`, {
                        method: "DELETE",
                        headers: {
                            "X-CSRFToken": csrfToken,
                            "Content-Type": "application/json"
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire({
                                title: "¡Eliminado!",
                                text: "La sección ha sido eliminada correctamente.",
                                icon: "success",
                                timer: 2000,
                                showConfirmButton: false
                            }).then(() => {
                                location.reload();
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
});
