document.addEventListener("DOMContentLoaded", function () {
  const lotteryField = document.getElementById("id_lottery");
  const ticketsField = document.getElementById("id_individual_tickets");

  if (!lotteryField || !ticketsField) return;

  lotteryField.onchange = function () {
    const lotteryId = this.value;
    if (lotteryId) {
      if (ticketsField) {
        const url = `/api/get_tickets_to_assign?lottery_id=${lotteryId}`;
        fetch(url)
          .then((response) => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then((data) => {
            ticketsField.innerHTML = ""; // Clear previous options
            data.forEach((ticket) => {
              const option = document.createElement("option");
              option.value = ticket.id;
              option.textContent = ticket.number;
              ticketsField.appendChild(option);
            });
          })
          .catch((error) => {
            console.error("Error fetching tickets:", error);
          });
      }
    } else {
      ticketsField.innerHTML = ""; // Clear options if no lottery is selected
    }
  };
});
