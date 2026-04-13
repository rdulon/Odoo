from odoo import fields, models


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"
    _order = "name"

    name = fields.Char(string="Brand", required=True)
    active = fields.Boolean(default=True)
    image_128 = fields.Image(string="Logo")
    description = fields.Html(string="Description")

    product_ids = fields.One2many(
        "product.template",
        "brand_id",
        string="Products",
    )

    _sql_constraints = [
        ("product_brand_name_uniq", "unique(name)", "The brand already exists."),
    ]