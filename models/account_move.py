# Copyright 2017 Humanytek.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models, fields
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    _name = 'account.move'
    _description = 'Account Move'

    move_type = fields.Selection([
        ('out_invoice', 'Customer invoice'),
        ('in_invoice', 'Supplier invoice'),
        ('out_refund', 'Customer CN'),
        ('in_refund', 'Supplier CN'),
        ('inbound', 'Customer payment'),
        ('outbound', 'Supplier payment'),
        ('transfer', 'Transfer'),
        ('yields', 'Yields'),
        ('commissions', 'Commissions'),
        ('withholdings', 'Withholdings')],
        string="Move type", store=True)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _name = 'account.invoice'
    _description = 'Account invoice'


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _name = 'account.payment'
    _description = 'Account payment'


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'
    _name = 'account.bank.statement'
    _description = 'account.bank.statement'

    # @api.multi
    # @api.onchange('line_ids')
    # def onchange_is_tranfer(self):
