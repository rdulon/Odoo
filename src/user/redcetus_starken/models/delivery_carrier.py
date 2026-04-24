from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[("starken", "Starken")],
        ondelete={"starken": "set default"},
    )

    starken_environment = fields.Selection(
        [
            ("qa", "QA"),
            ("prod", "Producción"),
        ],
        default="qa",
        string="Ambiente Starken",
    )

    starken_rut = fields.Char(string="Rut Starken")
    starken_clave = fields.Char(string="Clave Starken")

    starken_origin_commune_id = fields.Many2one(
        "starken.commune",
        string="Comuna origen Starken",
    )

    starken_origin_agency_code = fields.Integer(
        string="Código agencia origen",
        default=0,
    )

    starken_client_rut = fields.Char(
        string="Rut cliente Starken",
        default="1",
    )

    starken_timeout = fields.Integer(
        string="Timeout API",
        default=30,
    )

    starken_debug = fields.Boolean(
        string="Debug Starken",
        default=False,
    )