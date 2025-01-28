document.addEventListener("DOMContentLoaded", function () {
    const editToggle = document.getElementById("edit-toggle");
    const saveChanges = document.getElementById("save-changes");
    const csrfToken = document.querySelector("input[name=csrfmiddlewaretoken]").value;

    // Habilitar edición
    editToggle.addEventListener("click", () => {
        document.querySelectorAll("[id^=editable-]").forEach((field) => {
            if (field.tagName === "SELECT" || field.tagName === "INPUT") {
                field.disabled = false;
            } else {
                field.contentEditable = true;
                field.classList.add("bg-white");
            }
        });
        saveChanges.classList.remove("d-none");
        Swal.fire({
            icon: "info",
            title: "Edición habilitada",
            text: "Ahora puedes editar los campos del producto.",
            timer: 2000,
            showConfirmButton: false,
        });
    });

    // Guardar cambios
    saveChanges.addEventListener("click", () => {
        const productoId = editToggle.getAttribute("data-id");
        const payload = {
            producto_id: productoId,
            nombre: document.getElementById("editable-nombre").innerText.trim(),
            sku: document.getElementById("editable-sku").innerText.trim(),
            precio: parseFloat(document.getElementById("editable-precio").value),
            precio_descuento: parseFloat(document.getElementById("editable-precio-descuento").value),
            stock: parseInt(document.getElementById("editable-stock").innerText.trim()),
            descripcion: document.getElementById("editable-descripcion").innerText.trim(),
            estado: document.getElementById("editable-estado").value === "True",
            categoria_id: document.getElementById("editable-categoria").value,
            subcategoria_id: document.getElementById("editable-subcategoria").value,
        };

        fetch("/Blyss/actualizar-producto/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    Swal.fire({
                        icon: "success",
                        title: "Cambios guardados",
                        text: data.message,
                        timer: 2000,
                        showConfirmButton: false,
                    });
                    saveChanges.classList.add("d-none");
                    document.querySelectorAll("[id^=editable-]").forEach((field) => {
                        field.disabled = true;
                        field.classList.remove("bg-white");
                    });
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: data.message,
                    });
                }
            })
            .catch((error) => {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: `Error: ${error}`,
                });
            });
    });

    // Eliminar producto
    const deleteProduct = document.getElementById("delete-product");

    deleteProduct.addEventListener("click", () => {
        const productoId = deleteProduct.getAttribute("data-id");

        Swal.fire({
            title: "¿Estás seguro?",
            text: "No podrás revertir esta acción.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar",
        }).then((result) => {
            if (result.isConfirmed) {
                fetch("/Blyss/eliminar-producto/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify({ producto_id: productoId }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.success) {
                            Swal.fire({
                                icon: "success",
                                title: "Eliminado",
                                text: data.message,
                                timer: 2000,
                                showConfirmButton: false,
                            }).then(() => {
                                // Redirigir al listado de productos
                                window.location.href = "/Blyss/Admin/inventario/productos";
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: "Error",
                                text: data.message,
                            });
                        }
                    })
                    .catch((error) => {
                        Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: `Error: ${error}`,
                        });
                    });
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const csrfToken = document.querySelector("input[name=csrfmiddlewaretoken]").value;

    // Manejar la eliminación de imágenes
    document.querySelectorAll(".delete-image").forEach((button) => {
        button.addEventListener("click", function () {
            const imageId = this.getAttribute("data-id");

            // Confirmación antes de eliminar
            Swal.fire({
                title: "¿Estás seguro?",
                text: "No podrás revertir esta acción.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar",
            }).then((result) => {
                if (result.isConfirmed) {
                    // Realizar la solicitud AJAX
                    fetch(`/Blyss/eliminar-imagen/${imageId}/`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": csrfToken,
                        },
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            if (data.success) {
                                Swal.fire({
                                    icon: "success",
                                    title: "Eliminado",
                                    text: data.message,
                                    timer: 2000,
                                    showConfirmButton: false,
                                });
                                // Eliminar la card de la imagen del DOM
                                this.closest(".card").remove();
                            } else {
                                Swal.fire({
                                    icon: "error",
                                    title: "Error",
                                    text: data.message,
                                });
                            }
                        })
                        .catch((error) => {
                            Swal.fire({
                                icon: "error",
                                title: "Error",
                                text: `Error: ${error}`,
                            });
                        });
                }
            });
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("upload-form");
    const csrfToken = document.querySelector("input[name=csrfmiddlewaretoken]").value;

    if (uploadForm) {
        // Extraer el ID del producto del atributo `data-product-id`
        const productoId = uploadForm.getAttribute("data-product-id");
        console.log(`ID del producto: ${productoId}`); // Imprimir en consola para depuración

        // Manejar la carga de imágenes
        uploadForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const formData = new FormData();
            const fileInput = document.getElementById("imagen-input");
            const isPrincipal = document.getElementById("es_principal");

            // Validar que se seleccionó una imagen
            if (fileInput.files.length === 0) {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: "Debes seleccionar una imagen para cargar.",
                });
                return;
            }

            // Agregar datos al FormData
            formData.append("imagen", fileInput.files[0]);
            formData.append("es_principal", isPrincipal.checked);
            formData.append("csrfmiddlewaretoken", csrfToken);

            console.log("Datos enviados al servidor:", {
                productoId: productoId,
                esPrincipal: isPrincipal.checked,
                archivo: fileInput.files[0].name,
            }); // Imprimir detalles de los datos

            fetch(`/Blyss/cargar-imagen/${productoId}/`, {
                method: "POST",
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        Swal.fire({
                            icon: "success",
                            title: "Éxito",
                            text: "Imagen cargada correctamente.",
                            timer: 2000,
                            showConfirmButton: false,
                        }).then(() => {
                            location.reload(); // Recargar la página para mostrar la nueva imagen
                        });
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: data.message,
                        });
                    }
                })
                .catch((error) => {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: `Error: ${error}`,
                    });
                });
        });
    }
});
