import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import matplotlib.pyplot as plt
from io import BytesIO


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
            col_labels = ['Название', 'Описание']
            fig, ax = plt.subplots()
            ax.axis('tight')
            ax.axis('off')
            ax.table(cellText=categories, colLabels=col_labels, cellLoc="center", loc="center")
            image_stream = BytesIO()
            plt.savefig(image_stream, format='png')
            image_stream.seek(0)
            plt.close(fig)
            self.bot.send_photo(message.chat.id, image_stream, caption="Ваши категории:")

        @self.bot.message_handler(func=lambda message: "🗒" in message.text)
        def add_transaction(message):
            self.db_manager.update_user_category(message.from_user.id, next(filter(lambda category: category.name in message.text, self.db_manager.get_categories(message.from_user.id)), None).id)
            user_state = self.db_manager.get_user(message.from_user.id).current_state
            self.bot.send_message(
                message.chat.id,
                f"Введите сумму {'дохода' if user_state == 'income' else 'расхода'} и описание через запятую",
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
            self.bot.send_message(message.chat.id, "Пока не реализовано", reply_markup=self.main_menu())
        
        @self.bot.message_handler(func=lambda message: message.text == self.buttons["top_income"])
        def get_top_income(message):
            self.bot.send_message(message.chat.id, "Пока не реализовано", reply_markup=self.main_menu())
        
        @self.bot.message_handler(func=lambda message: message.text == self.buttons["dynamics_expense"])
        def get_dynamics_expense(message):
            self.bot.send_message(message.chat.id, "Пока не реализовано", reply_markup=self.main_menu())
        
        @self.bot.message_handler(func=lambda message: message.text == self.buttons["dynamics_income"])
        def get_dynamics_income(message):
            self.bot.send_message(message.chat.id, "Пока не реализовано", reply_markup=self.main_menu())
        
        @self.bot.message_handler(func=lambda message: message.text == self.buttons["back_menu"])
        def back_main_menu(message):
            self.bot.send_message(message.chat.id, "Выбери действие:", reply_markup=self.main_menu())

        @self.bot.message_handler(content_types=['text'])
        def process_action(message):
            try:
                user = self.db_manager.get_user(message.from_user.id)

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

                self.db_manager.update_user_state(message.from_user.id, None)
                self.db_manager.update_user_category(message.from_user.id, None)

            except Exception as e:
                self.bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, попробуйте снова.", reply_markup=self.main_menu())
                self.db_manager.update_user_state(message.from_user.id, None)
                self.db_manager.update_user_category(message.from_user.id, None)
                print(e)

    def run(self):
        self.bot.polling()
