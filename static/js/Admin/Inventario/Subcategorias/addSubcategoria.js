document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#add-subcategoria-form");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Evita el envío tradicional del formulario

        // Validar formulario
        const isValid = validateForm(form);
        if (!isValid) {
            Swal.fire({
                icon: "error",
                title: "Formulario inválido",
                text: "Por favor, corrige los errores en el formulario antes de enviarlo.",
            });
            return;
        }

        // Preparar datos
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        fetch("/Blyss/admin/inventario/add-subcategoria/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    Swal.fire({
                        icon: "success",
                        title: "Subcategoría registrada",
                        text: "La subcategoría ha sido creada exitosamente.",
                        confirmButtonText: "Aceptar",
                    }).then(() => {
                        form.reset(); // Limpiar el formulario
                    });
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error al registrar",
                        text: data.message || "Ocurrió un error al registrar la subcategoría.",
                    });
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                Swal.fire({
                    icon: "error",
                    title: "Error inesperado",
                    text: "Ocurrió un error al procesar la solicitud.",
                });
            });
    });

    // Validar formulario
    function validateForm(form) {
        let isValid = true;

        // Validar Nombre
        const nombre = form.querySelector("#nombre");
        if (!nombre.value.trim()) {
            setError(nombre, "El nombre es obligatorio.");
            isValid = false;
        } else if (nombre.value.trim().length > 100) {
            setError(nombre, "El nombre no puede exceder los 100 caracteres.");
            isValid = false;
        } else {
            clearError(nombre);
        }

        // Validar Descripción
        const descripcion = form.querySelector("#descripcion");
        if (descripcion.value.trim().length > 200) {
            setError(descripcion, "La descripción no puede exceder los 200 caracteres.");
            isValid = false;
        } else {
            clearError(descripcion);
        }

        // Validar Estado
        const estado = form.querySelector("#estado");
        if (!estado.value || estado.value === "") {
            setError(estado, "Debes seleccionar un estado.");
            isValid = false;
        } else {
            clearError(estado);
        }

        return isValid;
    }

    // Mostrar errores
    function setError(input, message) {
        const errorDiv = input.nextElementSibling;
        input.classList.add("is-invalid");
        if (errorDiv && errorDiv.classList.contains("invalid-feedback")) {
            errorDiv.textContent = message;
        }
    }

    // Limpiar errores
    function clearError(input) {
        input.classList.remove("is-invalid");
        input.classList.add("is-valid");
    }
});
