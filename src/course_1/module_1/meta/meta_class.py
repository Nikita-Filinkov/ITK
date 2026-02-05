from datetime import datetime


class CreatedAtMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs["created_at"] = datetime.now()

        return super().__new__(mcs, name, bases, attrs)


class User(metaclass=CreatedAtMeta):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name} ({self.age} лет)"


class Product(metaclass=CreatedAtMeta):
    def __init__(self, title, price):
        self.title = title
        self.price = price

    def __repr__(self):
        return f"Product(title='{self.title}', price={self.price})"


user = User
product = Product
print(user.created_at)
print(product.created_at)
assert user.created_at
assert product.created_at
