from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain
from odoo.http import request


class WebsiteSaleBrandFilter(WebsiteSale):

    def _add_search_subdomains_hook(self, search):
        brand_slug = request.params.get("brand")
        if not brand_slug:
            return []

        brand = request.env["product.brand"].sudo().search(
            [("website_slug", "=", brand_slug), ("active", "=", True)],
            limit=1,
        )
        if not brand:
            return []

        return Domain("brand_id", "=", brand.id)