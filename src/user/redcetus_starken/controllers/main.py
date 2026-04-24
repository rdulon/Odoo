from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleStarken(WebsiteSale):

    @http.route()
    def shop_address_submit(
        self,
        partner_id=None,
        address_type='billing',
        use_delivery_as_billing=None,
        callback=None,
        **form_data
    ):
        commune_id = form_data.get("starken_commune_id")

        response = super().shop_address_submit(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            **form_data
        )

        if commune_id and partner_id:
            try:
                partner = request.env["res.partner"].sudo().browse(int(partner_id))
                partner.write({"starken_commune_id": int(commune_id)})
            except (TypeError, ValueError):
                pass

        return response