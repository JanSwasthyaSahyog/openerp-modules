# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    _columns = {
        'insurance_policy_id': fields.many2one('insurance.schemes', 'Insurance Policy'),
        'is_insurance_journal': fields.boolean('Is Insurance Journal'),
        'dummy_amount': fields.float('Amount')
        }
    
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id,
                                                            date, amount, ttype, company_id, context=context)
        journal_pool = self.pool.get('account.journal')
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            if journal.type == 'insurance':
                res['value'].update({'is_insurance_journal': True})
                if context.get('active_model') == 'account.invoice':
                    if context.get('active_id'):
                        invoice_id = context.get('active_id')
                        invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
                        if amount:
                            if invoice_obj.amount_total != invoice_obj.residual or amount < invoice_obj.amount_total:
                                res['warning'] = {
                                    'title': _('Validation Error!'),
                                    'message' : _('You can not use %s payment method for partial payment.')%(journal.name)
                                }
                        account_id = journal.default_debit_account_id
                        if not account_id:
                            raise osv.except_osv(_('Error!'),
                                    _('There is no debit account defined  for %s.')%(journal.name))
                        res['value'].update({'account_id': account_id.id, 
                                             'amount': amount})
            else:
                res['value'].update({'is_insurance_journal': False})
        return res
    
    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        res = super(account_voucher, self).onchange_amount(cr, uid, ids, amount, rate, partner_id, journal_id,
                                                           currency_id, ttype, date, payment_rate_currency_id, company_id, context)
        if context is not None:
            if context.get('active_id') and context.get('active_model') == 'account.invoice':
                invoice_obj = self.pool.get('account.invoice').browse(cr, uid, context.get('active_id'))
                if invoice_obj:
                    if amount < invoice_obj.amount_total:
                        journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
                        if journal.type == 'insurance':
                            res['warning'] = {
                                        'title': _('Validation Error!'),
                                        'message' : _('You can not use %s payment method for partial payment.')%(journal.name)
                                    }
        return res
    
    def button_proforma_voucher(self, cr, uid, ids, context=None):
        res = super(account_voucher, self).button_proforma_voucher(cr, uid, ids, context=context)
        if ids:
            voucher = self.browse(cr, uid, ids)
            if voucher: voucher = voucher and voucher[0]
            if voucher.journal_id.type == 'insurance':
#            sale_advance_payment_inv_pool = self.pool.get('sale.advance.payment.inv')
#            wizard_vals = {'advance_payment_method': 'all'}
                if context.get('invoice_id'):
                    invoice_obj = self.pool.get('account.invoice').browse(cr, uid, context.get('invoice_id'))
    #                    wizard_vals.update({'amount': invoice_obj.amount_total})
    #                sale_advance_payment_inv_id = sale_advance_payment_inv_pool.create(cr, uid, wizard_vals)
                    cr.execute('select order_id from sale_order_invoice_rel where invoice_id=%d'%(context.get('invoice_id')))
                    result = cr.fetchone()
                    if result:
                        order_id = result and result[0]
                        if invoice_obj:
                            default_vals =  {'partner_id': voucher.insurance_policy_id.partner_id.id,
                                             'journal_id': voucher.journal_id.id,
                                             'date_invoice': voucher.date,
                                             'insurance_invoice': True,
                                             'dummy_journal': voucher.journal_id.id,
                                             'origin': invoice_obj.number,
                                             'origin_name': voucher.partner_id.name + '-' + voucher.partner_id.name}
                            new_invoice = self.pool.get('account.invoice').copy(cr, uid, context.get('invoice_id'), default=default_vals)
                        cr.execute('insert into sale_order_invoice_rel(order_id, invoice_id) values (%d, %d)'%(order_id, new_invoice))
                    else:
                        default_vals =  {'partner_id': voucher.insurance_policy_id.partner_id.id,
                                         'journal_id': voucher.journal_id.id,
                                         'date_invoice': voucher.date,
                                         'insurance_invoice': True,
                                         'dummy_journal': voucher.journal_id.id,
                                         'origin': invoice_obj.number,
                                        'origin_name': voucher.partner_id.name + '-' + voucher.partner_id.name }
                        new_invoice = self.pool.get('account.invoice').copy(cr, uid, context.get('invoice_id'), default=default_vals)
        return res
    
    def proforma_voucher(self, cr, uid, ids, context=None):
        voucher = self.browse(cr, uid, ids)
        if voucher: voucher = voucher and voucher[0]
        if voucher.journal_id.type == 'insurance':
            if voucher.amount < voucher.invoice_id.amount_total:
                raise osv.except_osv(_('Error!'),
                                        _('You can not use %s payment method for partial payment.')%(voucher.journal_id.name))
            else:
                res = super(account_voucher, self).proforma_voucher(cr, uid, ids, context)
       
                if voucher.invoice_id:
    #                sale_advance_payment_inv_id = sale_advance_payment_inv_pool.create(cr, uid, wizard_vals)
                    cr.execute('select order_id from sale_order_invoice_rel where invoice_id=%d'%(voucher.invoice_id.id))
                    result = cr.fetchone()
                    if result:
                        order_id = result and result[0]
                        if voucher.invoice_id:
                            default_vals =  {'partner_id': voucher.insurance_policy_id.partner_id.id,
                                             'journal_id': voucher.journal_id.id,
                                             'date_invoice': voucher.date,
                                             'insurance_invoice': True,
                                             'dummy_journal': voucher.journal_id.id,
                                             'origin': voucher.invoice_id.number,
                                             'origin_name': voucher.partner_id.name + '-' + voucher.partner_id.name}
                            new_invoice = self.pool.get('account.invoice').copy(cr, uid, voucher.invoice_id.id, default=default_vals)
                        cr.execute('insert into sale_order_invoice_rel(order_id, invoice_id) values (%d, %d)'%(order_id, new_invoice))
                    else:
                        default_vals =  {'partner_id': voucher.insurance_policy_id.partner_id.id,
                                         'journal_id': voucher.journal_id.id,
                                         'date_invoice': voucher.date,
                                         'insurance_invoice': True,
                                         'dummy_journal': voucher.journal_id.id,
                                         'origin': voucher.invoice_id.number,
                                         'origin_name': voucher.partner_id.name + '-' + voucher.partner_id.name}
                        new_invoice = self.pool.get('account.invoice').copy(cr, uid, voucher.invoice_id.id, default=default_vals)
                return res
        else:
            return super(account_voucher, self).proforma_voucher(cr, uid, ids, context)
    
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False

        if context is None:
            context = {}
        context_multi_currency = context.copy()
        if date:
            context_multi_currency.update({'date': date})

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_dr_ids': [] ,'line_cr_ids': [] ,'pre_line': False,},
        }

        #drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id
        account_id = False
        if journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
        elif journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

        default['value']['account_id'] = account_id

        if journal.type not in ('cash', 'bank', 'insurance'):
            return default

        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'

        #JSS Change START - if price is negative, add to total debit/credit
        if ttype == 'payment':
            account_type = 'payable'
            total_debit = price if price >=0.0 else 0.0
            total_credit = -price if price <0.0 else 0.0
        else:
            total_debit = -price if price <0.0 else 0.0
            total_credit = price if price >= 0.0 else 0.0
            account_type = 'receivable'
        #JSS Change END - if price is negative, add to total debit/credit

        if not context.get('move_line_ids', False):
            ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_line_found = False

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue
            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_line_found = line.id
                    break
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_line_found = line.id
                    break
                #otherwise we will split the voucher amount on each line (by most old first)

                #JSS Change START (adding residual amount to total_credit/debit)
                total_credit += line.credit and line.amount_residual or 0.0
                total_debit += line.debit and line.amount_residual_currency or 0.0
                #JSS Change END

            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_line_found = line.id
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0
        #voucher line creation
        for line in account_move_lines:

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id==line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual))
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (move_line_found == line.id) and min(abs(price), amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }

            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_line_found:
                if currency_id == line_currency_id:
                    _logger.info("reduce amount")
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)

        #jss add balance amount
        default['value']['balance_amount'] = self._compute_balance_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        
        if(default['value']['balance_amount'] < 0):
            default['warning'] = {
                'title': _('Validation Error!'),
                'message' : "Warning!! Amount Paid is more than the Amount Due. Do you want to continue?"
            }
        return default
    