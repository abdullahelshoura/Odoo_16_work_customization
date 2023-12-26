# -*- coding: utf-8 -*-
{
    'name': "add_description",

    'summary': """ """,

    'description': """
        
    """,

    'author': "IBS - khaled habib",
    'website': "http://www.ibs-odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','nardi_customization','sale'],

    # always loaded
    'data': [
        'views/edit_report.xml',



    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}