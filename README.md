## Требования

Написать приложение, в котором пользователи могут добавлять свои доходы и расходы, задавать категории транзакций и просматривать аналитику по ним.

Пользовательский флоу:
- Пользователь может ввести сумму дохода, его описание;
- Пользователь может создать собственные категории;
- Пользователь может ввести сумму расхода и категорию;
- Пользователь может запросить статистику расходов по промежутку дат (день, неделя, месяц, квартал, год). Статистику можно выводить топ трат в виде таблицы, а все остальное в виде графиков.

## База данных

- user
  - id
  - name
  - tg
- category
  - id
  - name
  - user_id
  - created_at
  - deleted_at
- transaction
  - id
  - name
  - category_id
  - user_id
  - created_at
  - deleted_at

## Чат ЖПТ

Для реализации приложения на Python, можно использовать следующие библиотеки и инструменты:

1. **Telegram Bot API** – для взаимодействия с пользователем через Telegram.
2. **SQLite** – в качестве открытой базы данных.
3. **matplotlib** и **pandas** – для анализа данных и построения графиков.

### Структура проекта
- **User**: класс для хранения информации о пользователе (доходы, расходы, категории).
- **Transaction**: класс для создания транзакций (доходы и расходы).
- **Category**: класс для управления категориями.
- **DatabaseManager**: класс для работы с базой данных.
- **Analytics**: класс для предоставления статистики.

### Пример структуры классов

```python
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# Класс пользователя
class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.categories = []

    def add_category(self, category_name):
        self.categories.append(Category(category_name))

# Класс транзакции (доходы и расходы)
class Transaction:
    def __init__(self, amount, description, category, date=None):
        self.amount = amount
        self.description = description
        self.category = category
        self.date = date if date else datetime.now()

# Класс для работы с категориями
class Category:
    def __init__(self, name):
        self.name = name

# Класс для управления базой данных
class DatabaseManager:
    def __init__(self, db_name="budget_tracker.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Создаем таблицы для хранения данных
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                                id INTEGER PRIMARY KEY,
                                user_id INTEGER,
                                amount REAL,
                                description TEXT,
                                category TEXT,
                                date TEXT)''')
        self.connection.commit()

    def add_transaction(self, user_id, amount, description, category):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO transactions (user_id, amount, description, category, date) VALUES (?, ?, ?, ?, ?)",
                            (user_id, amount, description, category, date))
        self.connection.commit()

    def get_transactions(self, user_id, start_date, end_date):
        self.cursor.execute("SELECT * FROM transactions WHERE user_id=? AND date BETWEEN ? AND ?",
                            (user_id, start_date, end_date))
        return self.cursor.fetchall()

# Класс для аналитики
class Analytics:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_expense_statistics(self, user_id, start_date, end_date):
        transactions = self.db_manager.get_transactions(user_id, start_date, end_date)
        df = pd.DataFrame(transactions, columns=['id', 'user_id', 'amount', 'description', 'category', 'date'])
        expense_df = df[df['amount'] < 0]
        top_expenses = expense_df.groupby('category')['amount'].sum().sort_values(ascending=True)
        return top_expenses

    def plot_expenses(self, user_id, start_date, end_date):
        statistics = self.get_expense_statistics(user_id, start_date, end_date)
        statistics.plot(kind='bar')
        plt.title(f"Top Expenses from {start_date} to {end_date}")
        plt.xlabel('Category')
        plt.ylabel('Amount')
        plt.savefig('expenses.png')

# Телеграм бот
class BudgetBot:
    def __init__(self, token, db_manager):
        self.bot = Bot(token=token)
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.db_manager = db_manager
        self.add_handlers()

    def add_handlers(self):
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('add_income', self.add_income))
        self.dispatcher.add_handler(CommandHandler('add_expense', self.add_expense))
        self.dispatcher.add_handler(CommandHandler('get_stats', self.get_stats))

    def start(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        update.message.reply_text(f"Привет, {user.first_name}! Это твой персональный бюджет-трекер.")

    def add_income(self, update: Update, context: CallbackContext):
        # Логика для добавления доходов
        pass

    def add_expense(self, update: Update, context: CallbackContext):
        # Логика для добавления расходов
        pass

    def get_stats(self, update: Update, context: CallbackContext):
        # Логика для запроса статистики
        pass

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

# Инициализация
if __name__ == "__main__":
    db_manager = DatabaseManager()
    bot = BudgetBot(token="YOUR_BOT_TOKEN", db_manager=db_manager)
    bot.run()
```

### Описание
1. **User** – класс для хранения информации о пользователе и категориях.
2. **Transaction** – описывает транзакцию.
3. **Category** – управляет категориями.
4. **DatabaseManager** – отвечает за работу с базой данных, создаёт таблицы, добавляет транзакции и предоставляет доступ к данным.
5. **Analytics** – предоставляет аналитику по расходам.
6. **BudgetBot** – телеграм бот, который взаимодействует с пользователем.

### Дополнения
- Телеграм-бот будет получать команды от пользователя (например, `/add_income`, `/add_expense`) и сохранять информацию в базу данных.
- Для графиков расходов используется `matplotlib`.
- Статистика отображается в виде таблиц или графиков, сохраняемых в изображениях.

Это базовый каркас приложения, который можно дополнить и улучшить.
