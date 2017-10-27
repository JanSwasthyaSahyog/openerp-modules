# -*- coding: utf-8 -*-
from openerp.osv import fields, osv


class insurance_schemes(osv.osv):
    _name = 'insurance.schemes'
    _description = 'Insurance Master'
    
    _columns = {
        'name': fields.char('Name', size=64, required=True, help="Incoterms are series of sales terms.They are used to divide transaction costs and responsibilities between buyer and seller and reflect state-of-the-art transportation practices."),
        'partner_id': fields.many2one('res.partner', 'Insurance Provider'),
        'description': fields.text('Description'),
        'type': fields.selection([('life_cover', 'Life Cover'),
                                  ('medi_claim', 'Medi-Claim'),
                                  ('accidental', 'Accidental')], string='Type Of Insurance'),
        'active': fields.boolean('Active', help="By unchecking the active field, you may hide an INCOTERM without deleting it."),
    }
    
    _defaults = {'active': True}