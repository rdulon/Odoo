from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.fields import Domain
from odoo.http import request


class WebsiteSaleBrandFilter(WebsiteSale):

    def _get_shop_domain(self, search, category, attribute_value_dict, search_in_description=True):
        domain = super()._get_shop_domain(
            search,
            category,
            attribute_value_dict,
            search_in_description=search_in_description,
        )

        brand_slug = request.params.get("brand")
        if not brand_slug:
            return domain

        brand = request.env["product.brand"].sudo().search(
            [("website_slug", "=", brand_slug), ("active", "=", True)],
            limit=1,
        )
        if not brand:
            return domain

        return domain & Domain("brand_id", "=", brand.id)

    def _shop_lookup_products(self, options, post, search, website):
        fuzzy_search_term, product_count, search_result = super()._shop_lookup_products(
            options, post, search, website
        )

        brand_slug = request.params.get("brand")
        if not brand_slug:
            return fuzzy_search_term, product_count, search_result

        brand = request.env["product.brand"].sudo().search(
            [("website_slug", "=", brand_slug), ("active", "=", True)],
            limit=1,
        )
        if not brand:
            return fuzzy_search_term, product_count, search_result

        search_result = search_result.filtered(lambda p: p.brand_id.id == brand.id)
        product_count = len(search_result)

        return fuzzy_search_term, product_count, search_result