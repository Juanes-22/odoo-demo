from odoo import models, Command


class EstateAccountProperty(models.Model):
    _inherit = "estate.property"

    def sold_property(self):
        # self.env["account.move"].create(
        #     {
        #         "partner_id": self.partner_id, 
        #         "move_type": "Customer Invoice",
        #         "invoice_line_ids": [
        #             Command.create({
        #                 "name": self.name,
        #                 "quantity": 1,
        #                 "price_unit": "dollar"
        #             })
        #         ]
        #     }
        # )

        return super().sold_property()
