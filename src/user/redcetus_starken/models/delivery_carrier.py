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

    starken_rounding = fields.Float(
        string="Redondeo despacho",
        default=0.0,
    )

    starken_fallback_price = fields.Float(
        string="Precio fallback Starken",
        default=0.0,
    )

    starken_free_shipping_state_ids = fields.Many2many(
        "res.country.state",
        string="Regiones con despacho gratis",
        help="Si se configura, el despacho gratis solo aplica para estas regiones.",
    )

    def starken_rate_shipment(self, order):
        self.ensure_one()

        partner = order.partner_shipping_id
        commune = partner.starken_commune_id

        if not commune:
            return {
                "success": False,
                "price": 0.0,
                "error_message": "Debe seleccionar una comuna en la dirección de despacho.",
                "warning_message": False,
            }

        if not self.starken_origin_commune_id:
            return {
                "success": False,
                "price": 0.0,
                "error_message": "Debe configurar la comuna origen Starken.",
                "warning_message": False,
            }

        # =========================
        # PESO Y VOLUMEN
        # =========================
        total_weight = 0.0
        total_volume = 0.0

        for line in order.order_line:
            if line.is_delivery or not line.product_id:
                continue

            qty = line.product_uom_qty
            product = line.product_id

            total_weight += (product.weight or 0.0) * qty
            total_volume += (product.volume or 0.0) * qty

        volumetric_weight = total_volume * 250
        weight = max(total_weight, volumetric_weight, self.starken_min_weight or 1.0)

        # =========================
        # REQUEST API
        # =========================
        payload = {
            "codigoCiudadOrigen": self.starken_origin_commune_id.city_code,
            "codigoCiudadDestino": commune.city_code,
            "codigoAgenciaDestino": 0,
            "codigoAgenciaOrigen": self.starken_origin_agency_code or 0,
            "alto": self.starken_default_height,
            "ancho": self.starken_default_width,
            "largo": self.starken_default_length,
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

        except Exception:
            if self.starken_fallback_price:
                return {
                    "success": True,
                    "price": self._starken_apply_rounding(self.starken_fallback_price),
                    "error_message": False,
                    "warning_message": "Tarifa estimada aplicada.",
                }

            return {
                "success": False,
                "price": 0.0,
                "error_message": "No fue posible calcular el despacho.",
                "warning_message": False,
            }

        # =========================
        # RESPUESTA API
        # =========================
        if data.get("codigoRespuesta") != 1:
            if self.starken_fallback_price:
                return {
                    "success": True,
                    "price": self._starken_apply_rounding(self.starken_fallback_price),
                    "error_message": False,
                    "warning_message": "Tarifa estimada aplicada.",
                }

            return {
                "success": False,
                "price": 0.0,
                "error_message": data.get("mensajeRespuesta"),
                "warning_message": False,
            }

        tarifas = data.get("listaTarifas", [])
        selected = False

        for tarifa in tarifas:
            tipo = tarifa.get("tipoEntrega", {})
            if str(tipo.get("codigoTipoEntrega")) == str(self.starken_delivery_type_code):
                selected = tarifa
                break

        if not selected and tarifas:
            selected = min(tarifas, key=lambda t: t.get("costoTotal", 0))

        if not selected:
            if self.starken_fallback_price:
                return {
                    "success": True,
                    "price": self._starken_apply_rounding(self.starken_fallback_price),
                    "error_message": False,
                    "warning_message": "Tarifa estimada aplicada.",
                }

            return {
                "success": False,
                "price": 0.0,
                "error_message": "Sin tarifas disponibles.",
                "warning_message": False,
            }

        # =========================
        # PRECIO FINAL
        # =========================
        base_price = float(selected.get("costoTotal", 0))
        price = self._starken_apply_rounding(base_price)

        # subtotal SOLO productos
        products_subtotal = sum(
            line.price_subtotal
            for line in order.order_line
            if not line.is_delivery
        )

        # FREE SHIPPING CORRECTO
        free_shipping_allowed = True

        if self.starken_free_shipping_state_ids:
            free_shipping_allowed = commune.state_id in self.starken_free_shipping_state_ids

        if (
            self.free_over
            and self.amount > 0
            and products_subtotal >= self.amount
            and free_shipping_allowed
        ):
            price = 0.0
            
        return {
            "success": True,
            "price": price,
            "error_message": False,
            "warning_message": False,
        }

    def _starken_apply_rounding(self, price):
        self.ensure_one()

        if not self.starken_rounding or self.starken_rounding <= 0:
            return price

        rounding = self.starken_rounding
        return ((price + rounding - 1) // rounding) * rounding