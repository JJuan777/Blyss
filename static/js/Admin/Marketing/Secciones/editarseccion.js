document.addEventListener("DOMContentLoaded", function () {
    const editButton = document.getElementById("editButton");
    const saveButton = document.getElementById("saveButton");

    const tituloText = document.getElementById("tituloText");
    const tituloInput = document.getElementById("tituloInput");

    const editableTexts = document.querySelectorAll(".editable-text");
    const editableSelects = document.querySelectorAll(".editable-select");

    const imageUploadContainer = document.getElementById("imageUploadContainer");
    const imageInput = document.getElementById("imageInput");
    const imagePreview = document.getElementById("imagePreview");

    const seccionId = document.getElementById("seccionId").value;

    editButton.addEventListener("click", function () {
        // Ocultar botón de edición y mostrar guardar
        editButton.classList.add("d-none");
        saveButton.classList.remove("d-none");

        // Mostrar inputs editables
        tituloText.classList.add("d-none");
        tituloInput.classList.remove("d-none");

        editableTexts.forEach(text => text.classList.add("d-none"));
        editableSelects.forEach(select => select.classList.remove("d-none"));

        // Mostrar el input de carga de imagen
        imageUploadContainer.classList.remove("d-none");
    });

    // Vista previa de imagen
    imageInput.addEventListener("change", function () {
        const file = imageInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    saveButton.addEventListener("click", function () {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

        if (!csrfToken) {
            Swal.fire("Error", "No se encontró el CSRF token.", "error");
            return;
        }

        // Obtener datos
        const titulo = tituloInput.value;
        const producto1 = document.getElementById("producto1Select").value;
        const producto2 = document.getElementById("producto2Select").value;
        const producto3 = document.getElementById("producto3Select").value;
        const producto4 = document.getElementById("producto4Select").value;

        const formData = new FormData();
        formData.append("titulo", titulo);
        formData.append("producto1", producto1);
        formData.append("producto2", producto2);
        formData.append("producto3", producto3);
        formData.append("producto4", producto4);

        if (imageInput.files[0]) {
            formData.append("imagen", imageInput.files[0]);
        }

        fetch(`/Blyss/admin/marketing/secciones/update/${seccionId}/`, {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire("Éxito", "Sección actualizada correctamente", "success").then(() => {
                    location.reload();
                });
            } else {
                Swal.fire("Error", "Hubo un problema al actualizar: " + data.error, "error");
            }
        })
        .catch(error => console.error("Error:", error));
    });
});
