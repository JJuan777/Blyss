// Checar y limitar existencias de producto en el carrito
document.addEventListener("DOMContentLoaded", function () {
    const decreaseBtn = document.getElementById("decrease-btn");
    const increaseBtn = document.getElementById("increase-btn");
    const cantidadInput = document.getElementById("cantidad");
    const maxStock = parseInt(cantidadInput.max);

    // Disminuir cantidad
    decreaseBtn.addEventListener("click", () => {
        let currentValue = parseInt(cantidadInput.value);
        if (currentValue > 1) {
            cantidadInput.value = currentValue - 1;
        }
    });

    // Aumentar cantidad
    increaseBtn.addEventListener("click", () => {
        let currentValue = parseInt(cantidadInput.value);
        if (currentValue < maxStock) {
            cantidadInput.value = currentValue + 1;
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const addToCartBtn = document.getElementById("add-to-cart-btn");
    const cantidadInput = document.getElementById("cantidad");
    const goToCartBtnContainer = document.getElementById("go-to-cart-btn-container");

    // Verifica si existe carrito al cargar la página
    if (tieneCarrito) {
        mostrarBotonCarrito();
    }

    // Evento para añadir al carrito
    addToCartBtn.addEventListener("click", function (event) {
        event.preventDefault();

        const productoId = addToCartBtn.dataset.productoId; // Obtén el ID del producto
        const cantidad = parseInt(cantidadInput.value); // Obtén la cantidad seleccionada

        fetch("/Blyss/carrito/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken") // Incluye el token CSRF
            },
            body: `producto_id=${productoId}&cantidad=${cantidad}` // Envía el producto y cantidad
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mostrar toast de éxito
                    Swal.fire({
                        toast: true,
                        icon: 'success',
                        title: data.message,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 3000,
                        timerProgressBar: true
                    });

                    // Agregar botón "Ir al Carrito" si no existe
                    mostrarBotonCarrito();
                } else {
                    // Mostrar toast de error
                    Swal.fire({
                        toast: true,
                        icon: 'error',
                        title: data.message,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 3000,
                        timerProgressBar: true
                    });
                }
            })
            .catch(error => {
                console.error("Error:", error);
                // Mostrar toast de error general
                Swal.fire({
                    toast: true,
                    icon: 'error',
                    title: 'Ocurrió un error al añadir al carrito.',
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true
                });
            });
    });

    // Función para mostrar el botón "Ir al Carrito"
    function mostrarBotonCarrito() {
        if (!document.getElementById("go-to-cart-btn")) {
            const goToCartBtn = document.createElement("a");
            goToCartBtn.id = "go-to-cart-btn";
            goToCartBtn.href = "/Blyss/carrito/"; // URL del carrito
            goToCartBtn.className = "btn btn-success btn-lg ms-3";
            goToCartBtn.innerHTML = `<i class="bi bi-cart"></i> Ir al Carrito`;
            goToCartBtnContainer.appendChild(goToCartBtn);
        }
    }

    // Función para obtener el token CSRF
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
