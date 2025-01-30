document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".toggle-favorito").forEach(button => {
        button.addEventListener("click", function () {
            let productoId = this.getAttribute("data-producto-id");
            let icono = this.querySelector("i");
            let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value; // Obtener CSRF desde el input

            fetch("/Blyss/favoritos/toggle/", {  // Verifica que esta URL es correcta en tu `urls.py`
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `producto_id=${productoId}`
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    if (data.favorito) {
                        icono.classList.remove("bi-heart");
                        icono.classList.add("bi-heart-fill", "text-danger");
                        button.setAttribute("title", "Eliminar de favoritos");
                    } else {
                        icono.classList.remove("bi-heart-fill", "text-danger");
                        icono.classList.add("bi-heart", "text-muted");
                        button.setAttribute("title", "Añadir a favoritos");
                    }
                } else {
                    alert(data.message);
                }
            })
            .catch(error => console.error("Error en la solicitud AJAX:", error));
        });
    });
});
