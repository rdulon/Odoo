from odoo import fields, models


class StarkenCommune(models.Model):
    _name = "starken.commune"
    _description = "Starken Commune"
    _rec_name = "name"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Integer()