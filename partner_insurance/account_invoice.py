# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    _columns = {
        'insurance_invoice': fields.boolean('Is Insurance Invoice?') ,
        'dummy_journal': fields.many2one('account.journal', 'Journal'),
        'origin_name': fields.char('Source Name', size=64),
        }
