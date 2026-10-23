from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError
LOAN_PERIOD_DAYS = 14
FINE_PER_DAY = 5.0


class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Видача'
    copy_id = fields.Many2one('library.copy', string='Примірник', required=True, ondelete='restrict')
    member_id = fields.Many2one('library.member', string='Читач', required=True, ondelete='restrict')
    loan_date = fields.Date(string='Дата видачі', default=fields.Date.context_today)
    due_date = fields.Date(string='Повернути до', compute='_compute_due_date', store=True)
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
    fine_amount = fields.Float(string='Штраф, грн', compute='_compute_fine_amount', store=True)
    is_overdue = fields.Boolean(string='Прострочена', compute='_compute_is_overdue')

    @api.depends('loan_date')
    def _compute_due_date(self):
        for rec in self:
            rec.due_date = rec.loan_date + timedelta(days=LOAN_PERIOD_DAYS) if rec.loan_date else False

    @api.depends('return_date', 'due_date')
    def _compute_fine_amount(self):
        for rec in self:
            if rec.return_date and rec.due_date and rec.return_date > rec.due_date:
                rec.fine_amount = (rec.return_date - rec.due_date).days * FINE_PER_DAY
            else:
                rec.fine_amount = 0.0

    @api.depends('state', 'due_date')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_overdue = bool(rec.state == 'active' and rec.due_date and rec.due_date < today)

    @api.onchange('copy_id')
    def _onchange_copy_id(self):
        if self.copy_id:
            domain = [('copy_id', '=', self.copy_id.id), ('state', '=', 'active')]
            if self._origin.id:
                domain.append(('id', '!=', self._origin.id))
            if self.env['library.loan'].search_count(domain):
                return {'warning': {'title': 'Увага', 'message': 'Цей примірник уже має активну видачу.'}}

    @api.constrains('copy_id', 'state')
    def _check_single_active_loan(self):
        for rec in self:
            if rec.state == 'active':
                other = self.search([('copy_id', '=', rec.copy_id.id), ('state', '=', 'active'), ('id', '!=', rec.id)], limit=1)
                if other:
                    raise ValidationError('Цей примірник уже виданий: у нього є інша активна видача.')

    @api.constrains('loan_date', 'due_date')
    def _check_due_after_loan(self):
        for rec in self:
            if rec.loan_date and rec.due_date and rec.due_date <= rec.loan_date:
                raise ValidationError('Дата повернення має бути пізніше дати видачі.')

    @api.constrains('loan_date', 'return_date')
    def _check_return_after_loan(self):
        for rec in self:
            if rec.return_date and rec.loan_date and rec.return_date < rec.loan_date:
                raise ValidationError('Фактична дата повернення не може бути раніше дати видачі.')

    def action_return(self):
        for rec in self:
            rec.state = 'returned'
            if not rec.return_date:
                rec.return_date = fields.Date.context_today(rec)
