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

        return request.render(
            "redcetus_brand.brand_product_listing",
            {
                "brand": brand,
                "products": products,
            },
        )

    @http.route(
        ["/shop/marcas"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def shop_brands(self, **kwargs):
        brands = request.env["product.brand"].sudo().search(
            [("active", "=", True),
             ("product_ids.is_published", "=", True),],
            order="name asc",
        )

        return request.render(
            "redcetus_brand.brand_list_page",
            {"brands": brands},
        )