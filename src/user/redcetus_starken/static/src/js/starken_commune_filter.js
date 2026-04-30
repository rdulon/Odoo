/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

function initStarkenForm() {
    const countrySelect = document.querySelector('select[name="country_id"]');
    const stateSelect = document.querySelector('select[name="state_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');
    const cityInput = document.querySelector('input[name="city"]');
    const zipInput = document.querySelector('input[name="zip"]');

    if (!countrySelect || !stateSelect || !communeSelect) {
        return;
    }

    const communeWrapper = communeSelect.closest('.mb-3, .form-group, div');
    const cityWrapper = cityInput ? cityInput.closest('.mb-3, .form-group, div') : null;
    const zipWrapper = zipInput ? zipInput.closest('.mb-3, .form-group, div') : null;

    function isChile() {
        const selectedOption = countrySelect.options[countrySelect.selectedIndex];
        const countryText = selectedOption ? selectedOption.textContent.trim().toLowerCase() : "";
        return countryText.includes("chile");
    }

    function toggleFieldsByCountry() {
        if (isChile()) {
            if (communeWrapper) communeWrapper.style.display = "";
            if (cityWrapper) cityWrapper.style.display = "none";
            if (zipWrapper) zipWrapper.style.display = "none";
        } else {
            if (communeWrapper) communeWrapper.style.display = "none";
            if (cityWrapper) cityWrapper.style.display = "";
            if (zipWrapper) zipWrapper.style.display = "";
        }
    }

    async function loadCommunesByState(stateId, selectedCommuneId = null) {
        communeSelect.innerHTML = '<option value="">Seleccione comuna</option>';

        if (!stateId) return;

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

    // Región → Comunas
    stateSelect.addEventListener("change", () => {
        loadCommunesByState(stateSelect.value);
    });

    // Comuna → City + ZIP
    communeSelect.addEventListener("change", () => {
        const selected = communeSelect.options[communeSelect.selectedIndex];

        if (isChile() && selected) {
            if (cityInput) {
                cityInput.value = selected.dataset.name || selected.textContent;
            }
            if (zipInput && !zipInput.value) {
                zipInput.value = "0000000";
            }
        }
    });

    // País → comportamiento
    countrySelect.addEventListener("change", () => {
        toggleFieldsByCountry();

        if (!isChile()) {
            communeSelect.value = "";
        }
    });

    // Init
    toggleFieldsByCountry();

    if (stateSelect.value) {
        loadCommunesByState(stateSelect.value, communeSelect.value);
    }
}

// Reintenta inicialización (porque Odoo carga dinámico)
document.addEventListener("DOMContentLoaded", initStarkenForm);
document.addEventListener("click", () => setTimeout(initStarkenForm, 300));