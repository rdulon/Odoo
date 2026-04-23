import requests

from odoo.exceptions import UserError


class StarkenClient:
    QA_BASE_URL = "https://restservices-qa.starken.cl/apiqa/starkenservices/rest"
    PROD_BASE_URL = "https://restservices.starken.cl/starkenservices/rest"

    def __init__(self, env):
        self.env = env
        self.config = env["ir.config_parameter"].sudo()

    def _get_base_url(self):
        environment = self.config.get_param("redcetus_delivery_starken.environment", default="qa")
        return self.PROD_BASE_URL if environment == "prod" else self.QA_BASE_URL

    def _get_headers(self):
        rut = self.config.get_param("redcetus_delivery_starken.rut")
        clave = self.config.get_param("redcetus_delivery_starken.clave")

        if not rut or not clave:
            raise UserError("Faltan credenciales Starken. Configure redcetus_delivery_starken.rut y redcetus_delivery_starken.clave en Parámetros del sistema.")

        return {
            "Rut": rut,
            "Clave": clave,
        }

    def listar_ciudades_destino(self):
        url = f"{self._get_base_url()}/listarCiudadesDestino"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json()