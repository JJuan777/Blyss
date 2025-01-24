document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#add-categoria-form");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevenir el envío tradicional del formulario

        // Validar el formulario
        const isValid = validateForm(form);
        if (!isValid) {
            Swal.fire({
                icon: "error",
                title: "Formulario inválido",
                text: "Por favor, corrige los errores en el formulario antes de enviarlo.",
            });
            return;
        }

        // Preparar los datos
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Enviar la solicitud POST con fetch
        fetch("/Blyss/admin/inventario/add-categoria/", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Error en la solicitud");
                }
                return response.json();
            })
            .then((data) => {
                if (data.success) {
                    Swal.fire({
                        icon: "success",
                        title: "Categoría registrada",
                        text: "La categoría ha sido creada exitosamente.",
                        confirmButtonText: "Aceptar",
                    }).then(() => {
                        form.reset(); // Limpiar el formulario
                        clearAllValidation(form); // Limpiar todas las validaciones
                    });
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error al registrar",
                        text: data.message || "Ocurrió un error al registrar la categoría.",
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

    // Establecer error
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

    // Limpiar todas las validaciones del formulario
    function clearAllValidation(form) {
        form.querySelectorAll(".is-valid, .is-invalid").forEach((input) => {
            input.classList.remove("is-valid", "is-invalid");
        });
        form.querySelectorAll(".invalid-feedback").forEach((errorDiv) => {
            errorDiv.textContent = "";
        });
    }
});
