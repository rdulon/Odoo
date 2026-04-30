/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

function isChile(countrySelect) {
    const selected = countrySelect.options[countrySelect.selectedIndex];
    const text = selected ? selected.textContent.toLowerCase() : "";
    return text.includes("chile");
}

function getWrapper(el) {
    if (!el) return null;
    return el.closest(".mb-3, .col-lg-4, .col-lg-6, .col-md-6, div");
}

function applyVisibility() {
    const countrySelect = document.querySelector('select[name="country_id"]');
    const stateSelect = document.querySelector('select[name="state_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');
    const cityInput = document.querySelector('input[name="city"]');
    const zipInput = document.querySelector('input[name="zip"]');

    if (!countrySelect || !communeSelect) return;

    const chile = isChile(countrySelect);

    const communeWrapper = getWrapper(communeSelect);
    const cityWrapper = getWrapper(cityInput);
    const zipWrapper = getWrapper(zipInput);

    if (communeWrapper) {
        communeWrapper.style.display = chile ? "" : "none";
    }

    if (cityWrapper) {
        cityWrapper.style.display = chile ? "none" : "";
    }

    if (zipWrapper) {
        zipWrapper.style.display = chile ? "none" : "";
    }

    // limpiar comuna si no es Chile
    if (!chile) {
        communeSelect.value = "";
    }

    // autocompletar city + zip
    if (chile) {
        const selected = communeSelect.options[communeSelect.selectedIndex];

        if (selected && selected.value) {
            if (cityInput) {
                cityInput.value = selected.textContent;
            }
        }

        if (zipInput && !zipInput.value) {
            zipInput.value = "0000000";
        }
    }
}

async function loadCommunes() {
    const stateSelect = document.querySelector('select[name="state_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');
    const countrySelect = document.querySelector('select[name="country_id"]');

    if (!stateSelect || !communeSelect || !countrySelect) return;
    if (!isChile(countrySelect)) return;

    const stateId = stateSelect.value;

    communeSelect.innerHTML = '<option value="">Seleccione comuna</option>';

    if (!stateId) return;

    const communes = await rpc("/starken/communes/by_state", {
        state_id: stateId,
    });

    for (const commune of communes) {
        const option = document.createElement("option");
        option.value = commune.id;
        option.textContent = commune.name;
        communeSelect.appendChild(option);
    }
}

function initEvents() {
    const countrySelect = document.querySelector('select[name="country_id"]');
    const stateSelect = document.querySelector('select[name="state_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');

    if (!countrySelect || !stateSelect || !communeSelect) return;

    if (countrySelect.dataset.starkenInit) return;
    countrySelect.dataset.starkenInit = "1";

    countrySelect.addEventListener("change", () => {
        applyVisibility();
        loadCommunes();
    });

    stateSelect.addEventListener("change", () => {
        loadCommunes();
    });

    communeSelect.addEventListener("change", () => {
        applyVisibility();
    });
}

// 🔥 CLAVE: detectar re-render de Odoo
const observer = new MutationObserver(() => {
    applyVisibility();
    initEvents();
});

observer.observe(document.body, {
    childList: true,
    subtree: true,
});

// Init inicial
document.addEventListener("DOMContentLoaded", () => {
    applyVisibility();
    initEvents();
});