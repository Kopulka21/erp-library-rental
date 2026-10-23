# Запуск: ./odoo-bin shell -d library_db --addons-path=... < shell_queries.py | tee orm_log.txt
from odoo import fields
today = fields.Date.today()

print("\n=== 1. Книги автора 'Іван Франко' ===")
books = env['library.book'].search([('author', '=', 'Іван Франко')])
print(books.mapped('name'))

print("\n=== 2. Вільні примірники 'Кобзар' ===")
kobzar = env['library.book'].search([('name', '=', 'Кобзар')], limit=1)
busy = env['library.loan'].search([('state', '=', 'active')]).mapped('copy_id')
free = env['library.copy'].search([('book_id', '=', kobzar.id), ('id', 'not in', busy.ids)])
print('Вільні:', free.mapped('inventory_number'), '| кількість:', len(free))
# те саме циклом:
free2 = kobzar.copy_ids.filtered(lambda c: not c.loan_ids.filtered(lambda l: l.state == 'active'))
print('Перевірка циклом:', len(free2))

print("\n=== 3. Прострочені видачі ===")
overdue = env['library.loan'].search([('state', '=', 'active'), ('due_date', '<', today)])
for l in overdue:
    print(l.display_name, '| до', l.due_date)

print("\n=== 4. create + write ===")
member = env['library.member'].search([('membership_number', '=', 'M-0003')], limit=1)
loan = env['library.loan'].create({'copy_id': free[0].id, 'member_id': member.id})
print('Створено:', loan.display_name, loan.state, loan.due_date)
loan.write({'state': 'returned', 'return_date': today})
print('Закрито:', loan.state, loan.return_date)
env.cr.commit()
