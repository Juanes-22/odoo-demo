# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "A Estate Property"

    id = fields.Integer()
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=lambda self: (datetime.today() + timedelta(days=90)).date()
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        default="new",
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user
    )
    property_tag_ids = fields.Many2many("estate.property.tag", string="Property Tag")
    property_offer_ids = fields.One2many(
        "estate.property.offer", "property_id", string="Offers"
    )

    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("property_offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            offers = record.property_offer_ids.mapped("price")
            record.best_price = max(offers) if offers else 0


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "A Estate Property Type"

    id = fields.Integer()
    name = fields.Char(required=True)


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "A Estate Property Tag"

    id = fields.Integer()
    name = fields.Char(required=True)


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "A Estate Property Offer"

    id = fields.Integer()
    price = fields.Float(required=True)
    status = fields.Selection(
        [("refused", "Refused"), ("accepted", "Accepted")], copy=False
    )

    partner_id = fields.Many2one(
        "res.partner", string="Partner", copy=False, required=True
    )
    property_id = fields.Many2one("estate.property", required=True)
