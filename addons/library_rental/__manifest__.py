{
    'name': 'Library Rental',
    'version': '19.0.1.0.0',
    'category': 'Services',
    'summary': 'Модуль управління бібліотекою та прокатом книг',
    'depends': ['base'],
    'data': [
        'security/library_security.xml', 'security/ir.model.access.csv',
        'views/library_views.xml',
        'views/book_views.xml',
        'views/member_views.xml',
        'views/copy_views.xml',
        'views/loan_views.xml',  
        'views/menu.xml',
        'data/library_demo.xml',
    ],
    'installable': True,
    'application': True,
}
