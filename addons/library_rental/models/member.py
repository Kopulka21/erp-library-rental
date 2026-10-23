from odoo import models, fields


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Читач бібліотеки'

    name = fields.Char(string="Ім’я читача", required=True)
    membership_number = fields.Char(string='Номер читацького', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Телефон')
    loan_ids = fields.One2many('library.loan', 'member_id', string='Видачі')

    _membership_number_unique = models.Constraint(
        'UNIQUE(membership_number)',
        'Номер читацького має бути унікальним.',
    )
