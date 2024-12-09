let gLotteryId = undefined;

// javascript logic to scroll buy button
const scrollToElement = () => {
    const targetElement = document.getElementById('buy-your-numbers');
    targetElement.scrollIntoView({ behavior: 'smooth' });
}

//  buy and reserve buttons logic

const buildSelectedTicketNumbersQuery = () =>
    `ticket_numbers=${userTicketNumbers.join(',')}`

const onClickBuyNow = () => {
    if (userTicketNumbers.length < 1) {
        alert("Necesita seleccionar al menos 1 numero");
        return;
    }
    const ticketsQuery = buildSelectedTicketNumbersQuery();
    window.location.href = `lottery/${gLotteryId}/purchase_data?${ticketsQuery}`
}

const hideBuyNowButton = () => {
    const button = document.getElementById("buy-now-button");
    button.style.display = "none";
}

const showBuyNowButton = () => {
    const button = document.getElementById("buy-now-button");
    button.style.display = "block";
}

const checkForToggleBuyButtonVisibility = () => {
    if (userTicketNumbers.length === 0)
        hideBuyNowButton();
    else
        showBuyNowButton();
}

hideBuyNowButton();

//  get and check ticket search state - search ticket section

const checkTicketStateButton = document.getElementById("check-ticket-state-button");

/**
 * Retrieves the value of a specific ticket number digit from the input fields.
 * @param {number} digitPosition - The position of the digit (1 to 4).
 * @returns {number} The value of the specified ticket number digit as an integer.
 */
const getInputTicketDigitValue = (digitPosition) =>
    parseInt(
        document.getElementById(`ticket-number-digit-${digitPosition}`).value
    );

/**
 * Constructs the complete ticket number from the individual digit values.
 * @param {number} digit_1 - The value of the first digit (from left to right).
 * @param {number} digit_2 - The value of the second digit (from left to right).
 * @param {number} digit_3 - The value of the third digit (from left to right).
 * @param {number} digit_4 - The value of the fourth digit (from left to right).
 * @returns {number} The constructed ticket number as an integer.
 */
const buildTicketNumber = (digit_1, digit_2, digit_3, digit_4) => {
    const EXP_DIGIT_4_POSITION = 1000; // same to multiply by 10^3
    const EXP_DIGIT_3_POSITION = 100; // same to multiply by 10^2
    const EXP_DIGIT_2_POSITION = 10; // same to multiply by 10^1
    const EXP_DIGIT_1_POSITION = 1; // same to multiply by 10^0

    const ticket_number =
        digit_4 * EXP_DIGIT_4_POSITION +
        digit_3 * EXP_DIGIT_3_POSITION +
        digit_2 * EXP_DIGIT_2_POSITION +
        digit_1 * EXP_DIGIT_1_POSITION;

    return ticket_number;
};
/**
 * Constructs the complete ticket number from the individual digit values.
 * @returns {number} The constructed ticket number as an integer.
 */
const getAndBuildTicketNumber = () => {
    const ticketDigit_1 = getInputTicketDigitValue(1);
    const ticketDigit_2 = getInputTicketDigitValue(2);
    const ticketDigit_3 = getInputTicketDigitValue(3);
    const ticketDigit_4 = getInputTicketDigitValue(4);

    const ticket_number = buildTicketNumber(
        ticketDigit_1,
        ticketDigit_2,
        ticketDigit_3,
        ticketDigit_4
    );

    return ticket_number;
};

const hideWarningTicketNotAvailable = () => {
    const warningSpan = document.getElementById("warning-ticket-not-available");
    warningSpan.style.display = "none";
}

const showWarningTicketNotAvailable = () => {
    const warningSpan = document.getElementById("warning-ticket-not-available");
    warningSpan.style.display = "inline";
}

const hideAddToCartButton = () => {
    const addToCartButton = document.getElementById("add-to-shoppy-cart-button-search-section");
    addToCartButton.style.display = "none";
}

const showAddToCartButton = () => {
    const addToCartButton = document.getElementById("add-to-shoppy-cart-button-search-section");
    addToCartButton.style.display = "flex";
}

const handleOnClickAddToShoppyCartSearchSection = () => {
    hideAddToCartButton();
    addSelectedNumber(getAndBuildTicketNumber());
}

const getTicketState = async () => {
    const response = await fetch(`api/get_ticket_state?lottery_id=${gLotteryId}&ticket_number=${getAndBuildTicketNumber()}`);
    const data = await response.json();
    const ticket_state = data["ticket_state"];

    if (ticket_state) showAddToCartButton();
    else showWarningTicketNotAvailable();

    checkTicketStateButton.disabled = false;
}

checkTicketStateButton.addEventListener("click", () => {
    checkTicketStateButton.disabled = true;
    hideAddToCartButton();
    hideWarningTicketNotAvailable();
    getTicketState();
});


// javascript logic for ticket numbers list
let currentPage = 1;
const ticketContainer = document.getElementById('ticket-container');
const prevButton = document.getElementById('prev-button');
const nextButton = document.getElementById('next-button');
const pageInfo = document.getElementById('page-info');

const activeTicketButtonClass = "active-ticket-number-option";


async function loadTickets(page) {
    const response = await fetch(`?page=${page}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    });
    const data = await response.json();

    // Limpiar contenedor antes de agregar nuevos tickets
    ticketContainer.innerHTML = '';

    data.tickets.forEach(ticket => {
        const button = document.createElement('button');
        button.id = `ticket-search-context-${ticket.number}`;
        button.className = 'border-4 border-cyan-300 rounded-md text-center bg-white md:hover:bg-cyan-200';
        button.textContent = ticket.number.toString().padStart(4, '0');
        button.addEventListener("click", () => {
            if (button.classList.contains(activeTicketButtonClass)) removeSelectNumber(ticket.number);
            else addSelectedNumber(ticket.number);
        }
        );

        ticketContainer.appendChild(button);

        if (userTicketNumbers.includes(ticket.number)) activeTicketButton(ticket.number);
    });

    pageInfo.textContent = `Página ${page}`;

    // Controlar la habilitación de los botones de paginación
    prevButton.disabled = !data.has_previous;
    nextButton.disabled = !data.has_next;
}


prevButton.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        loadTickets(currentPage);
    }
});

nextButton.addEventListener('click', () => {
    currentPage++;
    loadTickets(currentPage);
});

// Cargar los tickets iniciales
loadTickets(currentPage);


// javascript logic for ticket numbers selected
let userTicketNumbers = []

const hideWarningSelectNumbers = () => {
    const warningMessageElement = document.getElementById("warning-select-numbers");
    warningMessageElement.style.display = "none";
}

const showWarningSelectNumbers = () => {
    const warningMessageElement = document.getElementById("warning-select-numbers");
    warningMessageElement.style.display = "flex";
}

const activeTicketButton = (selectedTicketNumber) => {
    const ticketButton = document.getElementById(`ticket-search-context-${selectedTicketNumber}`);
    if (!ticketButton) return;
    ticketButton.classList.add(activeTicketButtonClass);
}

const deactiveTicketButton = (selectedTicketNumber) => {
    const ticketButton = document.getElementById(`ticket-search-context-${selectedTicketNumber}`);
    if (!ticketButton) return;
    ticketButton.classList.remove(activeTicketButtonClass);
}

const removeSelectNumber = (selectedTicketNumber) => {
    const index = userTicketNumbers.indexOf(selectedTicketNumber);
    if (index === -1) return;
    userTicketNumbers.splice(index, 1);
    const selectedNumbersTicketContainer = document.getElementById("my-numbers");
    const selectedTicketNumberCard = document.getElementById(`ticket-to-buy-${selectedTicketNumber}`);
    deactiveTicketButton(selectedTicketNumber);
    selectedNumbersTicketContainer.removeChild(selectedTicketNumberCard);
    if (userTicketNumbers.length === 0)
        showWarningSelectNumbers();
    checkForToggleBuyButtonVisibility();
}

const addSelectedNumber = (selectedTicketNumber) => {
    const selectedNumbersTicketContainer = document.getElementById("my-numbers");

    const formattedNumber = String(selectedTicketNumber).padStart(4, '0');

    if (!userTicketNumbers.includes(selectedTicketNumber)) {
        activeTicketButton(selectedTicketNumber);
        userTicketNumbers.push(selectedTicketNumber);
        const new_card_ticket = document.createElement('div');
        new_card_ticket.id = `ticket-to-buy-${selectedTicketNumber}`;
        new_card_ticket.innerHTML = formattedNumber;
        new_card_ticket.classList.add('card-selected-number');
        new_card_ticket.addEventListener("click", () => removeSelectNumber(selectedTicketNumber));
        selectedNumbersTicketContainer.appendChild(new_card_ticket);
        hideWarningSelectNumbers();
        hideActionButtons();
        checkForToggleBuyButtonVisibility();
    }
}

// javascript logic for lucky roulette
/**
 * Generates a random permutation of numbers from 0 to 9.
 * 
 * @returns {number[]} An array of numbers from 0 to 9 in random order.
 */
const getRandomNumber = () => {
    const numbers = Array.from({ length: 10 }, (_, i) => i);
    for (let i = numbers.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [numbers[i], numbers[j]] = [numbers[j], numbers[i]];
    }
    return numbers;
};

/**
 * Creates the HTML content for a reel.
 * 
 * @returns {string} The HTML content with divs for each number.
 */
const createReelContent = () => {
    return getRandomNumber()
        .map((value, index) =>
            `<div data-number="${value}" style="transform: rotateX(${index * 36}deg) translateZ(75px);">${value}</div>`)
        .join('');
};

/**
 * Initializes the reels by setting their HTML content and initial data attributes.
 */
const initReels = () => {
    const reelIds = ['reel1', 'reel2', 'reel3', 'reel4'];
    reelIds.forEach(reelId => {
        const reel = document.getElementById(reelId);
        if (reel) {
            reel.innerHTML = createReelContent();
            reel.setAttribute('data-angle', '0');
        }
    });
};

/**
 * Gets the front number of a reel based on its current rotation angle.
 * 
 * @param {HTMLElement} reel - The reel element.
 * @returns {string} The number currently at the front of the reel.
 */
const getFrontNumber = (reel) => {
    const currentAngle = parseFloat(reel.getAttribute('data-angle'));
    const normalizedAngle = currentAngle % 360;
    const index = (10 - normalizedAngle / 36) % 10;
    return reel.children[Math.round(index)].getAttribute('data-number');
};

/**
 * Rotates a reel by 36 degrees.
 * 
 * @param {HTMLElement} reel - The reel element to rotate.
 */
const rotateReel = (reel) => {
    let currentAngle = parseFloat(reel.getAttribute('data-angle'));
    currentAngle -= 36;
    reel.setAttribute('data-angle', currentAngle);

    Array.from(reel.children).forEach(child => {
        const angle = parseFloat(child.style.transform.match(/rotateX\(([-\d.]+)deg\)/)[1]) - 36;
        child.style.transform = `rotateX(${angle}deg) translateZ(75px)`;
        const normalizedAngle = angle % 360;
        if (normalizedAngle === 0) {
            child.style.color = "#00a9be";
        } else {
            child.style.color = 'grey';
        }
    });
};

/**
 * Starts the rotation of a reel to reach a target number.
 * 
 * @param {string} id - The ID of the reel element.
 * @param {string} targetNumber - The target number to stop at.
 */
const startRotation = (id, targetNumber) => {
    const reel = document.getElementById(id);
    const rotationInterval = 100;
    const rotationDuration = 2000;

    const interval = setInterval(() => rotateReel(reel), rotationInterval);

    setTimeout(() => {
        clearInterval(interval);
        let frontNumber = getFrontNumber(reel);
        const stopInterval = setInterval(() => {
            if (frontNumber == targetNumber) {
                clearInterval(stopInterval);
                showActionButtons();
            } else {
                rotateReel(reel);
                frontNumber = getFrontNumber(reel);
            }
        }, rotationInterval);
    }, rotationDuration);

};

/**
 * Rotates multiple reels to reach their respective target numbers.
 * 
 * @param {number[]} arrayNumbersTickets - An array of target numbers for each reel.
 */
const RotateButton = (arrayNumbersTickets) => {
    arrayNumbersTickets.forEach((value, index) => {
        startRotation(`reel${index + 1}`, value.toString());
    });
};

const setGlobalLotteryId = (lotteryId) => { gLotteryId = lotteryId; console.log(gLotteryId); }

/**
 * Gets the current lottery ID from the template.
 * @returns {number} The lottery ID as an integer.
 */
const getCurrentLotteryId = () => {
    const lotteryId = parseInt(`${gLotteryId}`);
    return lotteryId;
};

/**
 * Builds the endpoint URL for fetching a random available ticket.
 * @returns {string} The endpoint URL.
 */
const buildEndpointRandomTicketNumber = () => {
    const lotteryId = getCurrentLotteryId();
    const endpointUrl = `/api/lottery/${lotteryId}/random_available_ticket/`;
    return endpointUrl;
};

/**
 * Handles the response from a fetch request and throws an error if the response is not OK.
 * @param {Response} response - The response object from the fetch request.
 * @returns {Promise} The JSON representation of the response.
 * @throws {Error} If the response is not OK.
 */
const handleBadRequestResponse = (response) => {
    if (!response.ok) throw new Error("Error while processing the request");
    return response.json();
};

/**
 * Hide the action buttons after the first response is received.
 */
const hideActionButtons = () => {
    const actionButtons = document.getElementById("actionButtons");
    actionButtons.style.height = "0rem";
};


/**
 * Shows the action buttons after the first response is received.
 */
const showActionButtons = () => {
    const actionButtons = document.getElementById("actionButtons");
    actionButtons.style.height = "auto";
};

/**
 * Changes the text of the spin button to "Girar de nuevo" after the first response is received.
 */
const changeSpinButtonText = () => {
    document.getElementById("spinButton").textContent = "Girar de nuevo";
};

/**
 * Formats the ticket number with leading zeros to ensure a consistent display format.
 * @param {number} ticket_number - The ticket number to be formatted.
 * @returns {string} The formatted ticket number.
 */
const formattingTicketNumber = (ticket_number) =>
    ticket_number.toString().padStart(4, "0");



/**
 * Updates the reservation link with the ticket number obtained from the spin.
 * @param {number} ticketNumber - The ticket number obtained from the spin.
 */
const updateReservationLink = (ticketNumber) => {
    const reserveTicketLink = document.getElementById("reserveTicketLink");
};

let lastClickAddToShopCartEventListener = undefined;

/**
 * Updates the buy ticket link with the ticket number obtained from the spin.
 * @param {number} ticketNumber - The ticket number obtained from the spin.
 */
const updateBuyTicketLink = (ticketNumber) => {
    const buyTicketLink = document.getElementById("buyTicketLink");
    const lotteryId = getCurrentLotteryId();
    buyTicketLink.dataset.ticketNumber = `${ticketNumber}`;

    if (lastClickAddToShopCartEventListener)
        buyTicketLink.removeEventListener('click', lastClickAddToShopCartEventListener);

    lastClickAddToShopCartEventListener = () => {
        addSelectedNumber(ticketNumber);
    }

    buyTicketLink.addEventListener('click', lastClickAddToShopCartEventListener);
};


/**
 * Handles the response from the spin roulette request, updating the ticket numbers display and showing action buttons.
 * @param {Object} data - The response data containing the ticket number.
 */
const handleRequestResponseSpinRoulette = (data) => {
    const ticketNumber = formattingTicketNumber(data.ticket_number);
    RotateButton(Array.from(ticketNumber))
    changeSpinButtonText();
    updateReservationLink(data.ticket_number);
    updateBuyTicketLink(data.ticket_number);
};

/**
 * Handles any exceptions or errors that occur during the request process.
 * @param {Error} error - The error object containing details of the error.
 */
const handleCatchExceptionErrorRequest = (error) => {
    console.error("Error:", error.message);
};

/**
 * Initiates the spin roulette request to fetch a random available ticket.
 */
const performSpinRouletteRequest = () => {
    hideActionButtons();
    const endpointUrl = buildEndpointRandomTicketNumber();
    fetch(endpointUrl)
        .then(handleBadRequestResponse)
        .then(handleRequestResponseSpinRoulette)
};

document
    .getElementById("spinButton")
    .addEventListener("click", performSpinRouletteRequest);

// Initialize the reels when the script is loaded.
initReels();