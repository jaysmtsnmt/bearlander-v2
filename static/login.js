const form = document.getElementById("form-login")
const button = document.getElementById("input-submit")

form.addEventListener("submit", () => {
    button.disabled = true;
    button.classList.add("loading");
    button.querySelector(".btn-text").textContent = "Logging In...";
});