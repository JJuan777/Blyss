document.addEventListener("DOMContentLoaded", function () {
    const searchResults = document.getElementById("search-results");
    const loader = document.getElementById("loading");
    const orderSelect = document.getElementById("order-select");

    let offset = 0; // Empezamos desde 0
    let loading = false;
    let query = new URLSearchParams(window.location.search).get("q") || "";
    let order = new URLSearchParams(window.location.search).get("order") || "asc";
    let hayMas = true;

    function loadMoreProducts(reset = false) {
        if (loading || !hayMas) return;
        loading = true;
        loader.style.display = "block";

        if (reset) {
            offset = 0; // Reiniciar la paginación al filtrar
            searchResults.innerHTML = ""; // Limpiar productos antes de volver a cargar
            hayMas = true; // Resetear la bandera de paginación
        }

        fetch(`/Blyss/Search/?q=${encodeURIComponent(query)}&order=${order}&offset=${offset}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(response => response.json())
        .then(data => {
            if (data.productos.length === 0) {
                hayMas = false; // No hay más productos, detener futuras solicitudes
                loader.style.display = "none";
                return;
            }

            data.productos.forEach(producto => {
                let imageUrl = producto.imagen ? producto.imagen : "/static/images/default-product.jpg";
                let precioHTML = "";
            
                if (producto.precio_descuento && producto.precio_descuento > 0) {
                    let porcentajeDescuento = Math.round(100 - (producto.precio_descuento / producto.precio) * 100);
            
                    precioHTML = `
                        <div class="d-flex align-items-center">
                            <span class="text-danger fw-bold fs-5">$${producto.precio_descuento.toFixed(2)}</span>
                            <span class="badge bg-success ms-2 p-2">En oferta</span>
                        </div>
                        <div class="text-muted fw-normal" style="font-size: 1rem; text-decoration: line-through;">
                            Antes: $${producto.precio.toFixed(2)}
                        </div>
                        ${porcentajeDescuento > 0 ? `<div class="text-danger fw-bold mt-1" style="font-size: 1rem;">
                            Ahorra ${porcentajeDescuento}%
                        </div>` : ""}
                    `;
                } else {
                    precioHTML = `<span class="text-success fw-bold fs-5">$${producto.precio.toFixed(2)}</span>`;
                }
            
                let productHTML = `
                    <div class="col-md-4 mb-4 producto-item">
                        <div class="card h-100 shadow-lg border-0 rounded-3">
                            <div class="image-container">
                                <img src="${imageUrl}" class="card-img-top product-image" alt="${producto.nombre}">
                            </div>
                            <div class="card-body d-flex flex-column">
                                <h5 class="card-title text-primary mb-2">
                                    <a href="/Blyss/view/${producto.id}/" class="text-decoration-none text-primary fw-bold">
                                        ${producto.nombre}
                                    </a>
                                </h5>
                                <p class="text-muted mb-1"><i class="bi bi-shop"></i> Marca: <span class="fw-semibold">${producto.marca}</span></p>
                                <div class="mb-3">${precioHTML}</div>
                                <div class="mt-auto">

                                </div>
                            </div>
                        </div>
                    </div>
                `;
                searchResults.insertAdjacentHTML("beforeend", productHTML);
            });
            

            offset += data.productos.length; // Ahora sumamos la cantidad de productos devueltos
            hayMas = data.hay_mas; // Si ya no hay más productos, se detiene el scroll infinito
            loading = false;
            loader.style.display = "none";
        })
        .catch(error => {
            console.error("Error en la carga de productos:", error);
            loading = false;
            loader.style.display = "none";
        });
    }

    // Cargar productos al hacer scroll
    window.addEventListener("scroll", function () {
        if (hayMas && window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            loadMoreProducts();
        }
    });

    // Cambiar orden dinámicamente
    orderSelect.addEventListener("change", function () {
        order = this.value;
        offset = 0;
        hayMas = true;
        searchResults.innerHTML = ""; // Limpiar productos antes de recargar
        loadMoreProducts(true);
    });

    // Cargar los primeros productos al cargar la página
    loadMoreProducts();
});
