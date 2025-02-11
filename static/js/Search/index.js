document.addEventListener("DOMContentLoaded", function () { 
    const searchResults = document.getElementById("search-results");
    const loader = document.getElementById("loading");
    const orderSelect = document.getElementById("order-select");
    const minPriceInput = document.getElementById("min-price");
    const maxPriceInput = document.getElementById("max-price");
    const applyFilterBtn = document.getElementById("apply-filter");
    const filterTags = document.getElementById("filter-tags");
    const priceRadios = document.querySelectorAll("input[name='price-range']");
    const ratingRadios = document.querySelectorAll("input[name='rating-filter']");

    let offset = 0;
    let loading = false;
    let query = new URLSearchParams(window.location.search).get("q") || "";
    let order = new URLSearchParams(window.location.search).get("order") || "asc";
    let minPrice = "";
    let maxPrice = "";
    let minRating = "";
    let hayMas = true;

    function updateFilterTags() {
        filterTags.innerHTML = "";

        let filterText = "";
        if (minPrice || maxPrice) {
            filterText += `Precio: ${minPrice ? `$${minPrice}` : ''} - ${maxPrice ? `$${maxPrice}` : ''}`;
        }
        if (minRating) {
            filterText += (filterText ? " | " : "") + `Calificación: ${minRating}★ o más`;
        }

        if (filterText) {
            let filterTag = `
                <span class="badge bg-primary p-2">
                    ${filterText}
                    <button id="reset-filter" class="btn-close btn-close-white ms-2" aria-label="Reset"></button>
                </span>
            `;
            filterTags.innerHTML = filterTag;

            document.getElementById("reset-filter").addEventListener("click", function () {
                resetFilters();
            });
        }
    }

    function resetFilters() {
        minPriceInput.value = "";
        maxPriceInput.value = "";
        minPrice = "";
        maxPrice = "";
        minRating = "";

        priceRadios.forEach(radio => radio.checked = false);
        ratingRadios.forEach(radio => radio.checked = false);

        offset = 0;
        hayMas = true;
        searchResults.innerHTML = "";
        updateFilterTags();
        loadMoreProducts(true);
    }

    function applyFilters() {
        minPrice = minPriceInput.value.trim();
        maxPrice = maxPriceInput.value.trim();
        offset = 0;
        hayMas = true;
        searchResults.innerHTML = "";
        updateFilterTags();
        loadMoreProducts(true);
    }

    function loadMoreProducts(reset = false) {
        if (loading || !hayMas) return;
        loading = true;
        loader.style.display = "block";

        if (reset) {
            offset = 0;
            searchResults.innerHTML = "";
            hayMas = true;
        }

        let url = `/Blyss/Search/?q=${encodeURIComponent(query)}&order=${order}&offset=${offset}`;
        if (minPrice) url += `&min_price=${minPrice}`;
        if (maxPrice) url += `&max_price=${maxPrice}`;
        if (minRating) url += `&min_rating=${minRating}`;

        fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
            .then(response => response.json())
            .then(data => {
                if (data.productos.length === 0) {
                    hayMas = false;
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
                            <div class="text-muted fw-normal" style="text-decoration: line-through;">
                                Antes: $${producto.precio.toFixed(2)}
                            </div>
                            ${porcentajeDescuento > 0 ? `<div class="text-danger fw-bold mt-1">Ahorra ${porcentajeDescuento}%</div>` : ""}
                        `;
                    } else {
                        precioHTML = `<span class="text-success fw-bold fs-5">$${producto.precio.toFixed(2)}</span>`;
                    }

                    let productHTML = `
                        <div class="col-md-4 mb-4">
                            <div class="card h-100 shadow-lg border-0 rounded-3">
                                <img src="${imageUrl}" class="card-img-top product-image" alt="${producto.nombre}">
                                <div class="card-body">
                                    <h5 class="card-title text-primary">
                                        <a href="/Blyss/view/${producto.id}/" class="text-decoration-none">${producto.nombre}</a>
                                    </h5>
                                    <p class="text-muted">Marca: <span class="fw-semibold">${producto.marca}</span></p>
                                    <p class="text-warning">⭐ ${producto.calificacion} / 5</p>
                                    <div>${precioHTML}</div>
                                </div>
                            </div>
                        </div>
                    `;
                    searchResults.insertAdjacentHTML("beforeend", productHTML);
                });

                offset += data.productos.length;
                hayMas = data.hay_mas;
                loading = false;
                loader.style.display = "none";
            })
            .catch(error => {
                console.error("Error en la carga de productos:", error);
                loading = false;
                loader.style.display = "none";
            });
    }

    applyFilterBtn.addEventListener("click", applyFilters);

    priceRadios.forEach(radio => {
        radio.addEventListener("change", function () {
            let [min, max] = this.value.split("-");
            minPriceInput.value = min || "";
            maxPriceInput.value = max || "";
            minPrice = min || "";
            maxPrice = max || "";
            applyFilters();
        });
    });

    ratingRadios.forEach(radio => {
        radio.addEventListener("change", function () {
            minRating = this.value;
            applyFilters();
        });
    });

    loadMoreProducts();
});
