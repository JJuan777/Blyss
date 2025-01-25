document.addEventListener("DOMContentLoaded", function () {
    const editToggle = document.getElementById("edit-toggle");
    const saveChangesButton = document.getElementById("save-changes");
    const deleteButton = document.getElementById("delete-product");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    let isEditing = false;

    // Habilitar edición
    editToggle.addEventListener("click", () => {
        isEditing = !isEditing;

        // Alternar modo de edición
        document.querySelectorAll("[id^='editable-']").forEach((element) => {
            if (element.tagName === "P") {
                element.classList.toggle("form-control-plaintext");
                element.contentEditable = isEditing;
            } else if (element.tagName === "SELECT") {
                element.disabled = !isEditing;
            }
        });

        saveChangesButton.classList.toggle("d-none", !isEditing);
        editToggle.textContent = isEditing ? "Cancelar Edición" : "Habilitar Edición";
    });

    // Guardar cambios
    saveChangesButton.addEventListener("click", () => {
        const data = {
            nombre: document.getElementById("editable-nombre").textContent.trim(),
            sku: document.getElementById("editable-sku").textContent.trim(),
            precio: parseFloat(document.getElementById("editable-precio").textContent.trim()),
            descripcion: document.getElementById("editable-descripcion").textContent.trim(),
            estado: document.getElementById("editable-estado").value === "True",
        };

        fetch(`/Blyss/admin/inventario/productos/update/${editToggle.dataset.id}/`, {
            method: "PUT",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((data) => {
                Swal.fire({
                    icon: data.success ? "success" : "error",
                    title: data.success ? "Guardado" : "Error",
                    text: data.message,
                });

                if (data.success) location.reload();
            });
    });

    // Eliminar producto
    deleteButton.addEventListener("click", () => {
        Swal.fire({
            title: "¿Estás seguro?",
            text: "No podrás deshacer esta acción",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "Sí, eliminar",
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/Blyss/admin/inventario/productos/delete/${editToggle.dataset.id}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": csrfToken,
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        Swal.fire({
                            icon: data.success ? "success" : "error",
                            title: data.success ? "Eliminado" : "Error",
                            text: data.message,
                        });

                        if (data.success) window.location.href = "/Blyss/admin/inventario/productos/";
                    });
            }
        });
    });
});
