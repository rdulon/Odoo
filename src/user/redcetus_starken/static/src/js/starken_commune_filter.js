/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

document.addEventListener("DOMContentLoaded", () => {
    const stateSelect = document.querySelector('select[name="state_id"]');
    const communeSelect = document.querySelector('select[name="starken_commune_id"]');

    if (!stateSelect || !communeSelect) {
        return;
    }

    const currentCommuneId = communeSelect.value;

    async function loadCommunesByState(stateId, selectedCommuneId = null) {
        communeSelect.innerHTML = "";

        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "Seleccione comuna";
        communeSelect.appendChild(defaultOption);

        if (!stateId) {
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

                if (selectedCommuneId && String(commune.id) === String(selectedCommuneId)) {
                    option.selected = true;
                }

                communeSelect.appendChild(option);
            }
        } catch (error) {
            console.error("Error loading Starken communes", error);
        }
    }

    stateSelect.addEventListener("change", () => {
        loadCommunesByState(stateSelect.value);
    });

    if (stateSelect.value) {
        loadCommunesByState(stateSelect.value, currentCommuneId);
    }
});