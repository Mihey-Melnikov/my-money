import telebot

class MyMoneyBot:
    def __init__(self, token, db_manager):
        self.bot = telebot.TeleBot(token)
        self.db_manager = db_manager
        self.current_action = None
        self.add_handlers()

    def add_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            user = message.from_user
            self.db_manager.add_user(user.id, user.first_name)
            self.bot.send_message(message.chat.id, f"Привет, {user.first_name}! Это твой персональный бюджет-трекер.")

        @self.bot.message_handler(commands=['add_income'])
        def add_income(message):
            self.current_action = 'income'
            self.bot.send_message(message.chat.id, "Введите сумму дохода и описание через запятую (Пример: 1000, Зарплата)")

        @self.bot.message_handler(commands=['add_expense'])
        def add_expense(message):
            self.current_action = 'expense'
            self.bot.send_message(message.chat.id, "Введите сумму расхода, описание и категорию через запятую (Пример: 500, Продукты, Еда)")

        @self.bot.message_handler(commands=['add_category'])
        def add_category(message):
            self.current_action = 'category'
            self.bot.send_message(message.chat.id, "Введите название категории и ее описание через запятую (Пример: Рестораны, поход в ресторан)")

        @self.bot.message_handler(content_types=['text'])
        def process_action(message):
            try:
                user_id = message.from_user.id
                if self.current_action == 'income':
                    income_data = message.text.split(',')
                    amount = float(income_data[0].strip())
                    description = income_data[1].strip()
                    self.db_manager.add_transaction(user_id, amount, description, "Доход")
                    self.bot.send_message(message.chat.id, "Доход добавлен!")

                elif self.current_action == 'expense':
                    expense_data = message.text.split(',')
                    amount = -float(expense_data[0].strip())
                    description = expense_data[1].strip()
                    category = expense_data[2].strip()
                    self.db_manager.add_transaction(user_id, amount, description, category)
                    self.bot.send_message(message.chat.id, "Расход добавлен!")

                elif self.current_action == 'category':
                    category_data = message.text.split(',')
                    name = category_data[0].strip()
                    description = category_data[1].strip()
                    self.db_manager.add_category(user_id, name, description)
                    self.bot.send_message(message.chat.id, "Категория добавлена!")
                
                self.current_action = None

            except Exception as e:
                self.bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте снова.")
                self.current_action = None

    def run(self):
        self.bot.polling()