from odoo import models, fields


class RealEstateUser(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.property",
        "salesperson_id",
        string="Real Estate Properties",
        domain=[("state", "in", ["new", "offer_received"])],
    )
