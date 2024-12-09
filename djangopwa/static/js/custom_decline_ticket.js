const createDeclineTicketModal = () => {
  return `
        <style>
            .decline-modal-content {
                font-family: sans-serif;
                border-radius: 0.5rem;
            }

            .decline-modal-button {
                border: 0px;
                padding: 4px 1rem;
                color: white;
                border-radius: 1rem;
                font-wei
            }

            .decline-button-accept {
                background-color: #3294ff;
            }

            .decline-button-cancel {
                background-color: #899196;
                color: white;
            }

        </style>
        <div id="confirmationModal" style="position: fixed; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center;" onclick="closeModal(event)">
            <div class="decline-modal-content" style="background: white; padding: 20px; border: 1px solid #ccc; text-align: center;" onclick="event.stopPropagation();">
                <span onclick="closeModal()" style="cursor: pointer; float: right;">&times;</span>
                <p> Se declinará la compra y se pondrá nuevamente disponible </p>
                <p> ¿Desea proceder? </p>
                <button class="decline-modal-button decline-button-accept" id="confirmDecline">Si</button>
                <button class="decline-modal-button decline-button-cancel" onclick="closeModal()">Cancelar</button>
            </div>
        </div>
    `;
};

const closeModal = (event) => {
  const modal = document.getElementById("confirmationModal");
  if (modal) {
    document.body.removeChild(modal);
  }
};

const performRequestDeclineTicket = (client_id) =>
  fetch(`/api/decline_ticket/${client_id}`);

const handleDecline = async (client_id) => {
  const response = await performRequestDeclineTicket(client_id);
  const data = await response.json();
  closeModal();
  location.reload()
};

const declineTicket = (client_id) => {
  document.body.insertAdjacentHTML("beforeend", createDeclineTicketModal());
  document.getElementById("confirmDecline").onclick = () =>
    handleDecline(client_id);
};
