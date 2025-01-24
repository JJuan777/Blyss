document.addEventListener("DOMContentLoaded", function () {
    let currentPage = 1;
    let currentOrderBy = 'Nombre';
    let currentOrderDirection = 'asc';

    const categoriasTableBody = document.getElementById('categorias-table-body');
    const prevPageButton = document.getElementById('prev-page');
    const nextPageButton = document.getElementById('next-page');
    const paginationInfo = document.getElementById('pagination-info');
    const sortableHeaders = document.querySelectorAll('.sortable');

    // Función para cargar categorías dinámicamente
    function loadCategorias(page, orderBy, orderDirection) {
        fetch(`/Blyss/admin/inventario/obtener-categorias/?page=${page}&order_by=${orderBy}&order_direction=${orderDirection}`, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                if (data.categorias && data.categorias.length > 0) {
                    // Vacía la tabla y llena con nuevos datos
                    categoriasTableBody.innerHTML = '';
                    data.categorias.forEach(categoria => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${categoria.nombre}</td>
                            <td>${categoria.descripcion}</td>
                            <td class="text-center"><span class="badge ${categoria.estado === 'Activo' ? 'bg-success' : 'bg-danger'}">${categoria.estado}</span></td>
                            <td class="text-center">
                                <a href="/Blyss/admin/inventario/categorias/view/${categoria.id}/" class="btn btn-sm btn-info">
                                    <i class="bi bi-info-circle"></i>
                                </a>
                            </td>
                        `;
                        categoriasTableBody.appendChild(row);
                    });

                    // Actualiza los controles de paginación
                    currentPage = data.current_page;
                    paginationInfo.textContent = `Página ${data.current_page} de ${data.total_pages}`;
                    prevPageButton.disabled = !data.has_prev;
                    nextPageButton.disabled = !data.has_next;
                } else {
                    categoriasTableBody.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center">No hay categorías registradas.</td>
                        </tr>
                    `;
                    paginationInfo.textContent = '';
                    prevPageButton.disabled = true;
                    nextPageButton.disabled = true;
                }
            })
            .catch(error => {
                console.error('Error al cargar las categorías:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Hubo un problema al cargar las categorías.',
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

            loadCategorias(1, currentOrderBy, currentOrderDirection);
        });
    });

    // Listeners para los botones de paginación
    prevPageButton.addEventListener('click', function () {
        if (currentPage > 1) {
            loadCategorias(currentPage - 1, currentOrderBy, currentOrderDirection);
        }
    });

    nextPageButton.addEventListener('click', function () {
        loadCategorias(currentPage + 1, currentOrderBy, currentOrderDirection);
    });

    // Carga inicial
    loadCategorias(1, currentOrderBy, currentOrderDirection);
});
