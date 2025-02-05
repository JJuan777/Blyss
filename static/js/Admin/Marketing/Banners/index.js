document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-banner").forEach(button => {
        button.addEventListener("click", function () {
            const bannerId = this.getAttribute("data-id");

            Swal.fire({
                title: "¿Estás seguro?",
                text: "Esta acción eliminará el banner de forma permanente.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/Blyss/admin/marketing/banners/eliminar/${bannerId}/`, {
                        method: "DELETE",
                        headers: {
                            "X-CSRFToken": document.getElementById("csrf_token").value

                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire("¡Eliminado!", data.message, "success");
                            document.getElementById(`banner-${bannerId}`).remove();
                        } else {
                            Swal.fire("Error", data.message, "error");
                        }
                    })
                    .catch(error => {
                        console.error("Error al eliminar el banner:", error);
                        Swal.fire("Error", "No se pudo eliminar el banner.", "error");
                    });
                }
            });
        });
    });
});
