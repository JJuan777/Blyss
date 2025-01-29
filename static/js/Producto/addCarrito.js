// ✅ Limitar la cantidad de productos seleccionados
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

// ✅ Añadir productos al carrito y actualizar contador dinámico
document.addEventListener("DOMContentLoaded", function () {
    const addToCartBtn = document.getElementById("add-to-cart-btn");
    const cantidadInput = document.getElementById("cantidad");
    const goToCartBtnContainer = document.getElementById("go-to-cart-btn-container");

    // Verifica si ya hay productos en el carrito
    if (tieneCarrito) {
        mostrarBotonCarrito();
    }

    // Evento para añadir al carrito
    addToCartBtn.addEventListener("click", function (event) {
        event.preventDefault();

        const productoId = addToCartBtn.dataset.productoId;
        const cantidad = parseInt(cantidadInput.value);

        fetch("/Blyss/carrito/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: `producto_id=${productoId}&cantidad=${cantidad}`
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // ✅ Mostrar alerta de éxito
                    Swal.fire({
                        toast: true,
                        icon: 'success',
                        title: data.message,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 3000,
                        timerProgressBar: true
                    });

                    // ✅ Agregar botón "Ir al Carrito"
                    mostrarBotonCarrito();

                    // ✅ Actualizar el contador del carrito dinámicamente
                    actualizarContadorCarrito();
                } else {
                    // ✅ Mostrar error si no se pudo agregar
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
                // ✅ Mostrar error general
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

    // ✅ Mostrar el botón "Ir al Carrito" dinámicamente
    function mostrarBotonCarrito() {
        if (!document.getElementById("go-to-cart-btn")) {
            const goToCartBtn = document.createElement("a");
            goToCartBtn.id = "go-to-cart-btn";
            goToCartBtn.href = "/Blyss/carrito/";
            goToCartBtn.className = "btn btn-success btn-lg ms-3";
            goToCartBtn.innerHTML = `<i class="bi bi-cart"></i> Ir al Carrito`;
            goToCartBtnContainer.appendChild(goToCartBtn);
        }
    }

    // ✅ Función para obtener el token CSRF
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

// ✅ Actualizar dinámicamente el contador del carrito en la barra de navegación
function actualizarContadorCarrito() {
    fetch("/Blyss/carrito/total/") // URL de la vista AJAX que obtiene el total de productos
        .then(response => response.json())
        .then(data => {
            const cartCounter = document.getElementById("cart-counter");
            if (data.total_items > 0) {
                cartCounter.textContent = data.total_items;
                cartCounter.style.display = "inline-block";  // Mostrar si hay productos
            } else {
                cartCounter.style.display = "none";  // Ocultar si el carrito está vacío
            }
        })
        .catch(error => console.error("Error al actualizar el carrito:", error));
}
