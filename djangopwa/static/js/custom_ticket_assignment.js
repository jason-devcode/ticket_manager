const changeTextAddTicketAssignmentButton = () => {
    const button = document.querySelector('[href="/admin/djangopwa/ticketassignment/add/"]');
    if(button) button.innerHTML = button.innerHTML.replace('Añadir Asignar boleta', 'Asignar boletas');
}

document.addEventListener('DOMContentLoaded', () => {
    changeTextAddTicketAssignmentButton();
});
