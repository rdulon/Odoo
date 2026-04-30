/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

function getFieldWrapper(field) {
    if (!field) return null;
    return field.closest(".mb-3, .col-lg-4, .col-lg-6, .col-md-6, .form-group, div");
}

function initStarkenForm() {
    const countrySelect = document.querySelector('select[name="country_id"]');
    const stateSelect = document.querySelector('select[name="state_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');
    const cityInput = document.querySelector('input[name="city"]');
    const zipInput = document.querySelector('input[name="zip"]');

    if (!countrySelect || !stateSelect || !communeSelect) {
        return;
    }

    if (communeSelect.dataset.starkenInitialized === "1") {
        updateVisibility();
        return;
    }

    communeSelect.dataset.starkenInitialized = "1";

    const communeWrapper = getFieldWrapper(communeSelect);
    const cityWrapper = getFieldWrapper(cityInput);
    const zipWrapper = getFieldWrapper(zipInput);

    function isChile() {
        const selected = countrySelect.options[countrySelect.selectedIndex];
        const text = selected ? selected.textContent.trim().toLowerCase() : "";
        return text.includes("chile");
    }

    function updateVisibility() {
        const chile = isChile();

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

    async function loadCommunesByState(stateId, selectedCommuneId = null) {
        communeSelect.innerHTML = '<option value="">Seleccione comuna</option>';

        if (!stateId || !isChile()) {
            return;
        }

        const communes = await rpc("/starken/communes/by_state", {
            state_id: stateId,
        });

        for (const commune of communes) {
            const option = document.createElement("option");
            option.value = commune.id;
            option.textContent = commune.name;
            option.dataset.name = commune.name;

            if (selectedCommuneId && String(commune.id) === String(selectedCommuneId)) {
                option.selected = true;
            }

            communeSelect.appendChild(option);
        }
    }

    function syncCityZipFromCommune() {
        if (!isChile()) return;

        const selected = communeSelect.options[communeSelect.selectedIndex];

        if (selected && selected.value) {
            if (cityInput) {
                cityInput.value = selected.dataset.name || selected.textContent;
            }
            if (zipInput) {
                zipInput.value = zipInput.value || "0000000";
            }
        }
    }

    countrySelect.addEventListener("change", async () => {
        updateVisibility();
        await loadCommunesByState(stateSelect.value);
    });

    stateSelect.addEventListener("change", async () => {
        await loadCommunesByState(stateSelect.value);
    });

    communeSelect.addEventListener("change", syncCityZipFromCommune);

    updateVisibility();

    if (stateSelect.value) {
        loadCommunesByState(stateSelect.value, communeSelect.value).then(() => {
            updateVisibility();
            syncCityZipFromCommune();
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initStarkenForm();
    setTimeout(initStarkenForm, 500);
    setTimeout(initStarkenForm, 1500);
});

document.addEventListener("change", (event) => {
    if (
        event.target.matches('select[name="country_id"]') ||
        event.target.matches('select[name="state_id"]') ||
        event.target.matches('select[name="starken_commune_id"]')
    ) {
        setTimeout(initStarkenForm, 100);
    }
});