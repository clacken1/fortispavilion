{
    'name': "Payment Provider: Fygaro",
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'summary': "Fygaro payment provider .",
    'depends': ['payment'],
    'data': [
        'views/payment_fygaro_templates.xml',
        'views/payment_provider_views.xml',        
        'data/payment_provider_data.xml',
    ],
   'application': False,
   'post_init_hook': 'post_init_hook',
   'uninstall_hook': 'uninstall_hook',   
   'external_dependencies': {
        "python": ['jwt'],             
    },
    'installable': True,
    'application': False,    
    'license': 'LGPL-3',
}
