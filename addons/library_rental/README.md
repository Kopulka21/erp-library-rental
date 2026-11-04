# library_rental: бізнес-логіка (Практичне заняття 3)

## Обчислювані поля
- `due_date` («Повернути до»): `compute`, `store=True`, `@api.depends('loan_date')`. Дата видачі + 14 днів (константа `LOAN_PERIOD_DAYS = 14`).
- `fine_amount` («Штраф, грн»): `store=True`, `@api.depends('return_date', 'due_date')`. Рахується лише коли `return_date` заповнена і пізніша за `due_date`: дні прострочення × `FINE_PER_DAY` (5 грн/день), в інших випадках 0.
- `is_overdue`: нестор-поле (без `store`), `@api.depends('state', 'due_date')`. Істина, якщо видача активна і `due_date` менша за сьогодні.

## onchange
- `@api.onchange('copy_id')` лише попереджає («Цей примірник уже має активну видачу»), збереження не блокує. У пошуку виключається поточний запис (`_origin.id`).

## Обмеження цілісності (@api.constrains)
1. `copy_id`, `state`: один примірник не може мати двох активних видач. Пошук інших видач виключає `rec.id`. Помилка: «Цей примірник уже виданий: у нього є інша активна видача.»
2. `loan_date`, `due_date`: `due_date` має бути пізніше за `loan_date`. Помилка: «Дата повернення має бути пізніше дати видачі.»
3. `loan_date`, `return_date`: фактична дата повернення не раніше дати видачі. Помилка: «Фактична дата повернення не може бути раніше дати видачі.»

## Ставка штрафу і термін видачі
- Термін видачі: 14 днів (`LOAN_PERIOD_DAYS`). Штраф: 5 грн за кожен день прострочення (`FINE_PER_DAY`). Обидва значення задані константами на початку `models/loan.py`.

## Що довелося виправити вручну після AI-генерації
- Бракувало імпорту `ValidationError`: додала `from odoo.exceptions import ValidationError`.
- У форму та список (view) не були додані поля `fine_amount` та `is_overdue`: додала вручну. Команда вставки спрацювала двічі і створила дублікати полів, їх прибрала скриптом.
- Віджет `statusbar` за замовчуванням не клікабельний, тому не можна було перевести видачу в «Повернена»: додала `options="{'clickable': '1'}"`.
- Додала метод `action_return` і кнопку «Повернути» (ставить стан «Повернена» і сьогоднішню дату повернення, якщо вона порожня).

## Безпека (Практичне заняття 4)

### Групи доступу
- Категорія «Бібліотека» (у Odoo 19 через `res.groups.privilege`), в ній дві незалежні групи: `group_library_librarian` («Бібліотекар») і `group_library_reader` («Читач»).
- Групи не успадковують одна одну, щоб record rule для Читача не діяв на Бібліотекаря.

### Поле user_id
- `library.member.user_id`: Many2one до `res.users`, не required, з `UNIQUE(user_id)`, щоб один користувач не був привʼязаний до кількох читачів.

### Права доступу (ir.model.access.csv)
- Бібліотекар: read/write/create/unlink = 1 на book, copy, member, loan.
- Читач: лише read на book, copy і loan; на member усі права 0.

### Record rule
- `rule_library_loan_reader` на `library.loan`: домен `[(member_id.user_id, =, user.id)]`, поле `groups` заповнене групою `group_library_reader`. Без `groups` правило стало б глобальним і приховало б видачі навіть від Бібліотекаря та адміністратора.

### Меню
- Корінь «Бібліотека» бачать обидві групи; Книги, Примірники, Читачі, Видачі лише Бібліотекар; «Мої видачі» лише Читач.

### Що довелося виправити після AI-генерації
- У Odoo 19 у `res.groups` немає поля `category_id`: додала запис `res.groups.privilege` і привʼязала групи через `privilege_id`.
- Файл `library_security.xml` підключений у `__manifest__.py` раніше за `ir.model.access.csv`.
- Рядки CSV для Читача не скопійовані з Бібліотекаря (`1,0,0,0` і `0,0,0,0`).

### Перевірка під Читачем
- Користувач `reader@test.com` бачить лише «Мої видачі» зі своєю видачею; прямий перехід до library.member дає помилку доступу.

## Практичне 5 — Wizard «Оформити повернення» та QWeb-звіт

### Що додано
- `models/return_wizard.py` — `library.return.wizard` (TransientModel): `loan_id`, `condition_on_return`, `notes`; `default_get` бере `loan_id` з `active_id`, якщо `active_model == 'library.loan'`; `action_confirm()` закриває видачу.
- `views/return_wizard_views.xml` — форма візарда та дія з `target="new"` (модальне вікно).
- Кнопка «Оформити повернення» на формі Loan: передає `default_loan_id` через контекст, видима лише для активних видач і лише Бібліотекарю.
- `report/report_member_loan_history.xml` — QWeb PDF-звіт «Історія видач читача» на моделі `library.member`, прив'язаний через `binding_model_id` (меню Друк на формі читача).

### Що згенерував AI
Каркас візарда, форму, дію-вікно і шаблон звіту — за зразками із завдання.

### Що виправлено вручну
- Додано рядок у `ir.model.access.csv` для `library.return.wizard` — з Odoo 14 TransientModel без прав доступу не відкривається.
- У кнопці контекст `{'default_loan_id': id}` замість `active_id` — у виразах view Odoo 17+ поточний запис доступний як `id`.
- `return_wizard_views.xml` підключено в `__manifest__.py` перед `loan_views.xml`, бо кнопка посилається на `%(action_library_return_wizard)d`.
- У зразку `report_name` вказував на шаблон, якого не існує (був лише `..._document`). Додано обгортку `report_member_loan_history` з `web.html_container`, кожен читач друкується з власною шапкою `web.external_layout`.
- Значення `condition_on_return` звірено з `library.copy.condition` (`new` / `good` / `damaged`).
- Прибрано `clickable` зі statusbar та стару кнопку `action_return` — вони дозволяли закрити видачу в обхід візарда, без дати повернення, штрафу й оновлення стану примірника.
- В `action_confirm()` додано перевірку, що видача ще активна (`UserError` при повторному поверненні).

### AI-рев'ю (Крок 6)
- **ensure_one / multi-record:** `action_confirm()` починається з `self.ensure_one()` і працює з одним записом, без циклу `for rec in self`.
- **Відповідність моделі звіту:** `ir.actions.report.model = library.member`, у шаблоні `t-foreach="docs"` ітерує читачів (`member`), а видачі беруться через `member.loan_ids` — модель і `report_name` збігаються з тим, що реально ітерується.

### Перевірка
- INV-001 (прострочена з 01.10): після візарда — стан «Повернена», дата повернення 04.11, штраф 170,00 грн (34 дні × 5 грн), стан примірника змінено на «Добрий»; `fine_amount` перерахувався автоматично через `@api.depends`.
- Звіт для читачки Марії Коваль (2 видачі) генерується з шапкою компанії.
- На macOS не встановлено wkhtmltopdf, тому Odoo показує звіт як HTML; PDF збережено через друк браузера з `/report/html/library_rental.report_member_loan_history/2`.

