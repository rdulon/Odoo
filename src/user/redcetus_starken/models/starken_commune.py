from odoo import api, fields, models
from odoo.exceptions import UserError

from ..services.starken_client import StarkenClient


class StarkenCommune(models.Model):
    _name = "starken.commune"
    _description = "Starken Commune"
    _rec_name = "display_name"
    _order = "state_id, city_name, name"

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
        Commune = self.env["starken.commune"].sudo()

        region_map = {
            1: "CL-TA",
            2: "CL-AN",
            3: "CL-AT",
            4: "CL-CO",
            5: "CL-VS",
            6: "CL-LI",
            7: "CL-ML",
            8: "CL-BI",
            9: "CL-AR",
            10: "CL-LR",
            11: "CL-AI",
            12: "CL-MA",
            13: "CL-RM",
            14: "CL-LL",
            15: "CL-AP",
            16: "CL-NB",
        }

        created = 0
        updated = 0
        without_state = 0

        for city in data.get("listaCiudadesDestino", []):
            try:
                region_code = int(city.get("codigoRegion") or 0)
            except (TypeError, ValueError):
                region_code = 0

            city_code = city.get("codigoCiudad")
            city_name = city.get("nombreCiudad")
            communes = city.get("listaComunas", []) or []

            state = False
            state_code = region_map.get(region_code)
            if state_code:
                state = State.search([
                    ("country_id.code", "=", "CL"),
                    ("code", "=", state_code),
                ], limit=1)

            if not state:
                without_state += len(communes)

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

                existing = Commune.search([("code", "=", vals["code"])], limit=1)
                if existing:
                    existing.write(vals)
                    updated += 1
                else:
                    Commune.create(vals)
                    created += 1

        message = f"Comunas creadas: {created}, actualizadas: {updated}"
        if without_state:
            message += f". Sin región Odoo: {without_state}"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Importación completada",
                "message": message,
                "type": "success" if not without_state else "warning",
                "sticky": False,
            },
        }