from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSaleBrandFilter(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super()._get_search_domain(
            search,
            category,
            attrib_values,
            search_in_description=search_in_description,
        )

        brand_slug = request.params.get("brand")
        if brand_slug:
            brand = request.env["product.brand"].sudo().search(
                [("website_slug", "=", brand_slug), ("active", "=", True)],
                limit=1,
            )
            if brand:
                domain.append(("brand_id", "=", brand.id))

        return domain