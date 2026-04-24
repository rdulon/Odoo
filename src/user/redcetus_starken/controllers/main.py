import logging

from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteSaleStarken(WebsiteSale):

    def _complete_address_values(
        self, address_values, *args, order_sudo=False, **kwargs
    ):
        super()._complete_address_values(
            address_values, *args, order_sudo=order_sudo, **kwargs
        )

        commune_id = kwargs.get("starken_commune_id")

        if commune_id:
            try:
                address_values["starken_commune_id"] = int(commune_id)
                _logger.warning("STARKEN INJECTED IN ADDRESS VALUES: %s", commune_id)
            except (TypeError, ValueError):
                pass