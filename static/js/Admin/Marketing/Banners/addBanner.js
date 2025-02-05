document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.getElementById("imageInput");
    const imagePreview = document.getElementById("imagePreview");
    const bannerForm = document.getElementById("bannerForm");
    const bannerUrlInput = document.getElementById("bannerUrl");

    // Formatos permitidos
    const validImageTypes = ["image/jpeg", "image/png", "image/webp"];

    // Vista previa de la imagen
    imageInput.addEventListener("change", function () {
        const file = this.files[0];

        if (file) {
            // Validar formato de imagen
            if (!validImageTypes.includes(file.type)) {
                Swal.fire({
                    icon: "warning",
                    title: "Formato no válido",
                    text: "Solo se permiten imágenes en formato JPG, PNG o WEBP.",
                });
                this.value = ""; // Reiniciar input
                imagePreview.innerHTML = `<span class="text-muted">Vista previa</span>`;
                return;
            }

            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" style="max-height: 200px;">`;
            };
            reader.readAsDataURL(file);
        }
    });

    // Validación de URL (opcional)
    bannerUrlInput.addEventListener("input", function () {
        const urlPattern = /^(https?:\/\/)?([\w-]+\.)+[\w-]{2,}(\/[\w-]*)*$/;
        if (this.value.trim() !== "" && !urlPattern.test(this.value)) {
            this.classList.add("is-invalid");
        } else {
            this.classList.remove("is-invalid");
        }
    });

    // Enviar formulario por AJAX con SweetAlert2
    bannerForm.addEventListener("submit", function (event) {
        event.preventDefault();

        // Validar que se haya seleccionado una imagen
        if (!imageInput.files.length) {
            Swal.fire({
                icon: "error",
                title: "Imagen requerida",
                text: "Debes seleccionar una imagen para subir.",
            });
            return;
        }

        // Validar URL si se ha ingresado
        const urlValue = bannerUrlInput.value.trim();
        const urlPattern = /^(https?:\/\/)?([\w-]+\.)+[\w-]{2,}(\/[\w-]*)*$/;
        if (urlValue !== "" && !urlPattern.test(urlValue)) {
            Swal.fire({
                icon: "error",
                title: "URL inválida",
                text: "Introduce una URL válida o deja el campo vacío.",
            });
            return;
        }

        const formData = new FormData(this);
        formData.append("csrfmiddlewaretoken", document.querySelector("[name=csrfmiddlewaretoken]").value);

        // Mostrar un loading mientras se procesa
        Swal.fire({
            title: "Subiendo...",
            text: "Por favor, espera mientras se sube el banner.",
            allowOutsideClick: false,
            allowEscapeKey: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        fetch("/Blyss/admin/marketing/banners/agregar/", {
            method: "POST",
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: "success",
                    title: "¡Éxito!",
                    text: data.message,
                    timer: 3000,
                    showConfirmButton: false
                });

                bannerForm.reset();
                imagePreview.innerHTML = `<span class="text-muted">Vista previa</span>`;
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: data.message
                });
            }
        })
        .catch(error => {
            console.error("Error al subir el banner:", error);
            Swal.fire({
                icon: "error",
                title: "Error al subir el banner",
                text: "Hubo un problema con la subida. Inténtalo de nuevo."
            });
        });
    });
});
