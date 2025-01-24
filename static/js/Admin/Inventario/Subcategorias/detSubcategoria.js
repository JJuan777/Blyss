document.addEventListener("DOMContentLoaded", function () {
    const deleteButton = document.getElementById("delete-subcategory");
    const editToggleButton = document.getElementById("edit-toggle");
    const saveChangesButton = document.getElementById("save-changes");
    const editableNombre = document.getElementById("editable-nombre");
    const editableDescripcion = document.getElementById("editable-descripcion");
    const editableEstado = document.getElementById("editable-estado");

    const subcategoriaId = deleteButton.getAttribute("data-id");
    let isEditing = false;

    // Habilitar edición
    editToggleButton.addEventListener("click", function () {
        if (!isEditing) {
            toggleEditing(true);
        }
    });

    // Guardar cambios
    saveChangesButton.addEventListener("click", function () {
        const updatedNombre = editableNombre.textContent.trim();
        const updatedDescripcion = editableDescripcion.textContent.trim();
        const updatedEstado = editableEstado.value;

        if (!validateInputs(updatedNombre, updatedDescripcion)) {
            Swal.fire({
                icon: "error",
                title: "Formulario inválido",
                text: "Por favor, corrige los errores antes de guardar.",
            });
            return;
        }

        fetch(`/Blyss/admin/inventario/subcategorias/update/${subcategoriaId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            },
            body: JSON.stringify({
                nombre: updatedNombre,
                descripcion: updatedDescripcion,
                estado: updatedEstado,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    Swal.fire({
                        icon: "success",
                        title: "Subcategoría actualizada",
                        text: "Los cambios se han guardado exitosamente.",
                    });
                    toggleEditing(false);
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: data.message || "No se pudo guardar la subcategoría.",
                    });
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                Swal.fire({
                    icon: "error",
                    title: "Error inesperado",
                    text: "Ocurrió un error al guardar los cambios.",
                });
            });
    });

    // Eliminar subcategoría
    deleteButton.addEventListener("click", function () {
        Swal.fire({
            title: "¿Estás seguro?",
            text: "Esta acción eliminará la subcategoría de forma permanente.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#6c757d",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
        }).then((result) => {
            if (result.isConfirmed) {
                console.log(subcategoriaId)
                fetch(`/Blyss/admin/inventario/subcategorias/delete/${subcategoriaId}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.success) {
                            Swal.fire({
                                icon: "success",
                                title: "Subcategoría eliminada",
                                text: "La subcategoría se ha eliminado correctamente.",
                                confirmButtonText: "Aceptar",
                            }).then(() => {
                                window.location.href = "/Blyss/admin/inventario/subcategorias/";
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: "Error",
                                text: data.message || "No se pudo eliminar la subcategoría.",
                            });
                        }
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                        Swal.fire({
                            icon: "error",
                            title: "Error inesperado",
                            text: "Ocurrió un error al intentar eliminar la subcategoría.",
                        });
                    });
            }
        });
    });

    // Validar entradas
    function validateInputs(nombre, descripcion) {
        if (!nombre || nombre.length > 100) {
            return false;
        }
        if (descripcion.length > 200) {
            return false;
        }
        return true;
    }

    // Alternar edición
    function toggleEditing(enable) {
        isEditing = enable;

        editableNombre.contentEditable = enable;
        editableDescripcion.contentEditable = enable;
        editableEstado.disabled = !enable;

        editToggleButton.classList.toggle("d-none", enable);
        saveChangesButton.classList.toggle("d-none", !enable);
    }
});
