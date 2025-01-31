document.addEventListener("DOMContentLoaded", function () {
    const editToggleButton = document.getElementById("edit-toggle");
    const saveChangesButton = document.getElementById("save-changes");
    const editableNombre = document.getElementById("editable-nombre");
    const editableDescripcion = document.getElementById("editable-descripcion");
    const editableEstado = document.getElementById("editable-estado");
    const uploadImageInput = document.getElementById("upload-image");
    const removeImageButton = document.getElementById("remove-image");
    const categoriaImagen = document.getElementById("categoria-imagen");
    const deleteButton = document.getElementById("delete-category");

    const categoriaId = editToggleButton.getAttribute("data-id");
    let isEditing = false;
    let imageRemoved = false; // Bandera para saber si se eliminó la imagen

    // Habilitar edición
    editToggleButton.addEventListener("click", function () {
        isEditing = true;
        toggleEditing(true);
    });

    // Previsualización de la imagen al seleccionar un archivo
    uploadImageInput.addEventListener("change", function () {
        const file = uploadImageInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                categoriaImagen.src = e.target.result;
                imageRemoved = false; // Reiniciar bandera si se sube una nueva imagen
            };
            reader.readAsDataURL(file);
        }
    });

    // Eliminar imagen
    removeImageButton.addEventListener("click", function () {
        categoriaImagen.src = "/static/img/default-image.webp"; // Imagen por defecto
        uploadImageInput.value = "";
        imageRemoved = true; // Marcar imagen como eliminada
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

        const formData = new FormData();
        formData.append("nombre", updatedNombre);
        formData.append("descripcion", updatedDescripcion);
        formData.append("estado", updatedEstado);

        if (uploadImageInput.files[0]) {
            formData.append("imagen", uploadImageInput.files[0]);
        } else if (imageRemoved) {
            formData.append("eliminar_imagen", "True"); // Indicar que la imagen debe eliminarse
        }

        fetch(`/Blyss/admin/inventario/categorias/update/${categoriaId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: "success",
                    title: "Categoría actualizada",
                    text: "Los cambios se han guardado exitosamente.",
                }).then(() => {
                    toggleEditing(false);
                    location.reload();
                });
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: data.message || "No se pudo guardar la categoría.",
                });
            }
        })
        .catch(error => {
            console.error("Error:", error);
            Swal.fire({
                icon: "error",
                title: "Error inesperado",
                text: "Ocurrió un error al guardar los cambios.",
            });
        });
    });

    // Alternar edición
    function toggleEditing(enable) {
        isEditing = enable;
        editableNombre.contentEditable = enable;
        editableDescripcion.contentEditable = enable;
        editableEstado.disabled = !enable;
        uploadImageInput.classList.toggle("d-none", !enable);
        removeImageButton.classList.toggle("d-none", !enable);
        saveChangesButton.classList.toggle("d-none", !enable);
        editToggleButton.classList.toggle("d-none", enable);

        if (enable) {
            editableNombre.classList.add("border", "border-primary", "rounded", "px-2", "bg-light");
            editableDescripcion.classList.add("border", "border-primary", "rounded", "px-2", "bg-light");
        } else {
            editableNombre.classList.remove("border", "border-primary", "rounded", "px-2", "bg-light");
            editableDescripcion.classList.remove("border", "border-primary", "rounded", "px-2", "bg-light");
        }
    }

    // Validaciones
    function validateField(element, errorMessage, maxLength, required = true) {
        const value = element.textContent.trim();
        if ((required && !value) || value.length > maxLength) {
            setError(element, errorMessage);
            return false;
        }
        clearError(element);
        return true;
    }

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

    function clearError(element) {
        element.classList.remove("border-danger");
        element.classList.add("border-primary");
        const errorDiv = element.parentElement.querySelector(".error-message");
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // Eliminar categoría
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
                .then((response) => response.ok ? response.json() : Promise.reject("No se pudo eliminar la categoría."))
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
