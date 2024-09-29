from database.DatabaseManager import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from datetime import datetime


class TransactionModel(Base):
    '''
    Модель транзакции
    '''
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    user = relationship('UserModel', back_populates='transaction')
    category = relationship('CategoryModel', back_populates='transaction')

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, description='{self.description}', date='{self.date}')>"