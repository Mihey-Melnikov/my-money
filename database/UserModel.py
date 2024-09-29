from database.DatabaseManager import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class UserModel(Base):
    '''
    Модель пользователя
    '''
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    
    categories = relationship('CategoryModel', back_populates='user')
    transactions = relationship('TransactionModel', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"