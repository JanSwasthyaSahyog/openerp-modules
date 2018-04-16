# -*- coding: utf-8 -*-
{
    'name': 'Pay with Insurance',
    'category': 'Accounting',
    'description': """
In Account Invoice provide user to select insurance for payment
===============================================================
        """,
    'version': '1.0',
    'depends':['web_m2x_options','bahmni_customer_payment'],
    'data': ['insurance_schemes_view.xml',
             'account_journal_view.xml',
             'account_voucher_view.xml',
             'account_invoice_view.xml'],
    'installable': True,
    'application': True,
}