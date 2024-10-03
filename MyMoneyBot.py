import telebot


class MyMoneyBot:
    '''
    Телеграм бот
    '''
    def __init__(self, token, db_manager):
        self.bot = telebot.TeleBot(token)
        self.db_manager = db_manager
        self.add_handlers()

    def add_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            user = message.from_user
            self.db_manager.add_user(user.id, user.first_name)
            self.bot.send_message(message.chat.id, f"Привет, {user.first_name}! Это твой персональный бюджет-трекер.")

        @self.bot.message_handler(commands=['add_income'])
        def add_income(message):
            # Логика для добавления доходов
            self.bot.send_message(message.chat.id, "Введите сумму дохода и описание через запятую (Пример: 1000, Зарплата)")

            @self.bot.message_handler(content_types=['text'])
            def process_income(message):
                try:
                    user_id = message.from_user.id
                    income_data = message.text.split(',')
                    amount = float(income_data[0].strip())
                    description = income_data[1].strip()
                    self.db_manager.add_transaction(user_id, amount, description, "Доход")
                    self.bot.send_message(message.chat.id, "Доход добавлен!")
                except Exception as e:
                    self.bot.send_message(message.chat.id, "Ошибка при добавлении дохода. Попробуйте снова.")

        @self.bot.message_handler(commands=['add_expense'])
        def add_expense(message):
            # Логика для добавления расходов
            self.bot.send_message(message.chat.id, "Введите сумму расхода, описание и категорию через запятую (Пример: 500, Продукты, Еда)")

            @self.bot.message_handler(content_types=['text'])
            def process_expense(message):
                try:
                    user_id = message.from_user.id
                    expense_data = message.text.split(',')
                    amount = -float(expense_data[0].strip())  # Отрицательное значение для расхода
                    description = expense_data[1].strip()
                    category = expense_data[2].strip()
                    self.db_manager.add_transaction(user_id, amount, description, category)
                    self.bot.send_message(message.chat.id, "Расход добавлен!")
                except Exception as e:
                    self.bot.send_message(message.chat.id, "Ошибка при добавлении расхода. Попробуйте снова.")
        
        @self.bot.message_handler(commands=['add_category'])
        def add_category(message):
            # логика добавления категорий
            self.bot.send_message(message.chat.id, "Введите название категории и ее описание через запятую (Пример: Рестораны, поход в ресторан)")

            @self.bot.message_handler(content_types=['text'])
            def process_category(message):
                try:
                    user_id = message.from_user.id
                    category_data = message.text.split(',')
                    name = category_data[0].strip()
                    description = category_data[1].strip()
                    self.db_manager.add_category(user_id, name, description)
                    self.bot.send_message(message.chat.id, "Категория добавлена!")
                except Exception as e:
                    self.bot.send_message(message.chat.id, "Ошибка при добавлении категории. Попробуйте снова.")


    def run(self):
        self.bot.polling()