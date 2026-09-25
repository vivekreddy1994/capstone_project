class Book:
    def __init__(self, title, price, star_rating, availability, category):
        self.title = title
        self.price = price
        self.star_rating = star_rating
        self.availability = availability
        self.category = category

class Category:
    def __init__(self, name):
        self.name = name