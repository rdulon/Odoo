from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleStarken(WebsiteSale):

    if "starken_commune_id" not in WebsiteSale.WRITABLE_PARTNER_FIELDS:
        WebsiteSale.WRITABLE_PARTNER_FIELDS.append("starken_commune_id")

    @route('/shop/address/submit', type='http', auth='public', methods=['POST'], website=True, sitemap=False)
    def address_submit(self, **post):
        response = super().address_submit(**post)

        commune_id = post.get("starken_commune_id")
        if commune_id:
            try:
                commune_id = int(commune_id)
            except (TypeError, ValueError):
                commune_id = False

        if commune_id:
            order = request.website.sale_get_order()
            partner = order.partner_shipping_id or order.partner_id
            if partner and partner.exists():
                partner.sudo().write({"starken_commune_id": commune_id})

        return response