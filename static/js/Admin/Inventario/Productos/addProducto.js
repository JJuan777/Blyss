document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#add-producto-form");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Previene el envío predeterminado del formulario
    
        // Validar campos del formulario
        const isValid = validateForm(form);
    
        if (!isValid) {
            Swal.fire({
                icon: "error",
                title: "Formulario inválido",
                text: "Por favor, corrige los errores en el formulario antes de enviarlo.",
            });
            return;
        }
    
        const formData = new FormData(form);
    
        // Validar que el número de imágenes no exceda el límite
        const files = formData.getAll("imagenes");
        if (files.length > 10) {
            Swal.fire({
                icon: "error",
                title: "Demasiadas imágenes",
                text: "Solo puedes cargar un máximo de 10 imágenes.",
            });
            return;
        }
    
        // Enviar la solicitud al servidor
        fetch("/Blyss/admin/inventario/add-producto/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
            },
            body: formData,
        })
            .then((response) => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error("Error al guardar el producto");
            })
            .then((data) => {
                if (data.success) {
                    Swal.fire({
                        icon: "success",
                        title: "Producto registrado",
                        text: "El producto y las imágenes han sido registrados exitosamente.",
                        confirmButtonText: "Aceptar",
                    }).then(() => {
                        // Limpiar el formulario
                        form.reset();
    
                        // Eliminar las previsualizaciones
                        const previewContainer = document.getElementById("preview-container");
                        previewContainer.innerHTML = "";
    
                        // Limpiar validaciones (si tienes una función personalizada para esto)
                        clearAllValidation(form);
                    });
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error al registrar",
                        text: data.message || "Ocurrió un error al registrar el producto.",
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

    // Función para validar el formulario
    function validateForm(form) {
        let isValid = true;

        // Validar campos de texto
        const textFields = [
            { id: "nombre", maxLength: 150, required: true },
            { id: "sku", maxLength: 50, required: true },
            { id: "marca", maxLength: 100, required: true },
            { id: "descripcion", maxLength: 500, required: true },
        ];

        textFields.forEach((field) => {
            const input = form.querySelector(`#${field.id}`);
            const value = input.value.trim();

            if (field.required && !value) {
                setError(input, "Este campo es obligatorio.");
                isValid = false;
            } else if (value.length > field.maxLength) {
                setError(
                    input,
                    `Este campo no debe exceder los ${field.maxLength} caracteres.`
                );
                isValid = false;
            } else {
                clearError(input);
            }
        });

        // Validar campos numéricos
        const numberFields = [
            { id: "precio", min: 0, required: true },
            { id: "precio_descuento", min: 0, required: false },
            { id: "stock", min: 0, required: true },
            { id: "stock_max", min: 0, required: true },
            { id: "stock_min", min: 0, required: true },
            { id: "peso", min: 0, required: true },
        ];

        numberFields.forEach((field) => {
            const input = form.querySelector(`#${field.id}`);
            const value = parseFloat(input.value);

            if (field.required && (isNaN(value) || value === "")) {
                setError(input, "Este campo es obligatorio.");
                isValid = false;
            } else if (!isNaN(value) && value < field.min) {
                setError(input, `El valor no puede ser menor que ${field.min}.`);
                isValid = false;
            } else {
                clearError(input);
            }
        });

        // Validar select de estado
        const estado = form.querySelector("#estado");
        if (!estado.value) {
            setError(estado, "Debes seleccionar un estado.");
            isValid = false;
        } else {
            clearError(estado);
        }

        // Validar select de categoría
        const categoria = form.querySelector("#categoria");
        if (!categoria.value) {
            setError(categoria, "Debes seleccionar una categoría.");
            isValid = false;
        } else {
            clearError(categoria);
        }

        // Validar select de subcategoría
        const subcategoria = form.querySelector("#subcategoria");
        if (!subcategoria.value) {
            setError(subcategoria, "Debes seleccionar una subcategoría.");
            isValid = false;
        } else {
            clearError(subcategoria);
        }

        return isValid;
    }

    // Función para establecer mensajes de error
    function setError(input, message) {
        const errorDiv = input.nextElementSibling;
        input.classList.add("is-invalid");
        if (errorDiv && errorDiv.classList.contains("invalid-feedback")) {
            errorDiv.textContent = message;
        }
    }

    // Función para limpiar mensajes de error
    function clearError(input) {
        const errorDiv = input.nextElementSibling;
        input.classList.remove("is-invalid");
        input.classList.add("is-valid");
        if (errorDiv && errorDiv.classList.contains("invalid-feedback")) {
            errorDiv.textContent = "";
        }
    }

    // Función para limpiar todas las validaciones del formulario
    function clearAllValidation(form) {
        form.querySelectorAll(".is-valid, .is-invalid").forEach((input) => {
            input.classList.remove("is-valid", "is-invalid");
        });
        form.querySelectorAll(".invalid-feedback").forEach((errorDiv) => {
            errorDiv.textContent = "";
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.getElementById("imagenes");
    const previewContainer = document.getElementById("preview-container");

    // Manejar la selección de imágenes
    imageInput.addEventListener("change", function () {
        // Limpiar las previsualizaciones anteriores
        previewContainer.innerHTML = "";

        const files = Array.from(this.files);

        // Validar límite de imágenes
        if (files.length > 10) {
            Swal.fire({
                icon: "error",
                title: "Demasiadas imágenes",
                text: "Solo puedes cargar un máximo de 10 imágenes.",
            });
            this.value = ""; // Limpiar el input
            return;
        }

        // Mostrar previsualización de las imágenes seleccionadas
        files.forEach((file, index) => {
            const reader = new FileReader();

            reader.onload = function (e) {
                // Crear una card para cada imagen
                const imageCard = document.createElement("div");
                imageCard.className = "col-md-3 position-relative";

                imageCard.innerHTML = `
                    <div class="card shadow-sm">
                        <button 
                            type="button"
                            class="btn-close position-absolute top-0 end-0 m-2 remove-image" 
                            data-index="${index}" 
                            aria-label="Eliminar"
                        ></button>
                        <div class="d-flex align-items-center justify-content-center p-2 bg-light" style="height: 180px;">
                            <img 
                                src="${e.target.result}" 
                                class="img-fluid rounded"
                                alt="Imagen seleccionada"
                                style="max-width: 100%; max-height: 100%; object-fit: contain;"
                            />
                        </div>
                    </div>
                `;

                previewContainer.appendChild(imageCard);
            };

            reader.readAsDataURL(file);
        });
    });

    // Manejar eliminación de imágenes de la selección
    previewContainer.addEventListener("click", function (event) {
        if (event.target.classList.contains("remove-image")) {
            const index = event.target.getAttribute("data-index");

            // Eliminar la imagen del input
            const fileList = Array.from(imageInput.files);
            fileList.splice(index, 1);

            // Crear un nuevo objeto FileList sin la imagen eliminada
            const dataTransfer = new DataTransfer();
            fileList.forEach((file) => dataTransfer.items.add(file));

            imageInput.files = dataTransfer.files;

            // Actualizar la previsualización
            event.target.closest(".col-md-3").remove();
        }
    });
});
