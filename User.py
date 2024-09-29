import Category


class User:
    '''
    Класс пользователя
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        self.categories = []

    def add_category(self, category_name, category_description):
        self.categories.append(Category(category_name, category_description))