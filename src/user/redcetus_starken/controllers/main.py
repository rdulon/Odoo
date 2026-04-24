import logging

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class StarkenCustomerPortal(CustomerPortal):

    @http.route('/shop/address/submit', type='http', auth='public', methods=['POST'], website=True)
    def address_submit(self, **post):
        _logger.warning("STARKEN ADDRESS SUBMIT POST: %s", post)

        commune_id = post.get("starken_commune_id")

        response = super().address_submit(**post)

        if commune_id:
            try:
                commune_id = int(commune_id)
            except (TypeError, ValueError):
                commune_id = False

        if commune_id:
            partner = False

            partner_id = post.get("partner_id")
            if partner_id:
                try:
                    partner = request.env["res.partner"].sudo().browse(int(partner_id))
                except (TypeError, ValueError):
                    partner = False

            if not partner or not partner.exists():
                order = request.website.sale_get_order()
                partner = order.partner_shipping_id or order.partner_id if order else False

            if partner and partner.exists():
                partner.sudo().write({"starken_commune_id": commune_id})
                _logger.warning("STARKEN COMMUNE SAVED OK ON PARTNER %s", partner.id)

        return response