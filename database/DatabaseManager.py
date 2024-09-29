from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from database.CategoryModel import CategoryModel
from database.TransactionModel import TransactionModel
from database.UserModel import UserModel

# Базовый класс для моделей
Base = declarative_base()

# Класс для управления базой данных через ORM
class DatabaseManager:
    def __init__(self, db_url="sqlite:///budget_tracker.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # Методы для работы с пользователями
    def add_user(self, telegram_id):
        user = self.session.query(UserModel).filter_by(telegram_id=telegram_id).first()
        if not user:
            new_user = UserModel(telegram_id=telegram_id)
            self.session.add(new_user)
            self.session.commit()
            return new_user
        return user

    def get_user(self, telegram_id):
        return self.session.query(UserModel).filter_by(telegram_id=telegram_id).first()

    # Методы для работы с категориями
    def add_category(self, user_id, category_name):
        category = CategoryModel(name=category_name, user_id=user_id)
        self.session.add(category)
        self.session.commit()
        return category

    def get_categories(self, user_id):
        return self.session.query(CategoryModel).filter_by(user_id=user_id).all()

    # Методы для работы с транзакциями
    def add_transaction(self, user_id, amount, description, category_id=None):
        transaction = TransactionModel(
            user_id=user_id,
            amount=amount,
            description=description,
            category_id=category_id
        )
        self.session.add(transaction)
        self.session.commit()
        return transaction

    def get_transactions(self, user_id, start_date, end_date):
        return self.session.query(TransactionModel).filter(
            TransactionModel.user_id == user_id,
            TransactionModel.date >= start_date,
            TransactionModel.date <= end_date
        ).all()

    def close(self):
        self.session.close()
