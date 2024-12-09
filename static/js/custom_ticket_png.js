const parseGenerationDate = (generationDate) => {
  const date = new Date(generationDate);

  // Get the date in YYYY-MM-DD format
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, "0"); // Months are 0-indexed
  const day = String(date.getUTCDate()).padStart(2, "0");

  // Adjust for Colombian time (UTC-5)
  const colombianHours = date.getUTCHours() - 5;
  const hours = String((colombianHours + 24) % 24).padStart(2, "0"); // Wrap around if negative
  const minutes = String(date.getUTCMinutes()).padStart(2, "0");
  const seconds = String(date.getUTCSeconds()).padStart(2, "0");

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

const createTicketElement = ({
  ticket_number,
  client_name_lastname,
  seller_name_lastname,
  date_generation,
  balance,
  amount_to_pay,
}) => {
  const ticketBody = document.createElement("div");
  ticketBody.style.height = "auto";
  ticketBody.style.margin = "2rem";

  const genDate = parseGenerationDate(date_generation);

  const bodyHtml = `
        <style>
            @media print {
                @page {
                    margin: 0;
                    size: auto; /* auto es el tamaño de la página según el contenido */
                }
                body {
                    margin: 1cm;
                }
                /* Esconde el nombre del dominio y la fecha */
                header, footer {
                    display: none;
                }
            }

            * {
                font-family: sans-serif;
            }

            .flex {
                display: flex;
                width: 100%;
            }

            .center-content {
                justify-content: center;
                align-items: center;
            }
            
            .justify-center {
                justify-content: center;
            }

            .items-center {
                align-items: center;
            }

            .end-content {
                justify-content: flex-end;
                align-items: flex-end;
            }

            .column-layout {
                flex-direction: column;
                width: 100%;
                height: 100%;
            }

            .logo {
                font-weight: bold;
                font-size: 4rem;
                padding: 4rem;
            }

            .ticket-info {
                width: min-content;
                gap: 1rem;
                align-items: center;
            }

            .ticket-label {
                white-space: nowrap;
                font-weight: 600; /* semibold */
                font-size: 2rem;
            }

            .ticket-number {
                display: flex;
                color: white;
                padding: 1rem 2rem;
                background-color: #6d9eeb;
                font-weight: bold;
                font-size: 2.5rem;
            }

            .receipt-message {
                color: gray;
                text-align: center;
            }
        </style>

        <div class="flex column-layout">
            <div class="flex">
                <div class="flex center-content">
                    <span class="logo">Logo</span>
                </div>
                <div class="flex end-content">
                    <div class="flex ticket-info">
                        <span class="ticket-label">N° BOLETA</span>
                        <div class="ticket-number">${ticket_number}</div>
                    </div>
                </div>
            </div>
            <div class="flex">
                <div class="flex center-content" style="width: 25%">
                    <span style="height: min-content; text-align: center; font-size: 1.5rem;">Fecha</span>
                </div>
                <div class="flex center-content" style="margin: 1rem 0px;">
                    <div class="flex">
                        <span style="text-align: center; font-size: 1.5rem;">${genDate}</span>
                    </div>
                    <div class="flex end-content">
                        <div class="flex ticket-info">
                            <span style="font-size: 1.5rem">ABONO</span>
                            <div style="background-color: #a4c0f3; padding: 4px 6rem; font-size: 2rem;" >$${balance}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="flex" style="justify-content: end;">
                <span style="font-size: 1.5rem">Saldo</span>
                <div style="padding: 4px 6rem; font-size: 2rem;" >$${amount_to_pay}</div>
            </div>
            <div class="flex">
                <div class="flex center-content" style="width: 25%">
                    <span style="height: min-content; text-align: center; font-size: 1.5rem;">CLIENTE</span>
                </div>
                <div class="flex center-content" style="margin: 1rem 0px; background-color: #cfe3f5;">
                        <span style="text-align: center; font-size: 1.5rem; padding: 8px;">${client_name_lastname}</span>
                </div>
            </div>
            <div class="flex">
                <div class="flex center-content" style="width: 25%">
                    <span style="height: min-content; text-align: center; font-size: 1.5rem;">ASESOR</span>
                </div>
                <div class="flex center-content" style="margin: 1rem 0px; background-color: #cfe3f5;">
                        <span style="text-align: center; font-size: 1.5rem; padding: 8px;">${seller_name_lastname}</span>
                </div>
            </div>
            <div class="flex">
                <p class="receipt-message">
                    Estos recibos son el comprobante digital de abonos parciales realizados por los clientes a nuestros asesores. Recuerda que para recibir tu BOLETA ORIGINAL, debe estar totalmente cancelada. Al solicitar este comprobante vía electrónica estás ayudando al medio ambiente.
                </p>
            </div>
        </div>
    `;

  ticketBody.innerHTML = bodyHtml;

  return ticketBody;
};

const createWhatsappButton = (client_whatsapp_url) => {
  const whatsappButton = document.createElement("a");
  whatsappButton.style.position = "fixed";
  whatsappButton.style.right = "20px";
  whatsappButton.style.bottom = "100px";
  whatsappButton.style.width = "3rem";
  whatsappButton.style.height = "3rem";
  whatsappButton.innerHTML = `
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 256 258"
    >
        <defs>
            <linearGradient id="logosWhatsappIcon0" x1="50%" x2="50%" y1="100%" y2="0%">
            <stop offset="0%" stop-color="#1faf38" />
            <stop offset="100%" stop-color="#60d669" />
            </linearGradient>
            <linearGradient id="logosWhatsappIcon1" x1="50%" x2="50%" y1="100%" y2="0%">
            <stop offset="0%" stop-color="#f9f9f9" />
            <stop offset="100%" stop-color="#fff" />
            </linearGradient>
        </defs>
        <path
            fill="url(#logosWhatsappIcon0)"
            d="M5.463 127.456c-.006 21.677 5.658 42.843 16.428 61.499L4.433 252.697l65.232-17.104a123 123 0 0 0 58.8 14.97h.054c67.815 0 123.018-55.183 123.047-123.01c.013-32.867-12.775-63.773-36.009-87.025c-23.23-23.25-54.125-36.061-87.043-36.076c-67.823 0-123.022 55.18-123.05 123.004"
        />
        <path
            fill="url(#logosWhatsappIcon1)"
            d="M1.07 127.416c-.007 22.457 5.86 44.38 17.014 63.704L0 257.147l67.571-17.717c18.618 10.151 39.58 15.503 60.91 15.511h.055c70.248 0 127.434-57.168 127.464-127.423c.012-34.048-13.236-66.065-37.3-90.15C194.633 13.286 162.633.014 128.536 0C58.276 0 1.099 57.16 1.071 127.416m40.24 60.376l-2.523-4.005c-10.606-16.864-16.204-36.352-16.196-56.363C22.614 69.029 70.138 21.52 128.576 21.52c28.3.012 54.896 11.044 74.9 31.06c20.003 20.018 31.01 46.628 31.003 74.93c-.026 58.395-47.551 105.91-105.943 105.91h-.042c-19.013-.01-37.66-5.116-53.922-14.765l-3.87-2.295l-40.098 10.513z"
        />
        <path
            fill="#fff"
            d="M96.678 74.148c-2.386-5.303-4.897-5.41-7.166-5.503c-1.858-.08-3.982-.074-6.104-.074c-2.124 0-5.575.799-8.492 3.984c-2.92 3.188-11.148 10.892-11.148 26.561s11.413 30.813 13.004 32.94c1.593 2.123 22.033 35.307 54.405 48.073c26.904 10.609 32.379 8.499 38.218 7.967c5.84-.53 18.844-7.702 21.497-15.139c2.655-7.436 2.655-13.81 1.859-15.142c-.796-1.327-2.92-2.124-6.105-3.716s-18.844-9.298-21.763-10.361c-2.92-1.062-5.043-1.592-7.167 1.597c-2.124 3.184-8.223 10.356-10.082 12.48c-1.857 2.129-3.716 2.394-6.9.801c-3.187-1.598-13.444-4.957-25.613-15.806c-9.468-8.442-15.86-18.867-17.718-22.056c-1.858-3.184-.199-4.91 1.398-6.497c1.431-1.427 3.186-3.719 4.78-5.578c1.588-1.86 2.118-3.187 3.18-5.311c1.063-2.126.531-3.986-.264-5.579c-.798-1.593-6.987-17.343-9.819-23.64"
        />
    </svg>
    `;
  whatsappButton.href = client_whatsapp_url;
  whatsappButton.target="_blank";
  return whatsappButton;
};

const openTicketWindow = (ticket_png_data) => {
  const newWindow = window.open("", "clientBillTab", "");

  const ticketElement = createTicketElement(ticket_png_data);

  newWindow.document.body.style.margin = "0px";
  newWindow.document.body.appendChild(ticketElement);

  const whatsappButton = createWhatsappButton(
    ticket_png_data["client_whatsapp"]
  );
  let downloadButtonPng = document.createElement("a");

  setTimeout(() => {
    html2canvas(newWindow.document.body, { useCORS: true }).then((canvas) => {
      let dataURL = canvas.toDataURL("image/png");

      downloadButtonPng.href = dataURL;
      downloadButtonPng.download = `boleta_${
        ticket_png_data.ticket_number
      }_${new Date().toLocaleDateString("ES-es")}.png`;

      downloadButtonPng.innerText = "Descargar Imagen";

      downloadButtonPng.style.fontFamily = "sans";
      downloadButtonPng.style.position = "fixed";
      downloadButtonPng.style.bottom = "20px";
      downloadButtonPng.style.right = "20px";
      downloadButtonPng.style.backgroundColor = "#007bff";
      downloadButtonPng.style.color = "#fff";
      downloadButtonPng.style.border = "none";
      downloadButtonPng.style.borderRadius = "50px";
      downloadButtonPng.style.padding = "10px 20px";
      downloadButtonPng.style.fontSize = "16px";
      downloadButtonPng.style.textAlign = "center";
      downloadButtonPng.style.textDecoration = "none";
      downloadButtonPng.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
      downloadButtonPng.style.transition =
        "background-color 0.3s, box-shadow 0.3s";

      downloadButtonPng.onmouseover = function () {
        downloadButtonPng.style.backgroundColor = "#0056b3";
        downloadButtonPng.style.boxShadow = "0 6px 12px rgba(0, 0, 0, 0.3)";
      };

      downloadButtonPng.onmouseout = function () {
        downloadButtonPng.style.backgroundColor = "#007bff";
        downloadButtonPng.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
      };
    });
    
    newWindow.document.body.appendChild(whatsappButton);
    newWindow.document.body.appendChild(downloadButtonPng);
  }, 500);
};

const getTicketPng = async (client_id) => {
  const response = await fetch(`/api/get_ticket_png_data/${client_id}`);
  const data = await response.json();

  if (data.success) openTicketWindow(data.ticket_png_data);
};
