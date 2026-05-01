from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    starken_commune_id = fields.Many2one(
        "starken.commune",
        string="Comuna",
    )