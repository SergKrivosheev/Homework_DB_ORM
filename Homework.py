import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import json

Base = declarative_base()

class Publisher(Base):
    __tablename__ = "publisher"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'Publisher {self.id}: {self.name}'

class Book(Base):
    __tablename__ = "book"

    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=80), unique=True)
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey("publisher.id"), nullable=False)

    publisher = relationship(Publisher, backref="publisher")

class Shop(Base):
    __tablename__ = "shop"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'Shop {self.id}: {self.name}'

class Stock(Base):
    __tablename__ = "stock"

    id = sq.Column(sq.Integer, primary_key=True)
    id_book = sq.Column(sq.Integer, sq.ForeignKey("book.id"), nullable=False)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey("shop.id"), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)

    book = relationship(Book, backref="book")
    shop = relationship(Shop, backref="shop")

class Sale(Base):
    __tablename__ = "sale"

    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.DECIMAL(18, 2), nullable=False)
    date_sale = sq.Column(sq.Date, nullable=False)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey("stock.id"), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)

    stock = relationship(Stock, backref="stock")


def create_tables(engine):
    Base.metadata.create_all(engine)

def delete_tables(engine):
    Base.metadata.drop_all(engine)

db_type="postgresql"
username="postgres"
password="051289KsV!"

DSN = f"{db_type}://{username}:{password}@localhost:5432/postgres"

engine = sq.create_engine(DSN)
delete_tables(engine)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()
with open('tests_data.json', encoding='utf-8-sig') as f:
    data = json.load(f)
    for info in data:
        if info["model"] == 'publisher':
            obj = Publisher(name=info["fields"]["name"])
            session.add(obj)
            session.commit()
        elif info["model"] == "book":
            obj = Book(title=info["fields"]["title"], id_publisher=info["fields"]["id_publisher"])
            session.add(obj)
            session.commit()
        elif info["model"] == "shop":
            obj = Shop(name=info["fields"]["name"])
            session.add(obj)
            session.commit()
        elif info["model"] == "stock":
            obj = Stock(id_book=info["fields"]["id_book"], id_shop=info["fields"]["id_shop"], count=info["fields"]["count"])
            session.add(obj)
            session.commit()
        elif info["model"] == "sale":
            obj = Sale(price=info["fields"]["price"], date_sale=info["fields"]["date_sale"],
                       count=info["fields"]["count"], id_stock=info["fields"]["id_stock"])
            session.add(obj)
            session.commit()
parameter = input('Введите название или id издателя ')

if parameter.isnumeric():
    subq = session.query(Stock).join(Stock.shop).join(Stock.book).join(Book.publisher).filter(Publisher.id == parameter).subquery()
else:
    subq = session.query(Stock).join(Stock.shop).join(Stock.book).join(Book.publisher).filter(Publisher.name == parameter).subquery()

s = session.query(Shop).join(subq, Shop.id == subq.c.id_shop)
for o in s:
    print(o.id)

session.close()
