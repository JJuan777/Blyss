document.addEventListener("DOMContentLoaded", function () {
    const favoritoButton = document.querySelector(".favorito-btn");

    favoritoButton.addEventListener("click", function (event) {
        event.preventDefault();

        const productoId = favoritoButton.dataset.productoId;

        fetch("/Blyss/favoritos/toggle/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: `producto_id=${productoId}`
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const icon = favoritoButton.querySelector("i");

                    if (data.favorito) {
                        // Cambiar a "En favoritos"
                        icon.classList.remove("bi-heart", "text-muted");
                        icon.classList.add("bi-heart-fill", "text-danger");
                        favoritoButton.setAttribute("title", "Eliminar de favoritos");
                    } else {
                        // Cambiar a "No en favoritos"
                        icon.classList.remove("bi-heart-fill", "text-danger");
                        icon.classList.add("bi-heart", "text-muted");
                        favoritoButton.setAttribute("title", "Añadir a favoritos");
                    }
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Ocurrió un error al procesar la solicitud.");
            });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
