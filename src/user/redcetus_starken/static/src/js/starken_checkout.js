/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector('form[name="address_form"]');
    if (!form) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        const select = form.querySelector('select[name="starken_commune_id"]');
        if (!select || !select.value) {
            return;
        }

        event.preventDefault();

        try {
            await rpc("/starken/checkout/set_commune", {
                commune_id: select.value,
            });
        } catch (error) {
            console.error("Error saving Starken commune", error);
        }

        form.submit();
    });
});