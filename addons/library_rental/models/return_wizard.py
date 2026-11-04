from odoo import api, fields, models
from odoo.exceptions import UserError


class LibraryReturnWizard(models.TransientModel):
    _name = 'library.return.wizard'
    _description = 'Оформлення повернення книги'

    loan_id = fields.Many2one('library.loan', string='Видача', required=True)
    condition_on_return = fields.Selection(
        [('new', 'Новий'), ('good', 'Добрий'), ('damaged', 'Пошкоджений')],
        string='Стан при поверненні',
        required=True,
    )
    notes = fields.Text(string='Коментар бібліотекаря')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ctx = self.env.context
        if ctx.get('active_model') == 'library.loan' and ctx.get('active_id'):
            res['loan_id'] = ctx['active_id']
        return res

    def action_confirm(self):
        self.ensure_one()
        if self.loan_id.state != 'active':
            raise UserError('Ця видача вже закрита — повторне повернення неможливе.')
        self.loan_id.write({
            'state': 'returned',
            'return_date': fields.Date.today(),
        })
        self.loan_id.copy_id.condition = self.condition_on_return
        return {'type': 'ir.actions.act_window_close'}
