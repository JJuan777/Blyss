document.addEventListener("DOMContentLoaded", function () {
    const steps = {
        step1: document.getElementById("step-1"),
        step2: document.getElementById("step-2"),
        step3: document.getElementById("step-3"),
        step4: document.getElementById("step-4"),
    };

    const progressBar = document.getElementById("progress-bar");

    const buttons = {
        nextToStep2: document.getElementById("next-to-step-2"),
        nextToStep3: document.getElementById("next-to-step-3"),
        nextToStep4: document.getElementById("next-to-step-4"),
        backToStep1: document.getElementById("back-to-step-1"),
        backToStep2: document.getElementById("back-to-step-2"),
        backToStep3: document.getElementById("back-to-step-3"),
    };

    // Actualizar la barra de progreso
    function updateProgress(step) {
        const progress = {
            step1: { width: "25%", text: "Paso 1 de 4" },
            step2: { width: "50%", text: "Paso 2 de 4" },
            step3: { width: "75%", text: "Paso 3 de 4" },
            step4: { width: "100%", text: "Paso 4 de 4" },
        };

        progressBar.style.width = progress[step].width;
        progressBar.textContent = progress[step].text;
        progressBar.setAttribute("aria-valuenow", parseInt(progress[step].width));
    }

    // Mostrar y ocultar pasos
    function showStep(current, next, stepName) {
        current.style.display = "none";
        next.style.display = "block";
        updateProgress(stepName);
    }

    // Validar un campo individual
    function validateField(field) {
        if (field.value.trim() === "" || !field.checkValidity()) {
            field.classList.add("is-invalid");
            return false;
        }
        field.classList.remove("is-invalid");
        return true;
    }

    // Validar todos los campos de un paso
    function validateStep(step) {
        const inputs = step.querySelectorAll("input");
        let isValid = true;
        inputs.forEach((input) => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        return isValid;
    }

    // Botones "Continuar" y "Retroceder"
    buttons.nextToStep2.addEventListener("click", function () {
        if (validateStep(steps.step1)) {
            showStep(steps.step1, steps.step2, "step2");
        }
    });

    buttons.nextToStep3.addEventListener("click", function () {
        if (validateStep(steps.step2)) {
            showStep(steps.step2, steps.step3, "step3");
        }
    });

    buttons.nextToStep4.addEventListener("click", function () {
        if (validateStep(steps.step3)) {
            showStep(steps.step3, steps.step4, "step4");
        }
    });

    buttons.backToStep1.addEventListener("click", function () {
        showStep(steps.step2, steps.step1, "step1");
    });

    buttons.backToStep2.addEventListener("click", function () {
        showStep(steps.step3, steps.step2, "step2");
    });

    buttons.backToStep3.addEventListener("click", function () {
        showStep(steps.step4, steps.step3, "step3");
    });

    // Manejo del envío del formulario
    document.getElementById("registroForm").addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(this);

        fetch("", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    Swal.fire({
                        icon: "success",
                        title: "¡Registro Exitoso!",
                        text: data.message,
                        confirmButtonText: "Aceptar",
                    }).then(() => {
                        window.location.href = "/Blyss/login/";
                    });
                } else {
                    Swal.fire({
                        icon: "warning",
                        title: "Error",
                        text: data.message,
                        confirmButtonText: "Aceptar",
                    });
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                Swal.fire({
                    icon: "error",
                    title: "Error del Servidor",
                    text: "Ocurrió un error. Inténtalo de nuevo.",
                    confirmButtonText: "Aceptar",
                });
            });
    });
});
