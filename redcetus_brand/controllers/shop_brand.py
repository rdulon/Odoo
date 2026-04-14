from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound


class WebsiteSaleBrand(http.Controller):

    @http.route(
        ["/shop/marca/<string:brand_slug>"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def shop_by_brand(self, brand_slug, **kwargs):
        brand = request.env["product.brand"].sudo().search(
            [("website_slug", "=", brand_slug), ("active", "=", True)],
            limit=1,
        )
        if not brand:
            raise NotFound()

        products = request.env["product.template"].sudo().search(
            [
                ("sale_ok", "=", True),
                ("is_published", "=", True),
                ("brand_id", "=", brand.id),
            ],
            order="name asc",
        )

        values = {
            "brand": brand,
            "products": products,
        }

        return request.render("redcetus_brand.brand_product_listing", values)