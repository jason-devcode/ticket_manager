const changeElementInnerText = (selector, newText) => {
    const element = document.querySelector(selector);
    if (element) element.innerText = newText;
}

const traslateTextMessageUserCreation = () => changeElementInnerText(
    "form p.text-center", 
    "Primero, ingrese un nombre de usuario y contraseña. Luego, podrás editar más opciones de usuario."
);

const traslateTextTabImportantDates = () => changeElementInnerText(
    '[aria-controls="important-dates-tab"]', 
    "Fechas Importantes"
);

const traslateStaffFieldLabel = () => changeElementInnerText(
    '[for="id_is_staff"]',
    "Estado de personal"
);

const traslateStaffHelpBlock = () => {
    const element = document.querySelectorAll('.field-is_staff .row div .help-block')[1];
    console.log(element);
    element.innerText = "Designa al usuario como parte del personal, otorgandole accesos especiales de personal."
}

document.addEventListener('DOMContentLoaded', () => {
    traslateTextMessageUserCreation();
    traslateTextTabImportantDates();
    traslateStaffFieldLabel();
    traslateStaffHelpBlock();
})