const loginForm = document.getElementById("loginForm");
const bgContainer = document.getElementById("bgContainer");
const body = document.body;
const pageStage = document.querySelector(".page-stage");

if (loginForm && bgContainer) {
    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();
        bgContainer.classList.add("slide-right");

        // Keep animation smooth before navigating to dashboard.
        setTimeout(() => {
            loginForm.submit();
        }, 760);
    });
}

if (body) {
    window.requestAnimationFrame(() => {
        body.classList.remove("page-preload");
        body.classList.add("page-ready");
    });
}

function animatePageExit(callback) {
    if (!body || !pageStage) {
        callback();
        return;
    }
    body.classList.add("page-leaving");
    setTimeout(callback, 280);
}

document.querySelectorAll("[data-nav-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
        const href = link.getAttribute("href");
        if (!href || href.startsWith("#")) {
            return;
        }
        event.preventDefault();
        animatePageExit(() => {
            window.location.href = href;
        });
    });
});

document.querySelectorAll("form[data-animate-submit]").forEach((form) => {
    form.addEventListener("submit", (event) => {
        if (form.dataset.submitting === "true") {
            return;
        }
        if (form.hasAttribute("data-no-exit-animation")) {
            return;
        }
        event.preventDefault();
        form.dataset.submitting = "true";
        animatePageExit(() => {
            form.submit();
        });
    });
});
