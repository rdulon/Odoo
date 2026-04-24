import logging

from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteSaleStarken(WebsiteSale):

    def _prepare_address_values(self, order_sudo, **post):
        values = super()._prepare_address_values(order_sudo, **post)

        commune_id = post.get("starken_commune_id")

        if commune_id:
            try:
                values["starken_commune_id"] = int(commune_id)
                _logger.warning("STARKEN VALUE INJECTED: %s", values["starken_commune_id"])
            except (TypeError, ValueError):
                pass

        return values