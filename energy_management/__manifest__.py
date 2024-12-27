{
    'name': 'Energy Management',
    'version': '1.0',
    'summary': 'Gestione del consumo energetico e suggerimenti per ottimizzazione',
    'category': 'Management',
    'author': 'Fabrizio',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/energy_management_views.xml',
        'data/energy_data.xml',
        'data/module_category_data.xml',
        'report/energy_report.xml',
        'data/model_reference_data.xml',  # File con i riferimenti ai modelli
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}