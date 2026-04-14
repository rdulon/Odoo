from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"
    _order = "name"

    name = fields.Char(string="Brand", required=True)
    active = fields.Boolean(default=True)
    image_128 = fields.Image(string="Logo")
    description = fields.Html(string="Description")

    website_slug = fields.Char(string="Website Slug", required=True, copy=False)
    website_url = fields.Char(
        string="Website URL",
        compute="_compute_website_url",
    )

    product_ids = fields.One2many(
        "product.template",
        "brand_id",
        string="Products",
    )

    _sql_constraints = [
        ("product_brand_name_uniq", "unique(name)", "The brand already exists."),
        ("product_brand_website_slug_uniq", "unique(website_slug)", "The website slug already exists."),
    ]

    @api.onchange("name")
    def _onchange_name_set_website_slug(self):
        for record in self:
            if record.name and not record.website_slug:
                record.website_slug = self._slugify(record.name)

    @api.model
    def _slugify(self, value):
        value = (value or "").strip().lower()
        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ñ": "n",
        }
        for old, new in replacements.items():
            value = value.replace(old, new)

        allowed = []
        for char in value:
            if char.isalnum():
                allowed.append(char)
            elif char in [" ", "-", "_", "/"]:
                allowed.append("-")

        slug = "".join(allowed)
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug.strip("-")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("website_slug") and vals.get("name"):
                vals["website_slug"] = self._slugify(vals["name"])
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("name") and not vals.get("website_slug"):
            vals["website_slug"] = self._slugify(vals["name"])
        return super().write(vals)

    @api.constrains("website_slug")
    def _check_website_slug(self):
        for record in self:
            if not record.website_slug:
                raise ValidationError("The website slug is required.")

    def _compute_website_url(self):
        for record in self:
            if record.website_slug:
                record.website_url = f"/shop/marca/{record.website_slug}"
            else:
                record.website_url = ""