from odoo import models, fields, api

class MedicalBillLine(models.Model):
    _name = 'medical.bill.line'
    _description = 'Medical Bill Line'

    bill_id = fields.Many2one('medical.bill', string='Bill')

    product_id = fields.Many2one(
        'product.template',
        string='Item',
        required=True,
        ondelete='restrict',
        help='Select an item'
    )

    cost = fields.Float(string='Cost')
    quantity = fields.Integer(string='Quantity', default=1)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('cost', 'quantity')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.cost * line.quantity

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.cost = self.product_id.list_price  # Auto-fill cost from product
