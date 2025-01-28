document.addEventListener("DOMContentLoaded", function () {
    const mainImage = document.getElementById("main-image");
    const thumbnailsContainer = document.getElementById("thumbnails-container");
    const thumbnails = document.querySelectorAll(".thumbnail-image");
    const upArrow = document.getElementById("up-arrow");
    const downArrow = document.getElementById("down-arrow");

    let currentOffset = 0; // Mantiene el desplazamiento actual
    const thumbnailHeight = 110; // Altura de cada miniatura (incluyendo margen)
    const maxVisible = 4; // Número máximo de miniaturas visibles
    const totalThumbnails = thumbnails.length;
    const maxOffset = (totalThumbnails - maxVisible) * thumbnailHeight;

    // Cambiar la imagen principal al pasar el cursor sobre una miniatura
    thumbnails.forEach((thumbnail) => {
        thumbnail.addEventListener("mouseenter", () => {
            mainImage.src = thumbnail.dataset.src;

            // Resaltar miniatura seleccionada
            thumbnails.forEach((thumb) => thumb.classList.remove("selected-thumbnail"));
            thumbnail.classList.add("selected-thumbnail");
        });
    });

    // Mover hacia arriba al pasar el cursor sobre la flecha de arriba
    upArrow.addEventListener("mouseenter", () => {
        const interval = setInterval(() => {
            if (currentOffset > 0) {
                currentOffset -= thumbnailHeight;
                thumbnailsContainer.style.transform = `translateY(-${currentOffset}px)`;
            } else {
                clearInterval(interval);
            }
        }, 200);

        // Detener el desplazamiento cuando se salga de la flecha
        upArrow.addEventListener("mouseleave", () => clearInterval(interval), { once: true });
    });

    // Mover hacia abajo al pasar el cursor sobre la flecha de abajo
    downArrow.addEventListener("mouseenter", () => {
        const interval = setInterval(() => {
            if (currentOffset < maxOffset) {
                currentOffset += thumbnailHeight;
                thumbnailsContainer.style.transform = `translateY(-${currentOffset}px)`;
            } else {
                clearInterval(interval);
            }
        }, 200);

        // Detener el desplazamiento cuando se salga de la flecha
        downArrow.addEventListener("mouseleave", () => clearInterval(interval), { once: true });
    });
});


