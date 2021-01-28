# -*- coding: utf-8 -*-


{
    'name': 'Cash Flow',
    'version': '0.0.1',
    'summary': 'Cash Flow',
    'author': 'gflores',
    'maintainer': 'gflores',
    'company': 'Grupo Requiez SA de CV',
    'website': 'https://www.gruporequiez.com',
    'depends': ['account'],
    'category': 'Account',
    'demo': [],
    'data': [
        # data
        'data/report_data.xml',
        # views
        'wizard/cash_flow_view.xml',
        'views/account_move_view.xml',
        # automations
        'doc/base_automation.xml',
        # Reports
        'report/report_definition.xml',
        'report/report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
