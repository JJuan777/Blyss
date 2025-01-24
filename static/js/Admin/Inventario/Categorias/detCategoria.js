document.addEventListener("DOMContentLoaded", function () {
    const editToggleButton = document.getElementById("edit-toggle");
    const saveChangesButton = document.getElementById("save-changes");
    const editableNombre = document.getElementById("editable-nombre");
    const editableDescripcion = document.getElementById("editable-descripcion");
    const editableEstado = document.getElementById("editable-estado");

    // Obtener el ID de la categoría
    const categoriaId = editToggleButton.getAttribute("data-id");

    let isEditing = false;

    // Alternar entre habilitar edición y guardar cambios
    editToggleButton.addEventListener("click", function () {
        if (!isEditing) {
            // Habilitar edición
            isEditing = true;
            toggleEditing(true);
        }
    });

    // Validar entradas al guardar cambios
    saveChangesButton.addEventListener("click", function () {
        const updatedNombre = editableNombre.textContent.trim();
        const updatedDescripcion = editableDescripcion.textContent.trim();
        const updatedEstado = editableEstado.value;

        const isValid = validateInputs(updatedNombre, updatedDescripcion);

        if (!isValid) {
            Swal.fire({
                icon: "error",
                title: "Formulario inválido",
                text: "Por favor, corrige los errores antes de guardar.",
            });
            return;
        }

        fetch(`/Blyss/admin/inventario/categorias/update/${categoriaId}/`, {
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
                        title: "Categoría actualizada",
                        text: "Los cambios se han guardado exitosamente.",
                    });
                    toggleEditing(false);
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: data.message || "No se pudo guardar la categoría.",
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

    // Validación en tiempo real
    editableNombre.addEventListener("input", () => {
        validateField(editableNombre, "El nombre es obligatorio y no debe exceder los 100 caracteres.", 100);
    });

    editableDescripcion.addEventListener("input", () => {
        validateField(editableDescripcion, "La descripción no debe exceder los 200 caracteres.", 200, false);
    });

    // Función para alternar entre edición y vista
    function toggleEditing(enable) {
        isEditing = enable;

        editableNombre.contentEditable = enable;
        editableDescripcion.contentEditable = enable;
        editableEstado.disabled = !enable;

        if (enable) {
            editToggleButton.classList.add("d-none");
            saveChangesButton.classList.remove("d-none");

            editableNombre.classList.add("border", "border-primary", "rounded", "px-2", "bg-light");
            editableDescripcion.classList.add("border", "border-primary", "rounded", "px-2", "bg-light");
        } else {
            editToggleButton.classList.remove("d-none");
            saveChangesButton.classList.add("d-none");

            editableNombre.classList.remove("border", "border-primary", "rounded", "px-2", "bg-light");
            editableDescripcion.classList.remove("border", "border-primary", "rounded", "px-2", "bg-light");
        }
    }

    // Validar campos individuales
    function validateField(element, errorMessage, maxLength, required = true) {
        const value = element.textContent.trim();
        if ((required && !value) || value.length > maxLength) {
            setError(element, errorMessage);
            return false;
        }
        clearError(element);
        return true;
    }

    // Validar todos los campos
    function validateInputs(nombre, descripcion) {
        let isValid = true;

        if (!validateField(editableNombre, "El nombre es obligatorio y no debe exceder los 100 caracteres.", 100)) {
            isValid = false;
        }

        if (!validateField(editableDescripcion, "La descripción no debe exceder los 200 caracteres.", 200, false)) {
            isValid = false;
        }

        return isValid;
    }

    // Mostrar error
    function setError(element, message) {
        element.classList.add("border-danger");
        element.classList.remove("border-primary");
        if (!element.nextElementSibling || !element.nextElementSibling.classList.contains("error-message")) {
            const errorDiv = document.createElement("div");
            errorDiv.className = "error-message text-danger mt-1";
            errorDiv.textContent = message;
            element.parentElement.appendChild(errorDiv);
        }
    }

    // Limpiar error
    function clearError(element) {
        element.classList.remove("border-danger");
        element.classList.add("border-primary");
        const errorDiv = element.parentElement.querySelector(".error-message");
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    //Eliminar
    const deleteButton = document.getElementById("delete-category");

    // Confirmar y eliminar categoría
    deleteButton.addEventListener("click", function () {
        Swal.fire({
            title: "¿Estás seguro?",
            text: "Esta acción eliminará la categoría de forma permanente.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#6c757d",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/Blyss/admin/inventario/categorias/delete/${categoriaId}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    },
                })
                    .then((response) => {
                        if (response.ok) {
                            return response.json();
                        }
                        throw new Error("No se pudo eliminar la categoría.");
                    })
                    .then((data) => {
                        if (data.success) {
                            Swal.fire({
                                icon: "success",
                                title: "Categoría eliminada",
                                text: "La categoría se ha eliminado correctamente.",
                                confirmButtonText: "Aceptar",
                            }).then(() => {
                                window.location.href = "/Blyss/admin/inventario/categorias/";
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: "Error",
                                text: data.message || "No se pudo eliminar la categoría.",
                            });
                        }
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                        Swal.fire({
                            icon: "error",
                            title: "Error inesperado",
                            text: "Ocurrió un error al intentar eliminar la categoría.",
                        });
                    });
            }
        });
    });


});
