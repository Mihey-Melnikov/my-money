from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# Базовый класс для моделей
Base = declarative_base()

class UserModel(Base):
    '''
    Модель пользователя
    '''
    __tablename__ = 'user'
    telegram_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    current_state = Column(String, default=None)
    selected_category = Column(Integer, default=None)
    
    category = relationship('CategoryModel', back_populates='user')
    transaction = relationship('TransactionModel', back_populates='user')

    def __repr__(self):
        return f"<User(name={self.name}, telegram_id={self.telegram_id})>"


class TransactionModel(Base):
    '''
    Модель транзакции
    '''
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.telegram_id'))
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)

    user = relationship('UserModel', back_populates='transaction')
    category = relationship('CategoryModel', back_populates='transaction')

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, description='{self.description}', date='{self.date}')>"


class CategoryModel(Base):
    '''
    Модель категории
    '''
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.telegram_id'))

    user = relationship('UserModel', back_populates='category')
    transaction = relationship('TransactionModel', back_populates='category')

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class DatabaseManager:
    '''
    Класс для управления базой данных через ORM
    '''
    def __init__(self, db_url="sqlite:///my_money.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # Методы для работы с пользователями
    def add_user(self, telegram_id, name):
        user = self.session.query(UserModel).filter_by(telegram_id=telegram_id).first()
        if not user:
            new_user = UserModel(telegram_id=telegram_id, name=name)
            self.session.add(new_user)
            self.session.commit()
            return new_user
        return user

    def get_user(self, telegram_id):
        return self.session.query(UserModel).filter_by(telegram_id=telegram_id).first()
    
    def update_user_state(self, telegram_id, state):
        user = self.session.query(UserModel).filter_by(telegram_id=telegram_id).first()
        if user:
            user.current_state = state
            self.session.commit()
            return user
        return None
    
    def update_user_category(self, telegram_id, category):
        user = self.session.query(UserModel).filter_by(telegram_id=telegram_id).first()
        if user:
            user.selected_category = category
            self.session.commit()
            return user
        return None

    # Методы для работы с категориями
    def add_category(self, user_id, category_name, category_description):
        category = CategoryModel(name=category_name, user_id=user_id, description=category_description)
        self.session.add(category)
        self.session.commit()
        return category

    def get_categories(self, user_id):
        return self.session.query(CategoryModel).filter_by(user_id=user_id).all()

    # Методы для работы с транзакциями
    def add_transaction(self, user_id, amount, description, category_id):
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
