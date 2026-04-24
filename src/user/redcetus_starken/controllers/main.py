import logging

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class StarkenAddressSubmit(http.Controller):

    @http.route('/shop/address/submit', type='http', auth='public', methods=['POST'], website=True)
    def starken_address_submit(self, **post):
        _logger.warning("STARKEN ADDRESS SUBMIT POST: %s", post)

        # Buscar el controller original ya registrado para esta ruta.
        # Si esto no funciona, usaremos el método interno que indiquen los logs.
        partner_id = post.get("partner_id")
        commune_id = post.get("starken_commune_id")

        # Guardar comuna antes del flujo estándar.
        if partner_id and commune_id:
            try:
                partner = request.env["res.partner"].sudo().browse(int(partner_id))
                commune_id = int(commune_id)
                if partner.exists():
                    partner.write({"starken_commune_id": commune_id})
                    _logger.warning("STARKEN COMMUNE SAVED OK ON PARTNER %s", partner.id)
            except Exception:
                _logger.exception("STARKEN ERROR SAVING COMMUNE")

        # Ejecutar el submit estándar desde CustomerPortal si existe.
        portal = CustomerPortal()
        if hasattr(portal, "address_submit"):
            return portal.address_submit(**post)

        # Fallback temporal: volver al checkout.
        return request.redirect("/shop/checkout")