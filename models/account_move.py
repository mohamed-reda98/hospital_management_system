from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    medical_bill_id = fields.Many2one('medical.bill', string='Medical Bill', copy=False)
