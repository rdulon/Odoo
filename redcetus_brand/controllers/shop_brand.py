from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from werkzeug.exceptions import NotFound


def sitemap_shop_by_brand(env, rule, qs):
    brands = env["product.brand"].sudo().search([
        ("active", "=", True),
        ("product_ids.is_published", "=", True),
        ("product_ids.sale_ok", "=", True),
    ], order="name asc")

    for brand in brands:
        if brand.website_slug:
            yield {"loc": f"/shop/marca/{brand.website_slug}"}


class WebsiteSaleBrand(WebsiteSale):

    @http.route(
        ["/shop/marca/<string:brand_slug>"],
        type="http",
        auth="public",
        website=True,
        sitemap=sitemap_shop_by_brand,
    )
    def shop_by_brand(
        self,
        brand_slug,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        tags="",
        **post
    ):
        # Buscar la marca
        brand = request.env["product.brand"].sudo().search(
            [("website_slug", "=", brand_slug), ("active", "=", True)],
            limit=1,
        )
        if not brand:
            raise NotFound()

        # Guardar contexto para el filtro
        request.update_context(brand_slug=brand_slug)

        # Asegurar que el parámetro llegue al shop
        post = dict(post)
        post["brand"] = brand_slug

        # Llamar al shop estándar de Odoo
        response = super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            tags=tags,
            **post,
        )

        # Pasar datos adicionales al template
        if hasattr(response, "qcontext"):
            response.qcontext.update({
                "current_brand": brand,
                "brand_slug": brand_slug,
            })

        return response

    @http.route(
        ["/shop/marcas"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def shop_brands(self, **kwargs):
        brands = request.env["product.brand"].sudo().search(
            [
                ("active", "=", True),
                ("product_ids.is_published", "=", True),
                ("product_ids.sale_ok", "=", True),
            ],
            order="name asc",
        )

        return request.render(
            "redcetus_brand.brand_list_page",
            {"brands": brands},
        )