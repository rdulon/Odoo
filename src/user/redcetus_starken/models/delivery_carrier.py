import requests

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

    starken_delivery_type_code = fields.Selection(
        [
            ("2", "Domicilio"),
            ("1", "Agencia"),
        ],
        string="Tipo de entrega Starken",
        default="2",
    )

    starken_default_height = fields.Float(
        string="Alto por defecto (cm)",
        default=10.0,
    )

    starken_default_width = fields.Float(
        string="Ancho por defecto (cm)",
        default=10.0,
    )

    starken_default_length = fields.Float(
        string="Largo por defecto (cm)",
        default=10.0,
    )

    starken_min_weight = fields.Float(
        string="Peso mínimo (kg)",
        default=1.0,
    )

    starken_timeout = fields.Integer(
        string="Timeout API",
        default=30,
    )

    starken_debug = fields.Boolean(
        string="Debug Starken",
        default=False,
    )

    def starken_rate_shipment(self, order):
        self.ensure_one()

        partner = order.partner_shipping_id
        commune = partner.starken_commune_id

        if not commune:
            return {
                "success": False,
                "price": 0.0,
                "error_message": "Debe seleccionar una comuna Starken en la dirección de despacho.",
                "warning_message": False,
            }

        if not self.starken_origin_commune_id:
            return {
                "success": False,
                "price": 0.0,
                "error_message": "Debe configurar la comuna origen Starken en el método de envío.",
                "warning_message": False,
            }

        weight = sum(
            line.product_id.weight * line.product_uom_qty
            for line in order.order_line
            if not line.is_delivery and line.product_id
        )

        weight = max(weight, self.starken_min_weight or 1.0)

        payload = {
            "codigoCiudadOrigen": self.starken_origin_commune_id.city_code,
            "codigoCiudadDestino": commune.city_code,
            "codigoAgenciaDestino": 0,
            "codigoAgenciaOrigen": self.starken_origin_agency_code or 0,
            "alto": self.starken_default_height or 10.0,
            "ancho": self.starken_default_width or 10.0,
            "largo": self.starken_default_length or 10.0,
            "kilos": weight,
            "cuentaCorriente": "",
            "cuentaCorrienteDV": "",
            "rutCliente": self.starken_client_rut or "1",
        }

        base_url = (
            "https://restservices.starken.cl/starkenservices/rest"
            if self.starken_environment == "prod"
            else "https://restservices-qa.starken.cl/apiqa/starkenservices/rest"
        )

        try:
            response = requests.post(
                f"{base_url}/consultarTarifas",
                json=payload,
                headers={
                    "Rut": self.starken_rut,
                    "Clave": self.starken_clave,
                },
                timeout=self.starken_timeout or 30,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as error:
            return {
                "success": False,
                "price": 0.0,
                "error_message": f"Error consultando tarifa Starken: {error}",
                "warning_message": False,
            }

        if data.get("codigoRespuesta") != 1:
            return {
                "success": False,
                "price": 0.0,
                "error_message": data.get("mensajeRespuesta") or "Starken no entregó tarifa.",
                "warning_message": False,
            }

        tarifas = data.get("listaTarifas", [])
        selected = False

        for tarifa in tarifas:
            tipo_entrega = tarifa.get("tipoEntrega", {})
            if str(tipo_entrega.get("codigoTipoEntrega")) == str(self.starken_delivery_type_code or "2"):
                selected = tarifa
                break

        if not selected and tarifas:
            selected = min(tarifas, key=lambda t: t.get("costoTotal", 0))

        if not selected:
            return {
                "success": False,
                "price": 0.0,
                "error_message": "Starken no devolvió tarifas disponibles.",
                "warning_message": False,
            }

        return {
            "success": True,
            "price": float(selected.get("costoTotal", 0)),
            "error_message": False,
            "warning_message": False,
        }