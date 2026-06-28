from odoo import models, fields, api
from odoo.exceptions import UserError


class MedicalBill(models.Model):
    _name = 'medical.bill'
    _description = 'Medical Bill'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    patient_name = fields.Char(related='patient_id.name', string='Patient Name', readonly=True)
    patient_age = fields.Char(related='patient_id.age', string='Patient Age', readonly=True)
    patient_gender = fields.Selection(related='patient_id.gender', string='Gender', readonly=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)

    line_ids = fields.One2many('medical.bill.line', 'bill_id', string='Items')
    total_amount = fields.Float(string='Total', compute='_compute_total', store=True)

    invoice_ids = fields.One2many('account.move', 'medical_bill_id', string='Invoices')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(line.subtotal for line in rec.line_ids)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)

    def _get_invoice_partner(self):
        self.ensure_one()
        partner = self.env['res.partner'].search([('name', '=', self.patient_id.name)], limit=1)
        if not partner:
            partner = self.env['res.partner'].create({'name': self.patient_id.name})
        return partner

    def action_create_invoice(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError("Add at least one item before creating an invoice.")
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self._get_invoice_partner().id,
            'invoice_date': self.date or fields.Date.context_today(self),
            'medical_bill_id': self.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': line.product_id.name,
                    'product_id': line.product_id.product_variant_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.cost,
                }) for line in self.line_ids
            ],
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_invoices(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'domain': [('medical_bill_id', '=', self.id)],
            'context': {'create': False, 'default_move_type': 'out_invoice'},
        }
        if len(self.invoice_ids) == 1:
            action.update({'view_mode': 'form', 'res_id': self.invoice_ids.id})
        else:
            action['view_mode'] = 'list,form'
        return action

    def print_medical_bill_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/medical/receipt/{self.id}',
            'target': 'new',  # opens the receipt in a new tab
        }

    def action_save_bill_save(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medical Bills',
            'res_model': 'medical.bill',
            'view_mode': 'list,form',
            'target': 'current',
        }









