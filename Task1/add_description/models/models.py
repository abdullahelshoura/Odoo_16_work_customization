from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id, index=1)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id, required=True)
    boolham=fields.Boolean()

    # tax_totalss=fields.Binary(
    #     string="Invoice Totals",
    #     compute='_compute_tax_totalss',
    #     help='Edit Tax amounts if you encounter rounding issues.'
    # )

    def amount_salee(self):
        print(self.tax_totals)
        return self.amount_untaxed * 0.99

    def total_salee(self):
        return (self.amount_untaxed * 0.99) + self.amount_tax
    
    
    




    # def _compute_tax_totalss(self):
    #
    #
    #     for movee in self:
    #         s= movee.tax_totals
    #         if s['subtotals']:
    #             if len(s['subtotals']) != 0:
    #                 for line in s['subtotals']:
    #                     if line['name'] != '':
    #                         line.update({'name': 'Net.Sale'})
    #                         # print(s)
    #         movee.tax_totalss = s
    #         # print(movee.tax_totalss)



















