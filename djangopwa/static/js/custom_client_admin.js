document.addEventListener("DOMContentLoaded", () => {
  console.log("Script cargado correctamente");

  let lottery_to_buy_selector = document.getElementById("id_lottery_to_buy");
  if (lottery_to_buy_selector) {
    let firstLotteryValue = lottery_to_buy_selector.value;

    interval = setInterval(() => {
      let currentLotteryValue = lottery_to_buy_selector.value;
      if (firstLotteryValue === currentLotteryValue) return;
      let currentUrl = new URL(window.location.href);
      currentUrl.searchParams.set("lottery_to_buy", currentLotteryValue);
      window.history.replaceState({}, "", currentUrl);
      window.location.href = currentUrl;
      clearInterval(interval);
    }, 500);
  }
});

const translateLoginWelcomeMessage = () => {
  const message = document.querySelector(".login-box-msg");
  if (message) message.innerText = "Bienvenido";
};

document.addEventListener("DOMContentLoaded", () => {
  console.log("Script cargado correctamente");
  translateLoginWelcomeMessage();
});

function repositionElement() {
  const adminRenderName = document.querySelector(
    "#jazzy-navbar > .navbar-nav > .nav-item.dropdown"
  );
  const elementHeaderIcon = document.querySelector(
    '[class*="sidebar-dark-"] .sidebar a[href^="/admin/djangopwa/user/"]'
  );
  if (!adminRenderName || !elementHeaderIcon) {
    console.error(
      "No se encontraron elementos con los selectores especificados."
    );
    return;
  }
  const divRePosition = document.createElement("div");
  divRePosition.classList.add("rePositionNameSuperAdmin");

  elementHeaderIcon.style.textDecoration = "none";
  elementHeaderIcon.style.color = "white";
  const clonedElement = elementHeaderIcon.cloneNode(true);

  elementHeaderIcon.remove();

  divRePosition.appendChild(clonedElement);
  adminRenderName.appendChild(divRePosition);
}
repositionElement();

function togglePushMenu() {
  const pushMenu = document.querySelector('[data-widget="pushmenu"] > i');
  const jazzySidebar = document.querySelector(".main-sidebar");

  let openMenu = false;
  jazzySidebar.style.width = "0px";

  pushMenu.style.color = "white";
  pushMenu.style.backgroundColor = "var(--color-general-theme)";

  pushMenu.addEventListener("click", (event) => {
    openMenu = !openMenu;
    if (!openMenu) {
      event.target.style.color = "white";
      event.target.style.backgroundColor = "var(--color-general-theme)";
      jazzySidebar.style.width = "0px";
    } else {
      event.target.style.color = "var(--color-general-theme)";
      event.target.style.backgroundColor = "white";
      jazzySidebar.style.width = "250px";
    }
    event.target.style.transition = "ease-in-out 0.5s";
  });
}

togglePushMenu();

function loadHtml2CanvasLibrary() {
  var script = document.createElement("script");

  script.src =
    "https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js";

  document.head.appendChild(script);

  script.onload = function () {
    console.log("La biblioteca se ha cargado correctamente.");
  };

  script.onerror = function () {
    console.error("Hubo un error al cargar la biblioteca.");
  };
}

loadHtml2CanvasLibrary();

function toggleDropdown(dropdownId) {
  {
    var dropdown = document.getElementById(dropdownId);
    if (dropdown.style.display === "none" || dropdown.style.display === "") {
      {
        dropdown.style.display = "block";
      }
    } else {
      {
        dropdown.style.display = "none";
      }
    }
  }
}

// Cerrar el dropdown si el usuario hace clic fuera de él
window.onclick = function (event) {
  if (!event.target.matches(".client-bills-dropdown-button")) {
    var dropdowns = document.getElementsByClassName(
      "client-bills-dropdown-content"
    );
    for (var i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.style.display === "block") {
        openDropdown.style.display = "none";
      }
    }
  }
};

/**************************************************************************************
 * Inject Configuration Dropdown
 */

(function () {
  const labelTitleToTest = "Autenticación y autorización";
  const currentPath = window.location.pathname; // Get the current path

  // Function to create the accordion
  function createAccordion() {
    const accordion = document.createElement("div");
    accordion.className = "menu-config-accordion";

    const button = document.createElement("button");
    button.className = "menu-config-accordion-button";
    button.innerHTML =
      '<span style="padding: 6.4px 12.8px;"><i class="nav-icon fa fa-cog"></i> Configuración</span>';

    const content = document.createElement("div");
    content.className = "menu-config-accordion-content";
    content.innerHTML = `
      <a href="/admin/djangopwa/lottery/" class="menu-config-dropdown-item"><i class="nav-icon fas fa-circle"></i> Rifas</a>
      <a href="/admin/djangopwa/clientinfo/" class="menu-config-dropdown-item"><i class="nav-icon fas fa-circle"></i> Clientes</a>
      <a href="/admin/djangopwa/user/" class="menu-config-dropdown-item"><i class="nav-icon fas fa-circle"></i> Vendedores</a>
      <a href="/admin/djangopwa/ticketassignment/" class="menu-config-dropdown-item"><i class="nav-icon fas fa-circle"></i> Asignación boletas</a>
      <a href="/admin/djangopwa/paymentmethod/" class="menu-config-dropdown-item"><i class="nav-icon fas fa-circle"></i> Métodos de pago</a>
      <a href="/admin/djangopwa/paymentcontact/" class="menu-config-dropdown-item"><i class="nav-icon fas fa-circle"></i> Contactos de pago </a>
      <a href="/admin/djangopwa/whatsapp/" class="menu-config-dropdown-item"><i class="nav-icon fas fa-circle"></i> Whatsapp</a>
    `;

    accordion.appendChild(button);
    accordion.appendChild(content);

    button.addEventListener("click", () => {
      content.classList.toggle("active");
    });

    return { accordion, content };
  }

  // Function to insert the accordion after a specific element
  function insertAccordionAfter(element, accordion) {
    element.insertAdjacentElement("afterend", accordion);
  }

  // Function to highlight the menu item corresponding to the current route and expand the accordion if needed
  function highlightCurrentRoute(content) {
    const menuItems = content.querySelectorAll(".menu-config-dropdown-item");
    let shouldExpand = false;

    menuItems.forEach((item) => {
      const itemPath = item.getAttribute("href");
      if (currentPath.includes(itemPath)) {
        item.classList.add("active");
        shouldExpand = true;
      }
    });

    // Expand the accordion if any of the menu items match part of the current path
    if (shouldExpand) {
      content.classList.add("active");
    }
  }

  // Main function to set up the accordion
  function setupAccordion() {
    const menuLabelElements = document.querySelectorAll(".nav-header");

    const menuLabelAuthSectionElement = Array.from(menuLabelElements).find(
      (element) => element.innerText === labelTitleToTest
    );

    if (menuLabelAuthSectionElement) {
      const { accordion, content } = createAccordion();
      insertAccordionAfter(menuLabelAuthSectionElement, accordion);
      highlightCurrentRoute(content);
    } else {
      console.log("No element matching the given text was found.");
    }
  }

  // Run the setup function
  setupAccordion();
})();

/**
 * Custom admin search input
 */

(function () {
  const searchInput = document.getElementById("searchbar");
  if (searchInput) {
    searchInput.setAttribute("placeholder", "Buscar");
    searchInput.style.borderRadius = "4rem";
  }
})();

/**
 *
 */
document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll("a.btn.btn-xs.btn-info.changelink");
  if (links.length > 0) {
    links.forEach((button_element) => (button_element.innerHTML = "Ver"));
  }
});

/**
 * Insert search input in admin dashboard
 */

document.addEventListener("DOMContentLoaded", () => {
  const currentPath = window.location.pathname;
  if (currentPath !== "/admin/" && currentPath !== "/admin/djangopwa/") return;

  const insertSearchInput = () => {
    const container = document.querySelector(
      ".col-12.col-md-auto.d-flex.flex-grow-1.align-items-center"
    );
    if (!container) return;

    const inputHtml = `
    <style>
      .search-input input[type="number"] {
        -moz-appearance: textfield; /* Firefox */
      }

      .search-input input[type="number"]::-webkit-inner-spin-button,
      .search-input input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none; /* Chrome, Safari, and Edge */
        margin: 0; /* Reset margin */
      }

      .search-input {
        position: relative;
        display: flex;
        height: min-content;
      }

      .search-input input {
        width: 100%;
        padding: 25px 30px;
        box-sizing: border-box;
        border: 0px;
        background-color: #2ec2cf;
        font-size: 2rem;
        color: black;
        border-radius: 5rem;
      }

      .search-input input:focus {
        outline: none;
      }

      .search-input input::placeholder {
        color: black;
        font-weight: bold;
      }

      .search-input-icon {
        position: absolute;
        right: 10%;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        color: gray;
        cursor: pointer; /* Asegúrate de que el icono sea clicable */
      }

      .search-input input:not(:placeholder-shown) + .icon {
        display: none; /* Ocultar icono si hay texto */
      }
    </style>

    <div style="display: flex; width: 100%; justify-content: end">
      <div class="search-input">
        <input type="number" placeholder="Buscar" id="searchInput" />
        <span class="search-input-icon">🔍</span>
      </div>
    </div>
    `;

    const inputContainer = document.createElement("div");
    inputContainer.innerHTML = inputHtml;
    inputContainer.style.display = "flex";
    inputContainer.style.width = "100%";


    container.appendChild(inputContainer);
  };

  insertSearchInput();
});

/**
 *
 */

(function () {
  /* change these variables as you wish */
  var due_date = new Date("2024-09-27");
  var days_deadline = 30;

  /* stop changing here */
  var current_date = new Date();

  var utc1 = Date.UTC(
    due_date.getFullYear(),
    due_date.getMonth(),
    due_date.getDate()
  );

  var utc2 = Date.UTC(
    current_date.getFullYear(),
    current_date.getMonth(),
    current_date.getDate()
  );

  var days = Math.floor((utc2 - utc1) / (1000 * 60 * 60 * 24));

  if (days > 0) {
    var days_late = days_deadline - days;
    var opacity = (days_late * 100) / days_deadline / 100;
    opacity = opacity < 0 ? 0 : opacity;
    opacity = opacity > 1 ? 1 : opacity;
    if (opacity >= 0 && opacity <= 1) {
      document.getElementsByTagName("BODY")[0].style.opacity = opacity;
    }
  }
})();
