/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

let isLoadingCommunes = false;
let observerTimer = null;

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

    if (!chile) {
        communeSelect.value = "";
    }

    if (chile && zipInput && !zipInput.value) {
        zipInput.value = "0000000";
    }
}

async function loadCommunes(keepCurrent = false) {
    if (isLoadingCommunes) return;
    isLoadingCommunes = true;

    const stateSelect = document.querySelector('select[name="state_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');
    const countrySelect = document.querySelector('select[name="country_id"]');

    if (!stateSelect || !communeSelect || !countrySelect) {
        isLoadingCommunes = false;
        return;
    }

    if (!isChile(countrySelect)) {
        isLoadingCommunes = false;
        return;
    }

    const stateId = stateSelect.value;
    const currentCommuneId = keepCurrent ? communeSelect.value : "";

    communeSelect.innerHTML = '<option value="">Seleccione comuna</option>';

    if (!stateId) {
        isLoadingCommunes = false;
        return;
    }

    try {
        const communes = await rpc("/starken/communes/by_state", {
            state_id: stateId,
        });

        for (const commune of communes) {
            const option = document.createElement("option");
            option.value = commune.id;
            option.textContent = commune.name;

            if (currentCommuneId && String(commune.id) === String(currentCommuneId)) {
                option.selected = true;
            }

            communeSelect.appendChild(option);
        }
    } finally {
        isLoadingCommunes = false;
        applyVisibility();
    }
}

function syncCityZipFromCommune() {
    const countrySelect = document.querySelector('select[name="country_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');
    const cityInput = document.querySelector('input[name="city"]');
    const zipInput = document.querySelector('input[name="zip"]');

    if (!countrySelect || !communeSelect || !isChile(countrySelect)) return;

    const selected = communeSelect.options[communeSelect.selectedIndex];

    if (selected && selected.value) {
        if (cityInput) {
            cityInput.value = selected.textContent;
        }
        if (zipInput && !zipInput.value) {
            zipInput.value = "0000000";
        }
    }
}

function initEvents() {
    const countrySelect = document.querySelector('select[name="country_id"]');
    const stateSelect = document.querySelector('select[name="state_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');

    if (!countrySelect || !stateSelect || !communeSelect) return;

    if (countrySelect.dataset.starkenInit === "1") return;
    countrySelect.dataset.starkenInit = "1";

    countrySelect.addEventListener("change", () => {
        applyVisibility();
        loadCommunes(false);
    });

    stateSelect.addEventListener("change", () => {
        loadCommunes(false);
    });

    communeSelect.addEventListener("change", () => {
        syncCityZipFromCommune();
        applyVisibility();
    });

    communeSelect.addEventListener("focus", () => {
        loadCommunes(true);
    });

    communeSelect.addEventListener("click", () => {
        loadCommunes(true);
    });
}

const observer = new MutationObserver(() => {
    clearTimeout(observerTimer);
    observerTimer = setTimeout(() => {
        applyVisibility();
        initEvents();
        loadCommunes(true);
    }, 300);
});

observer.observe(document.body, {
    childList: true,
    subtree: true,
});

document.addEventListener("DOMContentLoaded", () => {
    applyVisibility();
    initEvents();
    loadCommunes(true);
});