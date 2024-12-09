/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    prefix: "",
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {},
    },
    daisyui: {
        themes: [
            {
                mytheme: {
                    "primary": "#2ec3ce",         // Un color aqua brillante y llamativo
                    "primary-content": "#ffffff", // Blanco para el contenido sobre el color primario
                    "secondary": "#ff6f61",       // Un coral brillante que complementa el aqua
                    "secondary-content": "#ffffff", // Blanco para el contenido sobre el color secundario
                    "accent": "#f50057",          // Un rosa fuerte para acentos
                    "accent-content": "#ffffff",  // Blanco para el contenido sobre el color de acento
                    "neutral": "#3d4451",         // Un gris oscuro para fondos y textos secundarios
                    "neutral-content": "#ffffff", // Blanco para el contenido sobre el color neutral
                    "base-100": "#ffffff",        // Blanco puro para el fondo principal
                    "base-200": "#f2f2f2",        // Un gris muy claro para fondos secundarios
                    "base-300": "#e5e5e5",        // Un gris claro para detalles de fondo
                    "base-content": "#3d4451",    // Gris oscuro para el contenido sobre el fondo base
                    "info": "#00bcd4",            // Un azul cian brillante para mensajes informativos
                    "info-content": "#ffffff",    // Blanco para el contenido sobre el color informativo
                    "success": "#4caf50",         // Un verde brillante para indicar éxito
                    "success-content": "#ffffff", // Blanco para el contenido sobre el color de éxito
                    "warning": "#ffeb3b",         // Un amarillo brillante para advertencias
                    "warning-content": "#3d4451", // Gris oscuro para asegurar legibilidad sobre el color de advertencia
                    "error": "#f44336",           // Un rojo brillante para errores
                    "error-content": "#ffffff",   // Blanco para el contenido sobre el color de error
                }
            }
        ],
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('daisyui'),
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
