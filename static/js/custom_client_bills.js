
const BillTypes = {
    BONO1: 1,
    BONO2: 2,
    BONO3: 3,
    TOTAL_PAYMENT: 4,
}

const formatDateTime = (dateTimeString, includeTime = false) => {
    // Create a Date object from the date and time string (assumed UTC)
    const date = new Date(dateTimeString);

    // Convert UTC date to Colombia time zone (UTC-5)
    const colombiaDate = new Date(date.getTime() - (5 * 60 * 60 * 1000));

    // Days of the week and months in Spanish
    const daysOfWeek = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

    // Get the day of the week, day of the month, month, and year
    const dayOfWeek = daysOfWeek[colombiaDate.getUTCDay()];
    const day = String(colombiaDate.getUTCDate()).padStart(2, '0');
    const month = months[colombiaDate.getUTCMonth()];
    const year = colombiaDate.getUTCFullYear();

    // Format the date
    let formattedDate = `${dayOfWeek}, ${day}/${month}/${year}`;

    // If includeTime is true, add the time to the formatted string
    if (includeTime) {
        const hours = String(colombiaDate.getUTCHours()).padStart(2, '0');
        const minutes = String(colombiaDate.getUTCMinutes()).padStart(2, '0');
        const seconds = String(colombiaDate.getUTCSeconds()).padStart(2, '0');
        formattedDate += `, Hora: ${hours}:${minutes}:${seconds}`;
    }

    return formattedDate;
};

function formatNumber(numberString) {
    // Convierte la cadena de número a un entero
    const number = parseInt(numberString, 10);

    // Usa toLocaleString para formatear el número con puntos como separadores de miles
    return number.toLocaleString('de-DE');
}

const billClientComponent = (billData) => {

    const billContainer = document.createElement("div");

    if (billData === undefined) return billContainer;

    billContainer.style.display = "flex";
    billContainer.style.flexDirection = "column";
    billContainer.style.width = "max-content";
    // billContainer.style.height = "100vh";
    billContainer.style.backgroundColor = "white";

    const style = `
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

            .bill-body {
              display: flex;
              flex-direction: column;
              height: 100%;
              background-color: white;
              padding: 0.5rem;
            }

            .bill-container {
              display: flex;
              flex-direction: column;
              height: 100%;
              font-family: sans;
              justify-content: center;
            }

            .grid-container {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 10px;
            }

            .grid-cell {
              display: flex;
              justify-content: center;
              align-items: center;
            }

            .bill-title {
              display: flex;
              justify-content: center;
              align-items: center;
              font-weight: 900;
              font-size: 1.5rem;
              width: 14rem;
              text-align: center;
            }

            .bill-grid-left-text {
              font-weight: 700;
              text-align: right;
            }

            .bill-grid-right-text {
              font-weight: 700;
              color: gray;
              width: 9rem;
              text-align: center;
            }

            .sales-list {
              display:flex;
              width: 100%;
              justify-content: center;
              font-size: 1.5rem;
              margin: 0.5rem;
              font-weight: 900;
            }

            .sales-table {
              border-collapse: collapse;
              width: 100%;
            }
            .sales-table th, .sales-table td {
              border: 1px solid #ccc; /* Gris claro */
              padding: 8px;
              text-align: center;
            }

            .sales-table {
              border-top: 2px solid white;
              border-right: 2px solid white;
              border-left: 2px solid white;
              border-bottom: 0px solid white;
            }

            .total-to-pay {
              color: red;
              font-size: 1.5rem;
              font-weight: bold;
            }

            .total-to-pay-value {
              color: red;
              border: 1px solid red;
              padding: 0.5rem 2rem;
              font-size: 1.5rem;
              font-weight: bold;
            }
        </style>        
    `

    const ticket_template = billData.ticket_template
    const certificate_template = billData.certificate_template

    const contain_certificate = certificate_template && certificate_template !== '';

    const html = ticket_template && ticket_template !== "" ? `
        <div style="display: flex; width: 100%; justify-content: center; position: relative; font-family: sans-serif;" >
          <div style="display: flex; flex-direction: column; position: relative;" >
            <div style="display: flex; width: 100%; height: 10rem;" >
              
              <div style="display: flex;flex-direction: column;width: 100%;padding: 0px 0.5rem;border: 2px solid lightgray;">
                <div style="display: flex;flex-direction: column;width: 100%;">
                    <div style="display: flex; padding-top: 6px; padding-left: 5%; border-bottom: 2px solid black; font-weight: bold; font-size: 0.85rem;">${billData.client.name} ${billData.client.lastname}</div>
                    <span style="font-weight: bold; color: #3f3f3f; font-size: 0.7rem;"><i>Nombre y Apellidos</i></span>
                </div>

                <div style="display: flex;width: 100%;gap: 8px;">
                    <div style="display: flex;flex-direction: column;width: 100%;">
                        <div style="display: flex; padding-top: 6px; padding-left: 5%; border-bottom: 2px solid black; font-weight: bold; font-size: 0.85rem;">
                          ${billData.client.document}
                        </div>
                        <span style="font-weight: bold; color: #3f3f3f; font-size: 0.7rem;"><i>Documento</i></span>
                    </div>
                    <div>
                        <span style="white-space: nowrap; color: red; font-weight: bold; font-size: 1.2rem;">
                          N° ${billData.ticket_number} 
                        </span>
                    </div>
                </div>

                <div style="display: flex;width: 100%;gap: 5px;">
                    <div style="display: flex;flex-direction: column;width: 100%;">
                        <div style="display: flex; padding-top: 6px; padding-left: 5%; border-bottom: 2px solid black; font-weight: bold; font-size: 0.85rem;">${billData.client.telephone}</div>
                        <span style="font-weight: bold; color: #3f3f3f; font-size: 0.7rem;"><i>Celular</i></span>
                    </div>
                    <div style="display: flex;flex-direction: column;width: 100%;">
                        <div style="display: flex; padding-top: 6px; padding-left: 5%; border-bottom: 2px solid black; font-weight: bold; font-size: 0.85rem;">${billData.client.city}</div>
                        <span style="font-weight: bold; color: #3f3f3f; font-size: 0.7rem;"><i>Ciudad</i></span>
                    </div>
                </div>
                <div style="display: flex;width: 100%; height: 100%; align-items: center;">
                    <div style="display: flex; width: 70%; gap: 2rem; justify-content: center; align-items: center; font-size: 0.8rem;font-weight: bold;">
                        <span style="width: min-content">Abono ${billData.client.balance}</span>
                        <span style="width: min-content">Saldo ${billData.client.amount_to_pay}</span>
                    </div>
                    <div style="display: flex;align-items: center;flex-direction: column;">
                        <div style="display: flex;padding-top: 6px;padding-left: 5%;border-bottom: 2px solid black;font-weight: bold;font-size: 0.85rem;white-space: nowrap;">${billData.client.seller_name_lastname}</div>
                        <span style="font-weight: bold; color: #3f3f3f; font-size: 0.7rem;"><i>Vendedor Boleta</i></span>
                    </div>
                </div>
              </div>

              <div style="display: flex;width: 100%;justify-content: center;align-items: center;font-size: 3rem;font-weight: bold;">
                <span>Logo</span>
              </div>
            </div>

            ${
              contain_certificate ? `
                <div style="display: flex; padding: 2rem; position: relative;" >
                  <img src="${certificate_template}"  style="position: absolute; width: 52%; top: 0px; left: 0px;" crossOrigin="anonymous">
                  <p style="position: absolute; left: 40%; transform: translateX(-50%); top: 18%; font-weight: bold; font-size: 1.4rem; color: red;"> N° ${billData.ticket_number} </p>
                </div>
              ` : ""
            }

            <div style="display: flex; position: relative;" >
                <img src="${ticket_template}" style="position: relative; height: ${ contain_certificate ? "26rem" : "31.5rem" };" crossOrigin="anonymous">
                    <p style="position: absolute; left: 40%; transform: translateX(-50%); top: 82%; font-weight: bold; font-size: 1.4rem; color: red;"> N° ${billData.ticket_number} </p>            
                </img>
            </div>
          </div>
        </div>
    ` : "";

    billContainer.innerHTML = html;

    return billContainer;
}

const createWhatsappButton = (client_whatsapp_url) => {
  const whatsappButton = document.createElement("a");
  whatsappButton.style.position = "fixed";
  whatsappButton.style.right = "20px";
  whatsappButton.style.bottom = "180px";
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
  whatsappButton.target = "_blank";
  return whatsappButton;
};

const openClientBillWindow = (billData) => {
    // Create new window
    const newWindow = window.open('', `clientBillTab_${Date.now()}`, '');

    // Create balance table component and append to new window
    const billElement = billClientComponent(billData);

    billElement.id = "capture";

    newWindow.document.body.style.margin = "0px";
    newWindow.document.body.style.display = "flex";
    newWindow.document.body.style.justifyContent = "center";

    newWindow.document.body.appendChild(billElement);

    
    const whatsappButton = createWhatsappButton(`https://wa.me/${billData.client.whatsapp}`);

    let downloadButtonPdf = document.createElement('div');
    let downloadButtonJpg = document.createElement('a');

    setTimeout(
        () => {
            downloadButtonPdf.innerText = 'Descargar PDF';
            downloadButtonPdf.id = "download-button"

            downloadButtonPdf.style.fontFamily = 'sans';
            downloadButtonPdf.style.position = 'fixed';
            downloadButtonPdf.style.bottom = '100px';
            downloadButtonPdf.style.right = '20px';
            downloadButtonPdf.style.backgroundColor = '#007bff';
            downloadButtonPdf.style.color = '#fff';
            downloadButtonPdf.style.border = 'none';
            downloadButtonPdf.style.borderRadius = '50px';
            downloadButtonPdf.style.padding = '10px 20px';
            downloadButtonPdf.style.fontSize = '16px';
            downloadButtonPdf.style.textAlign = 'center';
            downloadButtonPdf.style.textDecoration = 'none';
            downloadButtonPdf.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
            downloadButtonPdf.style.transition = 'background-color 0.3s, box-shadow 0.3s';

            downloadButtonPdf.onmouseover = function () {
                downloadButtonPdf.style.backgroundColor = '#0056b3';
                downloadButtonPdf.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.3)';
                downloadButtonPdf.style.cursor = "pointer";
            };

            downloadButtonPdf.onmouseout = function () {
                downloadButtonPdf.style.backgroundColor = '#007bff';
                downloadButtonPdf.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
                downloadButtonPdf.style.cursor = "default";
            };

            downloadButtonPdf.addEventListener("click", () => {
                downloadButtonPdf.style.display = 'none';
                downloadButtonJpg.style.display = 'none';
                whatsappButton.style.display = 'none';
                newWindow.print();
                downloadButtonPdf.style.display = 'block';
                downloadButtonJpg.style.display = 'block';
                whatsappButton.style.display = 'block';
            });
        }, 500);

    setTimeout(
        () => {
            html2canvas(billElement, { useCORS: true }).then((canvas) => {
                let dataURL = canvas.toDataURL('image/jpeg');

                downloadButtonJpg.href = dataURL;
                downloadButtonJpg.download = `factura_${new Date().toLocaleDateString("ES-es")}.jpg`;

                downloadButtonJpg.innerText = 'Descargar Imagen';

                downloadButtonJpg.addEventListener("click", () => {
                    downloadButtonPdf.style.display = "none";
                    setTimeout(() => downloadButtonPdf.style.display = "block", 1000);
                });

                downloadButtonJpg.style.fontFamily = 'sans';
                downloadButtonJpg.style.position = 'fixed';
                downloadButtonJpg.style.bottom = '20px';
                downloadButtonJpg.style.right = '20px';
                downloadButtonJpg.style.backgroundColor = '#007bff';
                downloadButtonJpg.style.color = '#fff';
                downloadButtonJpg.style.border = 'none';
                downloadButtonJpg.style.borderRadius = '50px';
                downloadButtonJpg.style.padding = '10px 20px';
                downloadButtonJpg.style.fontSize = '16px';
                downloadButtonJpg.style.textAlign = 'center';
                downloadButtonJpg.style.textDecoration = 'none';
                downloadButtonJpg.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
                downloadButtonJpg.style.transition = 'background-color 0.3s, box-shadow 0.3s';

                downloadButtonJpg.onmouseover = function () {
                    downloadButtonJpg.style.backgroundColor = '#0056b3';
                    downloadButtonJpg.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.3)';
                };

                downloadButtonJpg.onmouseout = function () {
                    downloadButtonJpg.style.backgroundColor = '#007bff';
                    downloadButtonJpg.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
                };


                newWindow.document.body.appendChild(downloadButtonPdf);
                newWindow.document.body.appendChild(downloadButtonJpg);
                newWindow.document.body.appendChild(whatsappButton);
            });
        }, 500);
};

const handleResponseGetClientBill = (response) => {
    billData = response.bill_data
    if (billData)
        openClientBillWindow(billData);
    else
        alert("No se ha realizado este pago")
}

const handleBadGetClientBillDataRequest = (response) => {
    if (!response.ok)
        throw new Error(`HTTP error! Status: ${response.status}`);
    return response.json();
}

const getClientBill = (clientId, billType) => {
    const endpoint = `/api/get_client_bill_data/${clientId}/${billType}`;
    fetch(endpoint)
        .then(handleBadGetClientBillDataRequest)
        .then(handleResponseGetClientBill)
        .catch((error) => {
            console.error('Error fetching the client bill:', error);
        });
}




