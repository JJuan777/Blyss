document.addEventListener("DOMContentLoaded", function () {
    let currentPage = 1;
    let currentOrderBy = 'Nombre';
    let currentOrderDirection = 'asc';

    const productosTableBody = document.getElementById('productos-table-body');
    const prevPageButton = document.getElementById('prev-page');
    const nextPageButton = document.getElementById('next-page');
    const paginationInfo = document.getElementById('pagination-info');
    const sortableHeaders = document.querySelectorAll('.sortable');

    // Función para cargar productos dinámicamente
    function loadProductos(page, orderBy, orderDirection) {
        fetch(`/Blyss/admin/inventario/obtener-productos/?page=${page}&order_by=${orderBy}&order_direction=${orderDirection}`, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                if (data.productos && data.productos.length > 0) {
                    // Vacía la tabla y llena con nuevos datos
                    productosTableBody.innerHTML = '';
                    data.productos.forEach(producto => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${producto.nombre}</td>
                            <td>${producto.sku}</td>
                            <td>${producto.stock}</td>
                            <td>${producto.precio}</td>
                            <td>${producto.marca}</td>
                            <td class="text-center"><span class="badge ${producto.estado === 'Activo' ? 'bg-success' : 'bg-danger'}">${producto.estado}</span></td>
                            <td class="text-center">
                            <a href="/Blyss/admin/inventario/productos/view/${producto.IdProducto}/" class="btn btn-sm btn-info">
                                <i class="bi bi-info-circle"></i>
                            </a>
                            </td>
                        `;
                        productosTableBody.appendChild(row);
                    });

                    // Actualiza los controles de paginación
                    currentPage = data.current_page;
                    paginationInfo.textContent = `Página ${data.current_page} de ${data.total_pages}`;
                    prevPageButton.disabled = !data.has_prev;
                    nextPageButton.disabled = !data.has_next;
                } else {
                    productosTableBody.innerHTML = `
                        <tr>
                            <td colspan="7" class="text-center">No hay productos registrados.</td>
                        </tr>
                    `;
                    paginationInfo.textContent = '';
                    prevPageButton.disabled = true;
                    nextPageButton.disabled = true;
                }
            })
            .catch(error => {
                console.error('Error al cargar los productos:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Hubo un problema al cargar los productos.',
                });
            });
    }

    // Listener para las cabeceras de ordenación
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function () {
            const orderBy = this.getAttribute('data-order-by');

            // Alternar la dirección de orden
            if (currentOrderBy === orderBy) {
                currentOrderDirection = currentOrderDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentOrderBy = orderBy;
                currentOrderDirection = 'asc';
            }

            // Actualizar las flechas de dirección
            document.querySelectorAll('.sort-icon').forEach(icon => icon.textContent = '↑');
            this.querySelector('.sort-icon').textContent = currentOrderDirection === 'asc' ? '↑' : '↓';

            loadProductos(1, currentOrderBy, currentOrderDirection);
        });
    });

    // Listeners para los botones de paginación
    prevPageButton.addEventListener('click', function () {
        if (currentPage > 1) {
            loadProductos(currentPage - 1, currentOrderBy, currentOrderDirection);
        }
    });

    nextPageButton.addEventListener('click', function () {
        loadProductos(currentPage + 1, currentOrderBy, currentOrderDirection);
    });

    // Carga inicial
    loadProductos(1, currentOrderBy, currentOrderDirection);
});
