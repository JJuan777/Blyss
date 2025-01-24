document.addEventListener("DOMContentLoaded", function () {
    let currentPage = 1;
    let currentOrderBy = 'Nombre';
    let currentOrderDirection = 'asc';

    const subcategoriasTableBody = document.getElementById('subcategorias-table-body');
    const prevPageButton = document.getElementById('prev-page');
    const nextPageButton = document.getElementById('next-page');
    const paginationInfo = document.getElementById('pagination-info');
    const sortableHeaders = document.querySelectorAll('.sortable');

    // Función para cargar subcategorías dinámicamente
    function loadSubcategorias(page, orderBy, orderDirection) {
        fetch(`/Blyss/admin/inventario/obtener-subcategorias/?page=${page}&order_by=${orderBy}&order_direction=${orderDirection}`, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                if (data.subcategorias && data.subcategorias.length > 0) {
                    // Vacía la tabla y llena con nuevos datos
                    subcategoriasTableBody.innerHTML = '';
                    data.subcategorias.forEach(subcategoria => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${subcategoria.nombre}</td>
                            <td>${subcategoria.descripcion}</td>
                            <td class="text-center"><span class="badge ${subcategoria.estado === 'Activo' ? 'bg-success' : 'bg-danger'}">${subcategoria.estado}</span></td>
                            <td class="text-center">
                                <a href="/Blyss/admin/inventario/subcategorias/view/${subcategoria.id}/" class="btn btn-sm btn-info">
                                    <i class="bi bi-info-circle"></i>
                                </a>
                            </td>
                        `;
                        subcategoriasTableBody.appendChild(row);
                    });

                    // Actualiza los controles de paginación
                    currentPage = data.current_page;
                    paginationInfo.textContent = `Página ${data.current_page} de ${data.total_pages}`;
                    prevPageButton.disabled = !data.has_prev;
                    nextPageButton.disabled = !data.has_next;
                } else {
                    subcategoriasTableBody.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center">No hay subcategorías registradas.</td>
                        </tr>
                    `;
                    paginationInfo.textContent = '';
                    prevPageButton.disabled = true;
                    nextPageButton.disabled = true;
                }
            })
            .catch(error => {
                console.error('Error al cargar las subcategorías:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Hubo un problema al cargar las subcategorías.',
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

            loadSubcategorias(1, currentOrderBy, currentOrderDirection);
        });
    });

    // Listeners para los botones de paginación
    prevPageButton.addEventListener('click', function () {
        if (currentPage > 1) {
            loadSubcategorias(currentPage - 1, currentOrderBy, currentOrderDirection);
        }
    });

    nextPageButton.addEventListener('click', function () {
        loadSubcategorias(currentPage + 1, currentOrderBy, currentOrderDirection);
    });

    // Carga inicial
    loadSubcategorias(1, currentOrderBy, currentOrderDirection);
});
