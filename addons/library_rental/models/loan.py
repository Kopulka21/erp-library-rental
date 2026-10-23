from odoo import api, fields, models
class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Видача'
    copy_id = fields.Many2one('library.copy', string='Примірник', required=True, ondelete='restrict')
    member_id = fields.Many2one('library.member', string='Читач', required=True, ondelete='restrict')
    loan_date = fields.Date(string='Дата видачі', default=fields.Date.context_today)
    due_date = fields.Date(string='Повернути до')
    return_date = fields.Date(string='Дата повернення')
    state = fields.Selection([('active', 'Активна'), ('returned', 'Повернена')], string='Стан', default='active')
    book_id = fields.Many2one(related='copy_id.book_id', string='Книга', readonly=True)
    book_author = fields.Char(related='copy_id.book_id.author', string='Автор книги', readonly=True)
    member_number = fields.Char(related='member_id.membership_number', string='Номер читацького', readonly=True)
    @api.depends('copy_id.inventory_number', 'member_id.name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = '%s → %s' % (rec.copy_id.inventory_number or '?', rec.member_id.name or '?')
    book_isbn = fields.Char(related='copy_id.book_id.isbn', string='ISBN', readonly=True)
    copy_condition = fields.Selection(related='copy_id.condition', string='Стан примірника', readonly=True)
