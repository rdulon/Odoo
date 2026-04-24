import logging

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


if "starken_commune_id" not in WebsiteSale.WRITABLE_PARTNER_FIELDS:
    WebsiteSale.WRITABLE_PARTNER_FIELDS.append("starken_commune_id")


class WebsiteSaleStarken(WebsiteSale):

    @http.route()
    def address_submit(self, **post):
        _logger.warning("STARKEN CHECKOUT POST: %s", post)

        response = super().address_submit(**post)

        commune_id = post.get("starken_commune_id")
        _logger.warning("STARKEN COMMUNE RECEIVED: %s", commune_id)

        if commune_id:
            try:
                commune_id = int(commune_id)
            except (TypeError, ValueError):
                commune_id = False

        if commune_id:
            order = request.website.sale_get_order()
            partner = order.partner_shipping_id or order.partner_id
            _logger.warning("STARKEN PARTNER TO UPDATE: %s", partner)

            if partner and partner.exists():
                partner.sudo().write({"starken_commune_id": commune_id})
                _logger.warning("STARKEN COMMUNE SAVED OK")

        return response