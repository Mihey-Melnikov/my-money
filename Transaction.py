from datetime import datetime


class Transaction:
    '''
    Класс транзакции (доходы и расходы)
    '''
    def __init__(self, amount, description, category, type, date=None):
        self.amount = amount
        self.description = description
        self.category = category
        self.date = date if date else datetime.now()
