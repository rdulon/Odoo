from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


if "starken_commune_id" not in WebsiteSale.WRITABLE_PARTNER_FIELDS:
    WebsiteSale.WRITABLE_PARTNER_FIELDS.append("starken_commune_id")


class StarkenCheckoutController(http.Controller):

    @http.route(
        "/starken/checkout/set_commune",
        type="jsonrpc",
        auth="public",
        website=True,
    )
    def set_checkout_commune(self, partner_id=None, commune_id=None):
        try:
            commune_id = int(commune_id or 0)
        except (TypeError, ValueError):
            commune_id = 0

        if not commune_id:
            return {"success": False}

        order = request.website.sale_get_order()
        if not order:
            return {"success": False}

        partner = order.partner_shipping_id or order.partner_id
        if partner and partner.exists():
            partner.sudo().write({"starken_commune_id": commune_id})
            return {"success": True}

        return {"success": False}