# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tests import tagged, Form


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_full_confirm(self):
        for rec in self:
            rec.action_confirm()
            picking_ids = self.env['stock.picking'].search([('origin', '=', rec.name)])
            for pick in picking_ids:
                if pick.state == 'assigned':
                    trans = pick.button_validate()
                    Form(self.env['stock.immediate.transfer'].with_context(trans['context'])).save().process()
            rec._create_invoices()
            rec.invoice_ids.action_post()

    def act_stock_invoice_return(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.return.picking",
            "view_mode": 'form',
            "context": {'default_sale_id': self.id, 'default_domain_picking_ids': [(6, 0, self.picking_ids.ids)]},
            "name": "Return Products",
            "target": "new",
        }

    def action_sales_register_payment(self):
        for rec in self:
            payment = rec.invoice_ids.action_register_payment()
            Form(self.env['account.payment.register'].with_context(payment['context'])).save().action_create_payments()


class SaleOrderGlobalReturn(models.TransientModel):
    _inherit = 'stock.return.picking'

    sale_id = fields.Many2one(comodel_name="sale.order")
    domain_picking_ids = fields.Many2many('stock.picking', relation="picking_order_return_rel")

    def create_returns(self):
        if self.sale_id:
            self.env['account.move.reversal'].create({
                'move_ids': [(6, 0, self.sale_id.invoice_ids.ids)],
                'journal_id': self.sale_id.invoice_ids[0].journal_id.id,
                'refund_method': 'refund',
            }).reverse_moves()
            remove_lines = []
            for line in self.sale_id.invoice_ids[-1].invoice_line_ids:
                if line.product_id.id in self.product_return_moves.mapped('product_id').ids:
                    quantity = self.product_return_moves.filtered(lambda p: p.product_id.id == line.product_id.id)[
                        0].quantity
                    self.sale_id.invoice_ids[-1].invoice_line_ids = [(1, line.id, {'quantity': quantity})]
                else:
                    remove_lines.append(line.id)
            for r in remove_lines:
                self.sale_id.invoice_ids[-1].invoice_line_ids = [(3, r)]

        return super(SaleOrderGlobalReturn, self).create_returns()


class ResUsers(models.Model):
    _inherit = 'res.users'
    chatter_position = fields.Selection([('normal', 'Normal'),
                                         ('sided', 'Sided')
                                         ], string="Chatter Position", required=True,
                                        default='normal')
