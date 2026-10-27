# erp-library-rental

Odoo-модуль library_rental для обліку видач книжкових примірників.

## Що виправлено вручну

- Файл '__init__.py' створився без підкреслень ('init.py'), тому я перейменувала його командою mv.
- heredoc для .gitignore завис ('heredoc>'). Я вийшла через Ctrl+C і створила файл через printf.
- У addons залишила лише library_rental, бо інші модулі Odoo не потрібні.

## Перевірки

- .gitignore містить venv/, __pycache__/, .idea/, odoo.conf.
- Модуль з’явився в списку застосунків і встановився без ERROR у консолі.

## Документація модуля

Бізнес-логіка модуля описана в addons/library_rental/README.md
