# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "A Estate Property"
    _order = "id desc"

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

    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price >= 0)",
            "Property expected price must be strictly positive",
        ),
        (
            "check_selling_price",
            "CHECK(selling_price >= 0)",
            "Property selling price must be strictly positive",
        ),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("property_offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            offers = record.property_offer_ids.mapped("price")
            record.best_price = max(offers) if offers else 0

    @api.onchange("garden")
    def _onchange_garden(self):
        self.garden_area = 10 if self.garden else 0
        self.garden_orientation = "north" if self.garden else ""

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            selling_price_lower_than_expected_price = (
                float_compare(record.selling_price, record.expected_price * 0.9, 2)
                == -1
            )
            if (
                not float_is_zero(record.selling_price, 2)
                and selling_price_lower_than_expected_price
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    "You must reduce the expected price if you want to accept this offer."
                )

    def sold_property(self):
        if self.state == "cancelled":
            raise UserError("Cancelled properties cannot be sold")

        for record in self:
            record.state = "sold"
        return True

    def cancel_property(self):
        if self.state == "sold":
            raise UserError("Sold properties cannot be cancelled")

        for record in self:
            record.state = "cancelled"
        return True


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "A Estate Property Type"
    _order = "sequence, name"

    id = fields.Integer()
    name = fields.Char(required=True)
    property_ids = fields.One2many(
        "estate.property", "property_type_id", "Estate Properties"
    )
    sequence = fields.Integer("Sequence", default=1)
    offer_ids = fields.One2many(
        "estate.property.offer", "property_type_id", "Property type offers"
    )
    offer_count = fields.Integer(compute="_compute_offer_count")

    _sql_constraints = [
        (
            "type_name_unique",
            "unique(name)",
            "Estate property type name must be unique",
        ),
    ]

    def _compute_offer_count(self):
        for record in self:
            offers = record.offer_ids
            record.offer_count = len(offers)


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "A Estate Property Tag"
    _order = "name"

    id = fields.Integer()
    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ("tag_name_unique", "unique(name)", "Estate property tag name must be unique"),
    ]


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "A Estate Property Offer"
    _order = "price desc"

    id = fields.Integer()
    price = fields.Float(required=True)
    status = fields.Selection(
        [("refused", "Refused"), ("accepted", "Accepted")], copy=False
    )

    partner_id = fields.Many2one(
        "res.partner", string="Partner", copy=False, required=True
    )
    property_id = fields.Many2one("estate.property", required=True)
    property_type_id = fields.Many2one(
        related="property_id.property_type_id", store=True
    )

    _sql_constraints = [
        (
            "check_offer_price",
            "CHECK(offer_price >= 0)",
            "Offer price must be strictly positive",
        ),
    ]

    def accept_offer(self):
        for record in self:
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id.id
            record.property_id.selling_price = record.price

        return True

    def refuse_offer(self):
        for record in self:
            record.status = "refused"
        return True
