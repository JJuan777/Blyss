document.addEventListener("DOMContentLoaded", function () {
    const updateTotals = () => {
        let subtotal = 0;
        let totalDescuento = 0;
        let totalPagar = 0;
        let totalItems = 0;

        document.querySelectorAll(".carrito-item").forEach(item => {
            const precioOriginalElement = item.querySelector(".text-decoration-line-through");
            const precioDescuentoElement = item.querySelector(".text-danger");
            const cantidadElement = item.querySelector(".cantidad-input");
            const cantidad = parseInt(cantidadElement.value);

            const precioOriginal = precioOriginalElement ? parseFloat(precioOriginalElement.textContent.replace("$", "").replace(",", "")) : 0;
            const precioDescuento = precioDescuentoElement ? parseFloat(precioDescuentoElement.textContent.replace("$", "").replace(",", "")) : 0;

            subtotal += precioOriginal * cantidad;
            totalPagar += precioDescuento * cantidad;
            totalDescuento += (precioOriginal - precioDescuento) * cantidad;
            totalItems += cantidad;
        });

        document.getElementById("subtotal").textContent = `$${subtotal.toLocaleString()}`;
        document.getElementById("descuento").textContent = `-$${totalDescuento.toLocaleString()}`;
        document.getElementById("total").textContent = `$${totalPagar.toLocaleString()}`;

        // ✅ Actualizar el contador del carrito en la barra de navegación
        actualizarContadorCarrito(totalItems);
    };

    // ✅ Incrementar la cantidad de productos
    document.querySelectorAll(".increase-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const input = this.previousElementSibling;
            let cantidad = parseInt(input.value);
            const max = parseInt(input.max);
            if (cantidad < max) {
                input.value = cantidad + 1;
                updateTotals();
            } else {
                Swal.fire({
                    title: "Stock máximo alcanzado",
                    text: "No puedes agregar más cantidad de este producto.",
                    icon: "warning",
                    toast: true,
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 2000
                });
            }
        });
    });

    // ✅ Disminuir la cantidad de productos
    document.querySelectorAll(".decrease-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const input = this.nextElementSibling;
            let cantidad = parseInt(input.value);
            if (cantidad > 1) {
                input.value = cantidad - 1;
                updateTotals();
            }
        });
    });

    // ✅ Eliminar un producto del carrito
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const productoId = this.getAttribute("data-producto-id");
            const rowElement = this.closest(".carrito-item");
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            Swal.fire({
                title: "¿Eliminar producto?",
                text: "Este producto será eliminado del carrito.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/Blyss/carrito/eliminar/${productoId}/`, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrfToken,
                            "Content-Type": "application/json"
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            rowElement.remove();
                            updateTotals();
                            Swal.fire({
                                title: "Eliminado",
                                text: "El producto ha sido eliminado del carrito.",
                                icon: "success",
                                toast: true,
                                position: "top-end",
                                showConfirmButton: false,
                                timer: 2500,
                                timerProgressBar: true
                            });
                        } else {
                            Swal.fire({
                                title: "Error",
                                text: "No se pudo eliminar el producto.",
                                icon: "error",
                                toast: true,
                                position: "top-end",
                                showConfirmButton: false,
                                timer: 2500
                            });
                        }
                    })
                    .catch(error => console.error("Error:", error));
                }
            });
        });
    });

    // ✅ Función para actualizar dinámicamente el contador del carrito
    function actualizarContadorCarrito(totalItems = null) {
        if (totalItems === null) {
            fetch("/Blyss/carrito/total/")
                .then(response => response.json())
                .then(data => {
                    mostrarContador(data.total_items);
                })
                .catch(error => console.error("Error al actualizar el carrito:", error));
        } else {
            mostrarContador(totalItems);
        }
    }

    function mostrarContador(totalItems) {
        const cartCounter = document.getElementById("cart-counter");
        if (totalItems > 0) {
            cartCounter.textContent = totalItems;
            cartCounter.style.display = "inline-block";
        } else {
            cartCounter.style.display = "none";
        }
    }

    updateTotals();
});
