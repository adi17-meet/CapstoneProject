from sqlalchemy import Column,Integer,String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, func
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key = True)
    name = Column(String())
    address = Column(String())
    email = Column(String())
    AllReviews = relationship("allreviews", uselist=False, back_populates="customer")
    photo = Column(String(), unique=True)
    password_hash = Column(String())
    orders = relationship("review", back_populates="customer")

    def hash_password(self, password):
        self.passowrd_hash = pwd_context.encrypt(password)

    def set_photo(self, photo):
        self.photo = photo

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

class AllReviews(Base):
    __tablename__ = 'allreviews'
    id = Column(Integer, primary_key=True)
    custom_app = Column(Integer, ForeignKey('customer.id'))
    custom = relationship("customer", back_populates="allreviews")
    products = relationship("allreviewsassociation", back_populates="allreviews")

class Review(Base):
    __tablename__ = "review"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    confirmation = Column(String, unique=True)
    products = relationship("reviewsassociation", back_populates="review")
    customer_id = Column(Integer, ForeignKey('customer.id'))
    customer = relationship("customer", back_populates="review")

class Product():
    __tablename__ = 'Products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    photo = Column(String)
    price = Column(Integer)
    reviews = relationship("reviewassociation", back_populates="products")
    AllReviews = relationship("allreviewsassociation", back_populates="product")


engine = create_engine('sqlite:///project.db')


Base.metadata.create_all(engine)


