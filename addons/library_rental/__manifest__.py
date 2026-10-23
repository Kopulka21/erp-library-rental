{
    'name': 'Library Rental',
    'version': '19.0.1.0.0',
    'category': 'Services',
    'summary': 'Модуль управління бібліотекою та прокатом книг',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/library_views.xml',
        'data/library_demo.xml',
    ],
    'installable': True,
    'application': True,
}
