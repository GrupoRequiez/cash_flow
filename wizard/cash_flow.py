# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from io import StringIO, BytesIO
import base64
import csv
from datetime import date, datetime, timedelta
import logging
from odoo import api, fields, models, exceptions, _
import collections


_logger = logging.getLogger(__name__)


def keep_wizard_open(f):
    def wrapper(*args, **kwargs):
        f(*args, *kwargs)
        self = args[0]
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
    return wrapper


def data_to_bytes(fieldnames, data):
    writer_file = StringIO()
    writer = csv.DictWriter(writer_file, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    writer.writerows(data)
    return writer_file.getvalue().encode('utf-8')


class CashFlow(models.TransientModel):
    _name = 'cash.flow'
    _description = 'Cash flow'

    date_start = fields.Date('Start Date', required=True, default='2021-01-01')
    date_end = fields.Date('End Date',  required=True, default='2021-01-31')
    data_file = fields.Binary(readonly=True)
    data_file_fname = fields.Char()
    getted = fields.Boolean('Getted', default=False)
    report_format = fields.Selection([
        ('csv', 'CSV'),
        ('pdf', 'PDF')],
        string="Report", default="csv")
    cash_flow_detail_ids = fields.One2many(
        'cash.flow.detail', 'cashflow_id', 'Deatils')

    # @keep_wizard_open
    @api.multi
    def calculate(self):
        detail = self.env['cash.flow.detail'].search([]).unlink()
        account_ids = (6808, 6809, 6810, 6811, 6812, 6813, 6814, 6815, 6816, 6817, 6818,
                       6819, 6820, 7192, 6821, 6822, 6823, 6824, 6825, 7194, 6826, 6827, 7177, 7288)
        AccountMoveLine_Obj = self.env['account.move.line']
        dict_list = []
        data = []
        fieldnames = ['CUENTAS', 'INICIAL', 'TRASPASOS', 'INGRESOS', 'RENDIMIENTOS',
                      'ENTRADAS', 'PAGOS', 'COMIS', 'RET', 'SALIDAS', 'SALDO']
        account_name = ""

        for account in account_ids:
            account_name = self.env['account.account'].search([('id', '=', account)]).name
            statement_id = self.env['account.bank.statement'].search([
                ('date', '<=', self.date_start),
                ('state', '=', 'confirm'),
                '&',
                ('journal_id.default_credit_account_id', '=', account),
                ('journal_id.default_debit_account_id', '=', account)],
                order="date desc",
                limit=1)
            balance = statement_id.balance_end

            move_line_transfer_ids = AccountMoveLine_Obj.search([
                ('date', '>', self.date_start),
                ('date', '<=', self.date_end),
                ('move_id.move_type', '=', 'transfer'),
                ('move_id.state', '=', 'posted'),
                ('credit', '>', 0.00),
                ('account_id', '=', account)],
                order="date")
            credit = sum([line.credit for line in move_line_transfer_ids])

            move_line_transfer_ids = AccountMoveLine_Obj.search([
                ('date', '>', self.date_start),
                ('date', '<=', self.date_end),
                ('move_id.move_type', '=', 'transfer'),
                ('move_id.state', '=', 'posted'),
                ('debit', '>', 0.00),
                ('account_id', '=', account)],
                order="date")
            debit = sum([line.debit for line in move_line_transfer_ids])

            move_line_yield_ids = AccountMoveLine_Obj.search([
                ('date', '>', self.date_start),
                ('date', '<=', self.date_end),
                ('move_id.move_type', '=', 'yield'),
                ('move_id.state', '=', 'posted'),
                ('debit', '>', 0.00),
                ('account_id.id', '=', account)],
                order="date")
            yield_ = sum([line.debit for line in move_line_yield_ids])

            move_line_income_ids = AccountMoveLine_Obj.search([
                ('date', '>', self.date_start),
                ('date', '<=', self.date_end),
                ('move_id.move_type', '=', 'inbound'),
                ('move_id.state', '=', 'posted'),
                ('debit', '>', 0.00),
                ('account_id.id', '=', account)],
                order="date")
            income = sum([line.debit for line in move_line_income_ids])

            move_line_expense_ids = AccountMoveLine_Obj.search([
                ('create_date', '>', self.date_start),
                ('create_date', '<=', self.date_end),
                ('move_id.move_type', '=', 'outbound'),
                ('move_id.state', '=', 'posted'),
                ('credit', '>', 0.00),
                ('account_id.id', '=', account)],
                order="date")
            exprenses = sum([line.credit for line in move_line_expense_ids])

            move_line_commission_ids = AccountMoveLine_Obj.search([
                ('create_date', '>', self.date_start),
                ('create_date', '<=', self.date_end),
                ('move_id.move_type', '=', 'commissions'),
                ('move_id.state', '=', 'posted'),
                ('credit', '>', 0.00),
                ('account_id.id', '=', account)],
                order="date")
            commissions = sum([line.credit for line in move_line_commission_ids])

            move_line_withholdings_ids = AccountMoveLine_Obj.search([
                ('create_date', '>', self.date_start),
                ('create_date', '<=', self.date_end),
                ('move_id.move_type', '=', 'withholdings'),
                ('move_id.state', '=', 'posted'),
                ('credit', '>', 0.00),
                ('account_id.id', '=', account)],
                order="date")
            withholdings = sum([line.credit for line in move_line_withholdings_ids])

            if balance+(credit-debit)+(income+yield_)-(exprenses+commissions+withholdings) != 0:
                data_data = {
                    'CUENTAS': account_name,
                    'INICIAL': balance,
                    'TRASPASOS': credit-debit,
                    'INGRESOS': income,
                    'RENDIMIENTOS': yield_,
                    'ENTRADAS': income+yield_,
                    'PAGOS': exprenses,
                    'COMIS': commissions,
                    'RET': withholdings,
                    'SALIDAS': exprenses+commissions+withholdings,
                    'SALDO': balance+(credit-debit)+(income+yield_)-(exprenses+commissions+withholdings)
                }
                data.append(data_data)

        self.getted = True
        if self.report_format == 'csv':
            fname = "cash_flow_%s.csv" % self.date_end.strftime("%d-%m-%y")
            self.data_file_fname = fname
            self.data_file = base64.b64encode(data_to_bytes(fieldnames, data))
        else:
            detail = self.env['cash.flow.detail']
            for d in data:
                detail.create({
                    'cashflow_id': self.id,
                    'account_name': d['CUENTAS'],
                    'initial_balance': d['INICIAL'],
                    'transfer_amount': d['TRASPASOS'],
                    'income_ammount': d['INGRESOS'],
                    'yield_amount': d['RENDIMIENTOS'],
                    'expense_amount': d['PAGOS'],
                    'commissions_amount': d['COMIS'],
                    'withholdings_amount': d['RET']
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cash.flow',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def print_report(self):  # , docids, data=None
        if self.getted:
            report = self.env['ir.actions.report']._get_report_from_name(
                'cash_flow.cash_flow_report_template')
            return report.report_action(self)
        else:
            raise exceptions.Warning('No se han generado el reporte')


class CashFlowDetails(models.TransientModel):
    _name = 'cash.flow.detail'
    _description = 'Cash flow details'

    cashflow_id = fields.Many2one('cash.flow', 'CashFlow', readonly=True)
    account_name = fields.Char('Account')
    initial_balance = fields.Float('Initial balance', digits=(15, 2))
    transfer_amount = fields.Float('Transfer', digits=(15, 2))
    income_ammount = fields.Float('Income', digits=(15, 2))
    yield_amount = fields.Float('Yield', digits=(15, 2))
    expense_amount = fields.Float('Expense', digits=(15, 2))
    commissions_amount = fields.Float('commission', digits=(15, 2))
    withholdings_amount = fields.Float('withholding', digits=(15, 2))
