document.getElementById("loginForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(this);

    fetch("", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                // Muestra un mensaje de éxito con SweetAlert2
                Swal.fire({
                    icon: "success",
                    title: "¡Éxito!",
                    text: data.message,
                    showConfirmButton: false,
                    timer: 2000,
                    toast: true,
                    position: "top-right",
                });

                setTimeout(() => {
                    window.location.href = "/Blyss"; // Redirige al inicio tras el login exitoso
                }, 500);
            } else {
                // Muestra un mensaje de error con SweetAlert2
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: data.message,
                    showConfirmButton: false,
                    timer: 3000,
                    toast: true,
                    position: "top-right",
                });
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            // Muestra un mensaje de error genérico con SweetAlert2
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "Ocurrió un error. Inténtalo de nuevo.",
                showConfirmButton: false,
                timer: 3000,
                toast: true,
                position: "top-right",
            });
        });
});
