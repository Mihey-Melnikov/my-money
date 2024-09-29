from database.DatabaseManager import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class CategoryModel(Base):
    '''
    Модель категории
    '''
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('UserModel', back_populates='category')
    transactions = relationship('TransactionModel', back_populates='category')

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', user_id={self.user_id})>"