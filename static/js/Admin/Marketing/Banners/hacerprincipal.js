document.addEventListener("DOMContentLoaded", function () {
    // Obtener token CSRF
    const csrfToken = document.getElementById("csrf_token").value;

    // Evento para hacer un banner principal
    document.querySelectorAll(".make-principal").forEach(button => {
        button.addEventListener("click", function () {
            const bannerId = this.getAttribute("data-id");
            
            fetch("/Blyss/banners/hacer-principal/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ banner_id: bannerId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload(); // Recargar la página para reflejar los cambios
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });
});
