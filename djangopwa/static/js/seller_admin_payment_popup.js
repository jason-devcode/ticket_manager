/**
 * Handles the response from a fetch request and throws an error if the response is not OK.
 * @param {Response} response - The response object from the fetch request.
 * @returns {Promise} The JSON representation of the response.
 * @throws {Error} If the response is not OK.
 */
const handleBadRequestResponse = (response) => {
    removeLoadingModal();
    if (!response.ok) throw new Error("Error while processing the request");
    return response.json();
};

/**
 * Handles any exceptions or errors that occur during the request process.
 * @param {Error} error - The error object containing details of the error.
 */
const handleCatchExceptionErrorRequest = (error) => {
    removeLoadingModal();
    console.error("Error:", error.message);
};


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

/**
 * Component representing a multi-date calendar for selecting dates.
 * @param {string} calendarTitle - The title for the calendar component.
 * @param {function} onClickSearchButton - Function to handle search button click event.
 * @returns {HTMLElement} The container element for the calendar component.
 */
const MultiDateCalendarComponent = (calendarTitle = "", onClickSearchButton = () => { }) => {
    // Create the container div element for the calendar.
    const container = document.createElement("div");

    // Define the styles for the calendar component.
    const styles = `
      <style>
        .calendar-container {
          font-family: Arial, sans-serif;
          max-width: 400px;
          margin: 0 auto;
          padding: 20px;
          border: 1px solid #ccc;
          border-radius: 5px;
          user-select: none;
          background: white;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .calendar-grid-container {
        }

        .calendar-header {
          text-align: center;
          margin-bottom: 10px;
        }
        .calendar-grid {
          display: grid;
          grid-template-columns: repeat(7, 1fr);
          gap: 2px;
        }
        .calendar-cell {
          height: 30px;
          display: flex;
          justify-content: center;
          align-items: center;
          cursor: pointer;
          border: 1px solid transparent;
        }
        .empty-cell {
          background-color: #f0f0f0;
        }
        .date-cell {
          background-color: #e0e0e0;
        }
        .selected-date {
          background-color: #ff6347;
          color: white;
          font-weight: bold;
        }

        #search-button {
            border: 0;
            background: #444;
            color: white;
            padding: 8px 2rem;
        }

        #search-button:hover {
            background: #666;
        }

        .multi_date_calendar_title {
            font-weight: bold;
            font-size: 2rem;
        }
      </style>
    `;

    // Define the HTML structure for the calendar component.
    const html = `
      <div class="calendar-container">
        <span class="multi_date_calendar_title" >${calendarTitle}</span>
        <div class="calendar-grid-container">
            <div class="calendar-header">
              <button id="prev-month">&lt;</button>
              <select id="month-select"></select>
              <select id="year-select"></select>
              <button id="next-month">&gt;</button>
            </div>
            <div class="calendar-grid" id="calendar-grid">
              <div class="calendar-cell">Sun</div>
              <div class="calendar-cell">Mon</div>
              <div class="calendar-cell">Tue</div>
              <div class="calendar-cell">Wed</div>
              <div class="calendar-cell">Thu</div>
              <div class="calendar-cell">Fri</div>
              <div class="calendar-cell">Sat</div>
            </div>
        </div>
        <button id="search-button">Search</button>
      </div>
    `;

    // Insert the styles and HTML into the container.
    container.innerHTML = styles + html;

    // Get references to the key elements within the calendar component.
    const calendarGrid = container.querySelector("#calendar-grid");
    const monthSelect = container.querySelector("#month-select");
    const yearSelect = container.querySelector("#year-select");
    const searchButton = container.querySelector("#search-button");

    // Array to keep track of selected dates.
    let selectedDates = [];
    // Flag to track mouse down state for selecting dates.
    let isMouseDown = false;

    /**
     * Initialize the calendar component by populating month and year dropdowns
     * and setting up event listeners for navigation and date selection.
     */
    const initializeCalendar = () => {
        populateMonths();
        populateYears();

        const today = new Date();
        let currentMonth = today.getMonth();
        let currentYear = today.getFullYear();

        renderCalendar(currentYear, currentMonth);

        monthSelect.value = currentMonth.toString();
        yearSelect.value = currentYear.toString();

        monthSelect.addEventListener("change", () => {
            currentMonth = parseInt(monthSelect.value);
            renderCalendar(currentYear, currentMonth);
        });

        yearSelect.addEventListener("change", () => {
            currentYear = parseInt(yearSelect.value);
            renderCalendar(currentYear, currentMonth);
        });

        container.querySelector("#prev-month").addEventListener("click", () => {
            if (currentMonth === 0) {
                currentMonth = 11;
                currentYear--;
            } else {
                currentMonth--;
            }
            updateCalendar(currentYear, currentMonth);
        });

        container.querySelector("#next-month").addEventListener("click", () => {
            if (currentMonth === 11) {
                currentMonth = 0;
                currentYear++;
            } else {
                currentMonth++;
            }
            updateCalendar(currentYear, currentMonth);
        });

        searchButton.addEventListener("click", handleSearch);

        calendarGrid.addEventListener("mousedown", handleMouseDown);
        document.addEventListener("mouseup", handleMouseUp);
        calendarGrid.addEventListener("mouseover", handleMouseOver);
    };

    /**
     * Populate the month dropdown with month names.
     */
    const populateMonths = () => {
        const months = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
            "septiembre", "octubre", "noviembre", "diciembre"
        ];
        months.forEach((month, index) => {
            const option = document.createElement("option");
            option.value = index;
            option.textContent = month;
            monthSelect.appendChild(option);
        });
    };

    /**
     * Populate the year dropdown with a range of years around the current year.
     */
    const populateYears = () => {
        const currentYear = new Date().getFullYear();
        for (let year = currentYear - 10; year <= currentYear + 10; year++) {
            const option = document.createElement("option");
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        }
    };

    /**
     * Render the calendar for a given year and month.
     * @param {number} year - The year to render.
     * @param {number} month - The month to render (0-based).
     */
    const renderCalendar = (year, month) => {
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const firstDayOfWeek = new Date(year, month, 1).getDay();
        const lastDayOfWeek = new Date(year, month, daysInMonth).getDay();

        calendarGrid.innerHTML = "";

        const daysOfWeek = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"];
        daysOfWeek.forEach(day => {
            const dayCell = document.createElement("div");
            dayCell.className = "calendar-cell";
            dayCell.textContent = day;
            calendarGrid.appendChild(dayCell);
        });

        for (let i = 0; i < firstDayOfWeek; i++) {
            const emptyCell = document.createElement("div");
            emptyCell.className = "calendar-cell empty-cell";
            calendarGrid.appendChild(emptyCell);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dateCell = document.createElement("div");
            dateCell.className = "calendar-cell date-cell";
            dateCell.textContent = day;
            dateCell.setAttribute("data-date", `${year}-${month + 1}-${day}`);

            if (selectedDates.includes(dateCell.getAttribute("data-date"))) {
                dateCell.classList.add("selected-date");
            }

            calendarGrid.appendChild(dateCell);
        }

        for (let i = lastDayOfWeek; i < 6; i++) {
            const emptyCell = document.createElement("div");
            emptyCell.className = "calendar-cell empty-cell";
            calendarGrid.appendChild(emptyCell);
        }
    };

    /**
     * Update the calendar display based on the current year and month.
     * @param {number} year - The year to update to.
     * @param {number} month - The month to update to (0-based).
     */
    const updateCalendar = (year, month) => {
        monthSelect.value = month.toString();
        yearSelect.value = year.toString();
        renderCalendar(year, month);
    };

    /**
     * Handle the mousedown event on a date cell to start the selection process.
     * @param {MouseEvent} event - The mousedown event.
     */
    const handleMouseDown = (event) => {
        const target = event.target;
        if (target.classList.contains("date-cell")) {
            isMouseDown = true;
            toggleDateSelection(target);
        }
    };

    /**
     * Handle the mouseover event to allow selecting multiple dates by dragging.
     * @param {MouseEvent} event - The mouseover event.
     */
    const handleMouseOver = (event) => {
        const target = event.target;
        if (isMouseDown && target.classList.contains("date-cell")) {
            toggleDateSelection(target);
        }
    };

    /**
     * Handle the mouseup event to end the selection process.
     * @param {MouseEvent} event - The mouseup event.
     */
    const handleMouseUp = (event) => {
        isMouseDown = false;
    };

    /**
     * Toggle the selection state of a date cell.
     * @param {HTMLElement} cell - The date cell to toggle.
     */
    const toggleDateSelection = (cell) => {
        const date = cell.getAttribute("data-date");
        const index = selectedDates.indexOf(date);
        if (index === -1) {
            selectedDates.push(date);
            cell.classList.add("selected-date");
        } else {
            selectedDates.splice(index, 1);
            cell.classList.remove("selected-date");
        }
    };

    /**
     * Handle the search button click event to log the selected dates.
     */
    const handleSearch = () => {
        onClickSearchButton(selectedDates)
    };

    // Initialize the calendar component.
    initializeCalendar();

    // Return the container element for the calendar component.
    return container;
};



/**
 * Creates a dynamic balance table component in HTML based on provided data.
 *
 * @param {number} seller_id - The ID of the seller for whom the balance is displayed.
 * @param {Object} data - The data object containing client details and total amount.
 * @returns {HTMLDivElement} The container element containing the rendered balance table component.
 */
const BalanceTableComponent = (seller_id, data) => {
    /**
     * Creates a cell element (either 'th' for header or 'td' for data).
     *
     * @param {string} content - The content/text of the cell.
     * @param {boolean} [isHeader=false] - Whether the cell is a header cell (default: false).
     * @param {string[]} [additionalClasses=[]] - Additional CSS classes to add to the cell.
     * @returns {HTMLTableCellElement} The created cell element.
     */
    const createCell = (content, isHeader = false, additionalClasses = []) => {
        const cell = document.createElement(isHeader ? 'th' : 'td');
        cell.appendChild(document.createTextNode(content));
        additionalClasses.forEach(cls => cell.classList.add(cls));
        return cell;
    };

    /**
     * Creates a header row element for the table.
     *
     * @param {string[]} headers - Array of header texts.
     * @returns {HTMLTableRowElement} The created header row element.
     */
    const createHeaderRow = (headers) => {
        const headerRow = document.createElement('tr');
        headers.forEach(headerText => {
            const cell = createCell(headerText, true, ['header-cell']);
            headerRow.appendChild(cell);
        });
        return headerRow;
    };

    /**
     * Creates a data row element for the table.
     *
     * @param {Object} client - The client object containing client details.
     * @returns {HTMLTableRowElement} The created data row element.
     */
    const createDataRow = (client) => {
        const row = document.createElement('tr');
        row.appendChild(createCell(client.client_id));
        row.appendChild(createCell(client.ticket_number));
        row.appendChild(createCell(client.total_amount));
        row.appendChild(createCell(new Date(client.last_payment_date).toLocaleString()));
        return row;
    };

    /**
     * Creates a total row element for the table.
     *
     * @param {number} totalAmount - The total amount to display in the row.
     * @returns {HTMLTableRowElement} The created total row element.
     */
    const createTotalRow = (totalAmount) => {
        const totalRow = document.createElement('tr');
        totalRow.appendChild(createCell('', false, ['total-cell']));
        totalRow.appendChild(createCell('Total', false, ['total-cell']));
        totalRow.appendChild(createCell(totalAmount, false, ['total-cell']));
        totalRow.appendChild(createCell('', false, ['total-cell']));
        return totalRow;
    };

    /**
     * Creates the main table element including header, data rows, and total row.
     *
     * @param {Object} data - The data object to populate the table.
     * @returns {HTMLTableElement} The created table element.
     */
    const createTable = (data) => {
        const table = document.createElement('table');
        table.classList.add('custom-table');

        // Create the table header
        const thead = document.createElement('thead');
        const titleRow = document.createElement('tr');
        const titleCell = createCell('Listado de cuadre', true, ['header-cell', 'table-header']);
        titleCell.colSpan = 4;
        titleRow.appendChild(titleCell);
        thead.appendChild(titleRow);
        thead.appendChild(createHeaderRow(['ID', '# de Rifa', 'Total Valor', 'Fecha último pago']));
        table.appendChild(thead);

        // Create the table body
        const tbody = document.createElement('tbody');
        Object.keys(data).forEach(key => {
            if (key !== "total") {
                tbody.appendChild(createDataRow(data[key]));
            }
        });

        // Add the total row at the end of the table
        tbody.appendChild(createTotalRow(data.total.amount));
        table.appendChild(tbody);

        return table;
    };

    /**
     * Builds the endpoint URL for generating a seller bill.
     *
     * @param {number} sellerID - The ID of the seller.
     * @returns {string} The constructed endpoint URL.
     */
    const buildEndpointGenerateSellerBill = (sellerID) => {
        const endpointUrl = `/api/generate_seller_bill/${sellerID}`;
        return endpointUrl;
    };

    function formatNumber(numberString) {
        // Convierte la cadena de número a un entero
        const number = parseInt(numberString, 10);

        // Usa toLocaleString para formatear el número con puntos como separadores de miles
        return number.toLocaleString('de-DE');
    }


    const generateBillSalesTableRows = (payments) => {
        let templateTableRows = ``;

        payments.forEach((payment) => {
            templateTableRows += `
                <tr>
                    <td>${payment.client_id}</td>
                    <td>${payment.ticket_number}</td>
                    <td>$${formatNumber(payment.total_amount.toString())}</td>
                    <td>${formatDateTime(payment.last_payment_date)}</td>   
                </tr>
            `
        })

        return templateTableRows;
    }

    const billSellerComponent = (sellerID, billData) => {

        const billContainer = document.createElement("div");

        if (billData === undefined) return billContainer;

        billContainer.style.display = "flex";
        billContainer.style.flexDirection = "column";
        billContainer.style.width = "100vw";
        billContainer.style.height = "100vh";
        billContainer.style.backgroundColor = "white";

        const style = `
            <style>
                .bill-body {
                  display: flex;
                  flex-direction: column;
                  height: 100%;
                  background-color: white;
                  gap: 2rem;
                  padding: 0.5rem;
                }

                .bill-container {
                  display: flex;
                  flex-directtion: column;
                  width: 100vw;
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
                  font-size: 2rem;
                  width: 14rem;
                  height: 6rem;
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
                  font-size: 2rem;
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

        const html = `
            <div class="bill-container">
              <div class="bill-body">
                <!-- BILL HEADER -->
                <div class="grid-container">
                  <div class="grid-cell">
                    <span class="bill-title" style="color: red;">Factura de Cobro</span>
                  </div>
                  <div class="grid-cell">
                    <span class="bill-title">No. ${billData.bill_id}</span>
                  </div>
                </div>
                <!-- BILL SELLER DATA -->
                <div class="grid-container">
                  <div class="grid-cell">
                    <span class="bill-grid-left-text">Factura generada el: </span>
                  </div>
                  <div class="grid-cell">
                    <span class="bill-grid-right-text">${formatDateTime(billData.generation_date, true)}</span>
                  </div>

                  <div class="grid-cell">
                      <span class="bill-grid-left-text">ID Vendedor: 
                        <span class="bill-grid-right-text">${billData.seller.seller_id}</span>
                      </span>
                  </div>
                  <div class="grid-cell">
                      <span class="bill-grid-left-text">Ciudad: 
                        <span class="bill-grid-right-text">${billData.seller.city_residence}</span>
                      </span>
                  </div>

                  <div class="grid-cell">
                      <span class="bill-grid-left-text">Vendedor: </span>
                  </div>
                  <div class="grid-cell">
                        <span class="bill-grid-right-text">${billData.seller.first_name + " " + billData.seller.last_name}</span>
                  </div>
                  <div class="grid-cell">
                      <span class="bill-grid-left-text">Documento: </span>
                  </div>
                  <div class="grid-cell">
                        <span class="bill-grid-right-text">${formatNumber(billData.seller.document_number)}</span>
                  </div>
                  <div class="grid-cell">
                      <span class="bill-grid-left-text">Whatsapp: </span>
                  </div>
                  <div class="grid-cell">
                        <span class="bill-grid-right-text">${billData.seller.whatsapp}</span>
                  </div>
                </div>
                <!-- SALES LIST -->
                <span class="sales-list">Lista de Ventas</span>

                <table class="sales-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th># de Rifa</th>
                      <th>Total Valor</th>
                      <th>Fecha Último Pago</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${generateBillSalesTableRows(billData.payment_balances)}
                  </tbody>
                </table>
                <!-- BILL HEADER -->
                <div class="grid-container">
                  <div class="grid-cell">
                    <span class="total-to-pay" style="color: red;">Total a Pagar</span>
                  </div>
                  <div class="grid-cell">
                    <span class="total-to-pay-value">$${formatNumber(billData.total_amount.toString())}</span>
                  </div>
                </div>
              </div>
            </div>
        `;
        billContainer.innerHTML = style + html;

        return billContainer;
    }

    /**
    * Opens a new window with the balance table component.
    *
    * @param {Object} data - The data to populate the table.
    * @param {number} seller_id - The ID of the seller.
    */
    const openBalanceTableWindow = (result, seller_id) => {
        // Create new window
        const newWindow = window.open('', '_blank', 'width=800,height=600');

        // Create balance table component and append to new window
        const billElement = billSellerComponent(seller_id, result?.data?.bill);

        billElement.id = "capture";

        newWindow.document.body.style.margin = "0px";
        newWindow.document.body.appendChild(billElement);

        setTimeout(
            () => {
                html2canvas(newWindow.document.body).then((canvas) => {
                    let dataURL = canvas.toDataURL('image/jpeg');

                    let downloadButton = document.createElement('a');
                    
                    downloadButton.href = dataURL;
                    downloadButton.download = `factura${result?.data?.bill?.bill_id || 0}.jpg`;

                    downloadButton.innerText = 'Descargar factura';
                    
                    downloadButton.style.fontFamily = 'sans';
                    downloadButton.style.position = 'fixed';
                    downloadButton.style.bottom = '20px';
                    downloadButton.style.right = '20px';
                    downloadButton.style.backgroundColor = '#007bff';
                    downloadButton.style.color = '#fff';
                    downloadButton.style.border = 'none';
                    downloadButton.style.borderRadius = '50px';
                    downloadButton.style.padding = '10px 20px';
                    downloadButton.style.fontSize = '16px';
                    downloadButton.style.textAlign = 'center';
                    downloadButton.style.textDecoration = 'none';
                    downloadButton.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
                    downloadButton.style.transition = 'background-color 0.3s, box-shadow 0.3s';

                    downloadButton.onmouseover = function () {
                        downloadButton.style.backgroundColor = '#0056b3';
                        downloadButton.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.3)';
                    };

                    downloadButton.onmouseout = function () {
                        downloadButton.style.backgroundColor = '#007bff';
                        downloadButton.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
                    };

                    newWindow.document.body.appendChild(downloadButton);
                });
            }, 500);
    };

    /**
     * Handles the response from a fetch request to generate a seller bill.
     *
     * @param {Object} result - The response result from the fetch request.
     */
    const handleRequestGenerateBillResponse = (result) => {
        removeLoadingModal();
        openBalanceTableWindow(result, seller_id)
        // const modals = document.querySelectorAll('.payment_balance_modal');
        // if (modals) modals.forEach((modal) => document.body.removeChild(modal));
        // document.body.appendChild(balanceModalElement)
    };

    /**
     * Performs a request to generate a seller bill using payment balance data.
     *
     * @param {Object} paymentBalance - The payment balance data object.
     * @param {number} sellerID - The ID of the seller for whom to generate the bill.
     */
    const performGenerateSellerBill = (paymentBalance, sellerID) => {
        const loadingModal = createLoadingModal(); // Assume this function creates a loading modal
        document.body.appendChild(loadingModal);

        const endpointUrl = buildEndpointGenerateSellerBill(sellerID);

        const requestBody = {
            payments: paymentBalance
        };

        const csrfToken = getCookie('csrftoken'); // Assuming getCookie function exists

        fetch(endpointUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(requestBody)
        })
            .then(handleBadRequestResponse) // Assuming handleBadRequestResponse function is defined elsewhere
            .then(handleRequestGenerateBillResponse)
            .catch(handleCatchExceptionErrorRequest); // Assuming handleCatchExceptionErrorRequest function is defined elsewhere
    };

    /**
     * Handles the click event for the "Generate Bill" button.
     */
    const handleOnClickGenerateBillButton = () => {
        performGenerateSellerBill(data, seller_id); // Assuming data and seller_id are accessible
    };

    /**
     * Creates a button element for generating a seller bill.
     *
     * @returns {HTMLDivElement} The container element containing the button.
     */
    const createButton = () => {
        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('button-container');

        const button = document.createElement('button');
        button.classList.add('generate-button');
        button.textContent = "Generar Factura";
        buttonContainer.appendChild(button);

        button.addEventListener("click", handleOnClickGenerateBillButton);

        return buttonContainer;
    };

    /**
     * Creates and returns a style element with CSS styles for the table.
     *
     * @returns {HTMLStyleElement} The style element containing table CSS styles.
     */
    const createTableStyles = () => {
        const style = document.createElement('style');
        style.innerHTML = `
            .custom-table {
                border-collapse: collapse;
                border-radius: 15px;
                table-layout: fixed;
                margin: 0 auto;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .custom-table th {
                background-color: #f2f2f2;
                padding: 10px;
                text-align: center;
                border-top: none;
                border-left: none;
                border-right: none;
                font-weight: bold;
                color: #00BFFF; /* Header text color */
            }
            .custom-table td {
                padding: 10px;
                text-align: center;
                text-wrap: nowrap;
            }
            .custom-table .header-cell {
                height: 40px;
            }
            .custom-table .data-cell {
                height: 50px;
            }
            .custom-table .total-cell {
                background-color: #e0e0e0;
                height: 40px;
                border-left: none;
                border-right: none;
                border-bottom: none;
            }
            .table-header {
                text-align: center;
                font-weight: bold;
                font-size: 1.5rem;
                color: #000000 !important; /* Title text color */
            }
            #balance-table-container {
                border-radius: 15px; /* Rounded borders for the container */
                background-color: #ffffff; /* White background for the container */
            }
            .button-container {
                text-align: center;
                margin: 1rem; /* Space above the button */
            }
            .generate-button {
                background-color: #00BFFF; /* Button background color */
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
                font-size: 1rem;
                cursor: pointer;
                text-align: center;
            }
        `;
        return style;
    };

    /**
     * Creates the main container element for the balance table component.
     *
     * @param {Object} data - The data object to populate the table.
     * @returns {HTMLDivElement} The created container element.
     */
    const createContainer = (data) => {
        const containerDiv = document.createElement('div');
        containerDiv.id = "balance-table-container";
        containerDiv.style.maxHeight = "800px";
        containerDiv.style.overflow = "hidden";
        containerDiv.style.borderRadius = "15px";
        containerDiv.style.backgroundColor = "#ffffff";
        containerDiv.style.boxShadow = "0 0 10px rgba(0, 0, 0, 0.1)";

        const style = createTableStyles();
        const table = createTable(data);
        const button = createButton();

        containerDiv.appendChild(style);
        containerDiv.appendChild(table);
        containerDiv.appendChild(button);

        return containerDiv;
    };

    // Initialize component creation
    return createContainer(data);
};


/**
 * Retrieves the value of a cookie by its name.
 *
 * @param {string} name - The name of the cookie to retrieve.
 * @returns {string|null} The value of the cookie, or null if not found.
 */
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};


/**
 * Creates and returns an overlay element for the modal.
 * @returns {HTMLDivElement} The created overlay element.
 */
const createOverlay = () => {
    const overlay = document.createElement('div');
    overlay.className = 'modal_overlay';
    overlay.id = 'modalOverlay';
    overlay.addEventListener('click', removeModal);
    return overlay;
};

/**
 * Creates and returns the modal element.
 * @returns {HTMLDivElement} The created modal element.
 */
const createModal = (modalId) => {
    const modal = document.createElement('div');
    modal.id = modalId;
    modal.classList.add('payment_balance_modal');
    return modal;
};

const createLoadingModal = () => {
    const loadingModal = createModal("loading_modal");

    const styles = `
        <style>
            .loading-modal-container {
                display: flex;
                width: 100%;
                height: 100%;
                justify-content: center;
                align-items: center;
                font-size: 1.5rem;
                font-weight: bold;
                background-color: white; /* Set background color to white */
                padding: 2rem;
                border-radius: 9999px;
            }
        </style>    
    `;

    const html = `<div class="loading-modal-container">Cargando...</div>`;

    loadingModal.innerHTML = styles + html;
    return loadingModal;
};

const removeLoadingModal = () => {
    const loadingModal = document.getElementById("loading_modal");
    if (loadingModal) document.body.removeChild(loadingModal)
};


const createBalancePaymentModal = (seller_id, result) => {
    const balancePaymentModal = createModal("balance_payment_modal");
    const balanceContainer = document.createElement('div');
    balanceContainer.classList.add("balance-payment-modal-container");

    styles = `
    <style>
        .balance-payment-modal-container {
            display: flex;
            width: 100%;
            height: 100%;
            justify-content: center;
            align-items: center;
            font-size: 1.5rem;
            font-weight: bold;
        }
    </style>`

    balanceContainer.innerHTML += styles

    balanceContainer.appendChild(BalanceTableComponent(seller_id, result.data));

    balancePaymentModal.appendChild(balanceContainer);
    return balancePaymentModal;
};

const removeBalancePaymentModal = () => {
    const balancePaymentModal = document.getElementById("balance_payment_modal");
    document.body.removeChild(balancePaymentModal)
};

/**
 * Removes the modal and overlay elements from the DOM.
 */
const removeModal = () => {
    const modals = document.querySelectorAll('.payment_balance_modal');
    const overlay = document.getElementById('modalOverlay');
    if (modals) {
        modals.forEach((modal) => document.body.removeChild(modal));
    }
    if (overlay) {
        document.body.removeChild(overlay);
    }
};

/**
 * Builds and returns the endpoint URL for fetching payment balance data.
 * @param {number} sellerID - The ID of the seller.
 * @returns {string} The constructed endpoint URL.
 */
const buildEndpointGetPaymentBalance = (sellerID) => {
    const endpointUrl = `/api/balance_payment_list/${sellerID}`
    return endpointUrl;
};

/**
 * Handles the response from a fetch request and logs the result.
 * @param {Object} result - The response result from the fetch request.
 */
const handleRequestPaymentBalanceResponse = (seller_id, result) => {
    removeLoadingModal();
    const modals = document.querySelectorAll('.payment_balance_modal');
    if (modals) modals.forEach((modal) => document.body.removeChild(modal));
    balanceModalElement = createBalancePaymentModal(seller_id, result)
    document.body.appendChild(balanceModalElement)
};


/**
 * Performs a fetch request to retrieve payment balance data based on selected dates.
 * @param {number} sellerID - The ID of the seller for whom to fetch payment balance.
 * @param {Array} selectedDates - Array of selected dates for which to fetch data.
 */
const performPaymentBalanceRequest = (sellerID, selectedDates) => {

    const loadingModal = createLoadingModal();
    document.body.appendChild(loadingModal);

    const endpointUrl = buildEndpointGetPaymentBalance(sellerID);

    // Construct the request body
    const requestBody = {
        dates: selectedDates
    };

    const csrfToken = getCookie('csrftoken');

    fetch(endpointUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Include token CSRF
        },
        body: JSON.stringify(requestBody)
    })
        .then(handleBadRequestResponse)
        .then((result) => handleRequestPaymentBalanceResponse(sellerID, result))
        .catch(handleCatchExceptionErrorRequest);
};

/**
 * Inserts the payment balance modal into the DOM.
 * @param {number} seller_id - The ID of the seller for whom to insert the modal.
 */
const insertPaymentBalanceModal = (seller_id) => {
    const overlay = createOverlay();
    const modal = createModal('modal_container_balance_payment');
    const multiDateElement = MultiDateCalendarComponent(
        "Cuadre de pagos", (selectedDates) => performPaymentBalanceRequest(seller_id, selectedDates));

    modal.appendChild(multiDateElement);

    document.body.appendChild(overlay);
    document.body.appendChild(modal);
};

/**
 * Initializes the payment balance modal for a seller with the given seller ID.
 * @param {number} seller_id - The ID of the seller for whom the modal is being initialized.
 */
const balance_seller_payment = (seller_id) => {
    insertPaymentBalanceModal(seller_id);
};
