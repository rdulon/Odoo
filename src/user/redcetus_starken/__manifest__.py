{
    "name": "RedCetus Delivery Starken",
    "version": "19.0.1.0.0",
    "depends": ["base", "contacts", "website_sale", "delivery"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/website_sale_templates.xml",
        "views/starken_commune_views.xml",
        "views/delivery_carrier_views.xml",
    ],
    "installable": True,
    "application": False,
    "assets": {
        "web.assets_frontend": [
            "redcetus_starken/static/src/js/starken_commune_filter.js",
        ],
    },    
}