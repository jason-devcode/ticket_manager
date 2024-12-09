document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const saveButton = document.querySelector('[name="_save"]');
        const deleteButton = document.querySelector('[class="inline-deletelink"]')

        if (saveButton && deleteButton) {
            const copySaveButton = saveButton.cloneNode(true);

            copySaveButton.className = "inline-savebuttonlink btn-success";

            const deleteButtonParent = deleteButton.parentNode;

            deleteButtonParent.replaceChild(copySaveButton, deleteButton);
        }
    }, 100);
})