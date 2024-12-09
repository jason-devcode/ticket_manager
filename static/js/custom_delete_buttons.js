(function () {
  document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll("a.btn.btn-danger.form-control");
    if (links.length > 0) {
      const deleteButton = links[0];
      deleteButton.style.display = "none";
    }
  });
})();
