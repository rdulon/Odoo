from odoo.addons.website_sale.controllers.main import WebsiteSale


if "starken_commune_id" not in WebsiteSale.WRITABLE_PARTNER_FIELDS:
    WebsiteSale.WRITABLE_PARTNER_FIELDS.append("starken_commune_id")