/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

function initStarkenCommuneFilter() {
    const stateSelect = document.querySelector('select[name="state_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');

    if (!stateSelect || !communeSelect || communeSelect.dataset.starkenFilterReady) {
        return;
    }

    communeSelect.dataset.starkenFilterReady = "1";

    async function loadCommunesByState(stateId, selectedCommuneId = null) {
        communeSelect.innerHTML = '<option value="">Seleccione comuna</option>';

        if (!stateId) {
            return;
        }

        const communes = await rpc("/starken/communes/by_state", {
            state_id: stateId,
        });

        for (const commune of communes) {
            const option = document.createElement("option");
            option.value = commune.id;
            option.textContent = commune.name;

            if (selectedCommuneId && String(commune.id) === String(selectedCommuneId)) {
                option.selected = true;
            }

            communeSelect.appendChild(option);
        }
    }

    const currentCommuneId = communeSelect.value;

    stateSelect.addEventListener("change", () => {
        loadCommunesByState(stateSelect.value);
    });

    if (stateSelect.value) {
        loadCommunesByState(stateSelect.value, currentCommuneId);
    }
}

document.addEventListener("DOMContentLoaded", initStarkenCommuneFilter);
document.addEventListener("click", () => setTimeout(initStarkenCommuneFilter, 300));