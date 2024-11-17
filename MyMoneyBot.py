import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
from datetime import timedelta, datetime


class MyMoneyBot:
    def __init__(self, token, db_manager):
        self.bot = telebot.TeleBot(token)
        self.db_manager = db_manager
        self.add_handlers()
        self.buttons = {
            "add_category": "Добавить категорию 🗒",
            "add_income": "Добавить доход 📈",
            "add_expense": "Добавить расход 📉",
            "get_category": "Мои категории 📓",
            "get_statistics": "Статистика 💰",
            "del_category": "Удалить категорию ⛔️",
            "update_category": "Изменить категорию 🔄",
            "back_menu": "Вернуться в меню ↩️",
            "top_expense": "Топ трат",
            "top_income": "Топ дохода",
            "dynamics_expense": "Динамика трат",
            "dynamics_income": "Динамика дохода"
        }

    def main_menu(self):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            KeyboardButton(self.buttons["add_category"]),
            KeyboardButton(self.buttons["add_income"]),
            KeyboardButton(self.buttons["add_expense"]),
            KeyboardButton(self.buttons["get_category"]),
            KeyboardButton(self.buttons["get_statistics"])
        )
        return keyboard

    def categories_menu(self, user_id):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        categories = self.db_manager.get_categories(user_id)
        for category in categories:
            keyboard.add(KeyboardButton(f"🗒 {category.name}"))
        keyboard.add(KeyboardButton(self.buttons["back_menu"]))
        return keyboard
    
    def categories_action_menu(self):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            KeyboardButton(self.buttons["del_category"]),
            KeyboardButton(self.buttons["update_category"]),
            KeyboardButton(self.buttons["back_menu"])
        )
        return keyboard
    
    def statistics_action_menu(self):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            KeyboardButton(self.buttons["top_expense"]),
            KeyboardButton(self.buttons["top_income"]),
            KeyboardButton(self.buttons["dynamics_expense"]),
            KeyboardButton(self.buttons["dynamics_income"]),
            KeyboardButton(self.buttons["back_menu"])
        )
        return keyboard
    
    def calendar_menu(self):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            KeyboardButton("За последнюю неделю"),
            KeyboardButton("За последний месяц"),
            KeyboardButton("За последний квартал"),
            KeyboardButton("За последний год"),
            KeyboardButton("📅 Указать свою дату")
        )
        return keyboard

    def add_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            user = message.from_user
            self.db_manager.add_user(user.id, user.first_name)
            self.db_manager.update_user_state(message.from_user.id, None)
            self.db_manager.update_user_category(message.from_user.id, None)
            self.bot.send_message(
                message.chat.id,
                f"Привет, {user.first_name}! Это твой персональный бюджет-трекер. Выбери действие:",
                reply_markup=self.main_menu()
            )

        @self.bot.message_handler(func=lambda message: message.text == self.buttons["add_income"])
        def add_income(message):
            if not self.db_manager.get_categories(message.from_user.id):
                self.bot.send_message(
                    message.chat.id,
                    "У вас еще нет категорий, сначала добавьте категорию",
                    reply_markup=self.categories_menu(message.from_user.id)
                )
                return
            self.db_manager.update_user_state(message.from_user.id, "income")
            self.bot.send_message(
                message.chat.id,
                "Выберите категорию",
                reply_markup=self.categories_menu(message.from_user.id)
            )

        @self.bot.message_handler(func=lambda message: message.text == self.buttons["add_expense"])
        def add_expense(message):
            if not self.db_manager.get_categories(message.from_user.id):
                self.bot.send_message(
                    message.chat.id,
                    "У вас еще нет категорий, сначала добавьте категорию",
                    reply_markup=self.categories_menu(message.from_user.id)
                )
                return
            self.db_manager.update_user_state(message.from_user.id, "expense")
            self.bot.send_message(
                message.chat.id,
                "Выберите категорию",
                reply_markup=self.categories_menu(message.from_user.id)
            )

        @self.bot.message_handler(func=lambda message: message.text == self.buttons["add_category"])
        def add_category(message):
            self.db_manager.update_user_state(message.from_user.id, "category")
            self.bot.send_message(
                message.chat.id,
                "Введите название категории и ее описание через запятую",
                reply_markup=ReplyKeyboardRemove()
            )
        
        @self.bot.message_handler(func=lambda message: message.text == self.buttons["get_category"])
        def get_categories(message):
            categories = [[category.name, category.description] for category in self.db_manager.get_categories(message.from_user.id)]
            table_image = self.get_table(['Название', 'Описание'], categories)
            self.bot.send_photo(message.chat.id, table_image, caption="Ваши категории:")

        @self.bot.message_handler(func=lambda message: "🗒" in message.text)
        def add_transaction(message):
            self.db_manager.update_user_category(message.from_user.id, next(filter(lambda category: category.name in message.text, self.db_manager.get_categories(message.from_user.id)), None).id)
            user_state = self.db_manager.get_user(message.from_user.id).current_state
            self.bot.send_message(
                message.chat.id,
                f"Введите сумму {'дохода' if user_state == 'income' else 'расхода'} и описание через запятую",
                reply_markup=ReplyKeyboardRemove()
            )
        
        @self.bot.message_handler(func=lambda message: "📅 Указать свою дату" == message.text)
        def select_date(message):
            self.bot.send_message(
                message.chat.id, 
                "Напишите диапозон дат в формате dd.mm.yyyy - dd.mm.yyyy", 
                reply_markup=ReplyKeyboardRemove()
            )

        @self.bot.message_handler(func=lambda message: message.text == self.buttons["del_category"])
        def del_category(message):
            self.bot.send_message(message.chat.id, "Пока не реализовано", reply_markup=self.main_menu())

        @self.bot.message_handler(func=lambda message: message.text == self.buttons["update_category"])
        def update_category(message):
            self.bot.send_message(message.chat.id, "Пока не реализовано", reply_markup=self.main_menu())

        @self.bot.message_handler(func=lambda message: message.text == self.buttons["get_statistics"])
        def select_statistics(message):
            self.bot.send_message(
                message.chat.id,
                "Что вы хотите узнать?",
                reply_markup=self.statistics_action_menu()
            )

        @self.bot.message_handler(func=lambda message: message.text == self.buttons["top_expense"])
        def get_top_expense(message):
            self.db_manager.update_user_state(message.from_user.id, "top_expense")
            self.bot.send_message(message.chat.id, "Укажите дату для получения статистики", reply_markup=self.calendar_menu())
        
        @self.bot.message_handler(func=lambda message: message.text == self.buttons["top_income"])
        def get_top_income(message):
            self.db_manager.update_user_state(message.from_user.id, "top_income")
            self.bot.send_message(message.chat.id, "Укажите дату для получения статистики", reply_markup=self.calendar_menu())
        
        @self.bot.message_handler(func=lambda message: message.text == self.buttons["dynamics_expense"])
        def get_dynamics_expense(message):
            self.db_manager.update_user_state(message.from_user.id, "dynamics_expense")
            self.bot.send_message(message.chat.id, "Укажите дату для получения статистики", reply_markup=self.calendar_menu())
        
        @self.bot.message_handler(func=lambda message: message.text == self.buttons["dynamics_income"])
        def get_dynamics_income(message):
            self.db_manager.update_user_state(message.from_user.id, "dynamics_income")
            self.bot.send_message(message.chat.id, "Укажите дату для получения статистики", reply_markup=self.calendar_menu())
        
        @self.bot.message_handler(func=lambda message: message.text == self.buttons["back_menu"])
        def back_main_menu(message):
            self.bot.send_message(message.chat.id, "Выбери действие:", reply_markup=self.main_menu())

        @self.bot.message_handler(content_types=['text'])
        def process_action(message):
            try:
                user = self.db_manager.get_user(message.from_user.id)
                date_start = datetime.now()
                date_end = datetime.now()

                if user.current_state == 'income':
                    income_data = message.text.split(',')
                    amount = float(income_data[0].strip())
                    description = income_data[1].strip()
                    self.db_manager.add_transaction(user.telegram_id, amount, description, user.selected_category)
                    self.bot.send_message(message.chat.id, "Доход добавлен!", reply_markup=self.main_menu())

                elif user.current_state == 'expense':
                    expense_data = message.text.split(',')
                    amount = -float(expense_data[0].strip())
                    description = expense_data[1].strip()
                    self.db_manager.add_transaction(user.telegram_id, amount, description, user.selected_category)
                    self.bot.send_message(message.chat.id, "Расход добавлен!", reply_markup=self.main_menu())

                elif user.current_state == 'category':
                    category_data = message.text.split(',')
                    name = category_data[0].strip()
                    description = category_data[1].strip()
                    self.db_manager.add_category(user.telegram_id, name, description)
                    self.bot.send_message(message.chat.id, "Категория добавлена!", reply_markup=self.main_menu())
                
                elif user.current_state == 'top_expense':
                    date_start, date_end = self.parse_date(message.text)
                    transactions = [[transaction.description, abs(transaction.amount)] 
                                    for transaction in self.db_manager.get_transactions(
                                        user.telegram_id, date_start, date_end, 'expense')]
                    transactions.sort(key=lambda x: (-x[1], x[0]))
                    table_image = self.get_table(['Название', 'Сумма'], transactions)
                    self.bot.send_photo(message.chat.id, 
                                        table_image, 
                                        reply_markup=self.main_menu(), 
                                        caption=f"Топ трат с {date_start.strftime('%d.%m.%Y')} по {date_end.strftime('%d.%m.%Y')}:")
                
                elif user.current_state == 'top_income':
                    date_start, date_end = self.parse_date(message.text)
                    self.bot.send_message(message.chat.id, "top_income", reply_markup=self.main_menu())
                
                elif user.current_state == 'dynamics_expense':
                    date_start, date_end = self.parse_date(message.text)
                    self.bot.send_message(message.chat.id, "dynamics_expense", reply_markup=self.main_menu())
                
                elif user.current_state == 'dynamics_income':
                    date_start, date_end = self.parse_date(message.text)
                    self.bot.send_message(message.chat.id, "dynamics_income", reply_markup=self.main_menu())

                self.db_manager.update_user_state(message.from_user.id, None)
                self.db_manager.update_user_category(message.from_user.id, None)

            except Exception as e:
                self.bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте снова.", reply_markup=self.main_menu())
                self.db_manager.update_user_state(message.from_user.id, None)
                self.db_manager.update_user_category(message.from_user.id, None)
                print(e)

    def parse_date(self, input):
        date_start = datetime.now()
        date_end = datetime.now()

        if ' - ' in input:
            date_start_str, date_end_str = input.split(' - ')
            date_start = datetime.strptime(date_start_str, "%d.%m.%Y")
            date_end = datetime.strptime(date_end_str, "%d.%m.%Y") + timedelta(seconds=86399) # сутки - 1 секунда, чтобы входили траты за день
        elif input == 'За последнюю неделю':
            date_start = datetime.now() - timedelta(days=7)
            date_end = datetime.now()
        elif input == 'За последний месяц':
            date_start = datetime.now() - timedelta(days=30)
            date_end = datetime.now()
        elif input == 'За последний квартал':
            date_start = datetime.now() - timedelta(days=90)
            date_end = datetime.now()
        elif input == 'За последний год':
            date_start = datetime.now() - timedelta(days=365)
            date_end = datetime.now()
        else:
            raise ValueError("Неверное значение даты")

        return date_start, date_end

    def get_table(self, head, data):
        col_labels = head
        fig, ax = plt.subplots(figsize=(5, len(data) * 0.4))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=data, colLabels=col_labels, cellLoc="left", loc="center")
        for j, label in enumerate(col_labels):
            header_cell = table[0, j]
            header_cell.set_text_props(weight='bold', color='black')
            header_cell.set_facecolor('#f0f0f0')
        for i in range(1, len(data) + 1): 
            for j in range(len(col_labels)):
                table[i, j].set_text_props(ha="left")
        image_stream = BytesIO()
        plt.savefig(image_stream, format='png', bbox_inches='tight', pad_inches=0.05)
        image_stream.seek(0)
        plt.close(fig)

        return image_stream

    def run(self):
        self.bot.polling()
