document.getElementById("checkout-btn").addEventListener("click", function() {
    var modal = new bootstrap.Modal(document.getElementById("modalPago"));
    modal.show();
});

async function procesarPago(metodo) {
    try {
        // Obtener la dirección seleccionada
        let direccionSeleccionada = document.querySelector('input[name="direccion"]:checked');
        if (!direccionSeleccionada) {
            Swal.fire("Error", "Por favor, selecciona una dirección de envío.", "error");
            return;
        }

        const response = await fetch("/Blyss/procesar-compra/", {
            method: "POST",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ 
                metodo_pago: metodo,
                direccion_id: direccionSeleccionada.value  // Enviar la dirección seleccionada
            })
        });

        if (!response.ok) {
            throw new Error(`Error en la petición: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            Swal.fire("Pago realizado", "Tu pago ha sido procesado con éxito.", "success").then(() => {
                window.location.href = "/Blyss/pedidos/";
            });
        } else {
            Swal.fire("Error", data.message, "error");
        }
    } catch (error) {
        Swal.fire("Error inesperado", error.message, "error");
    }
}

document.getElementById("pago-tarjeta").addEventListener("submit", function(event) {
    event.preventDefault();
    Swal.fire({
        title: "Procesando pago...",
        text: "Por favor, espera un momento.",
        icon: "info",
        showConfirmButton: false,
        timer: 2000,
        didOpen: () => Swal.showLoading()
    }).then(() => {
        procesarPago("Tarjeta de Crédito");
    });
});

document.getElementById("pagar-paypal").addEventListener("click", function() {
    Swal.fire({
        title: "Redirigiendo a PayPal...",
        text: "Por favor, espera mientras te dirigimos al sitio de PayPal.",
        icon: "info",
        showConfirmButton: false,
        timer: 2000,
        didOpen: () => Swal.showLoading()
    }).then(() => {
        procesarPago("PayPal");
    });
});
