from odoo import api, fields, models
from odoo.exceptions import UserError

from ..services.starken_client import StarkenClient


class StarkenCommune(models.Model):
    _name = "starken.commune"
    _description = "Starken Commune"
    _rec_name = "display_name"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Integer(required=True, index=True)

    region_code = fields.Integer(index=True)
    city_code = fields.Integer(index=True)
    city_name = fields.Char()

    is_destination = fields.Boolean(default=True)
    active = fields.Boolean(default=True)

    state_id = fields.Many2one("res.country.state", string="Región Odoo")

    display_name = fields.Char(compute="_compute_display_name", store=True)

    _sql_constraints = [
        ("starken_commune_code_uniq", "unique(code)", "El código de comuna debe ser único."),
    ]

    @api.depends("name", "city_name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.name} ({rec.city_name})" if rec.city_name else rec.name

    @api.model
    def action_import_destination_communes(self, *args):
        client = StarkenClient(self.env)
        data = client.listar_ciudades_destino()

        if data.get("codigoRespuesta") != 1:
            raise UserError("Starken respondió con error: %s" % data.get("mensajeRespuesta"))

        State = self.env["res.country.state"].sudo()

        region_map = {
            15: "AP",
            1: "TA",
            2: "AN",
            3: "AT",
            4: "CO",
            5: "VS",
            13: "RM",
            6: "LI",
            7: "ML",
            16: "NB",
            8: "BI",
            9: "AR",
            14: "LR",
            10: "LL",
            11: "AI",
            12: "MA",
        }

        created = 0
        updated = 0

        for city in data.get("listaCiudadesDestino", []):
            region_code = city.get("codigoRegion")
            city_code = city.get("codigoCiudad")
            city_name = city.get("nombreCiudad")
            communes = city.get("listaComunas", []) or []

            state = False
            region_short = region_map.get(region_code)
            if region_short:
                state = State.search([
                    ("country_id.code", "=", "CL"),
                    ("code", "=", region_short),
                ], limit=1)

            for commune in communes:
                vals = {
                    "name": commune.get("nombreComuna"),
                    "code": commune.get("codigoComuna"),
                    "region_code": region_code,
                    "city_code": city_code,
                    "city_name": city_name,
                    "is_destination": True,
                    "state_id": state.id if state else False,
                    "active": True,
                }

                existing = self.search([("code", "=", vals["code"])], limit=1)
                if existing:
                    existing.write(vals)
                    updated += 1
                else:
                    self.create(vals)
                    created += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Importación completada",
                "message": f"Comunas creadas: {created}, actualizadas: {updated}",
                "type": "success",
                "sticky": False,
            },
        }