{
    "name": "RedCetus Brand",
    "version": "19.0.1.0.0",
    "summary": "Brands for products",
    "category": "Product",
    "author": "RedCetus",
    "license": "LGPL-3",
    "depends": ["product", "website_sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_brand_views.xml",
        "views/product_template_views.xml",
        "views/website_brand_views.xml",
        "views/website_product_brand_views.xml",
    ],
    "installable": True,
    "application": False,
}