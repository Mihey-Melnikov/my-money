from database.DatabaseManager import DatabaseManager
from MyMoneyBot import MyMoneyBot


# Инициализация
if __name__ == "__main__":
    db_manager = DatabaseManager()
    bot = MyMoneyBot(token="8062202014:AAGewJa8LUl7nnCUDtVI4n6Q1NZhQ5KM8Go", db_manager=db_manager)
    bot.run()
