# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer, TEXT, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()
engine_url = "sqlite:///restaurant.db"
engine = create_engine(engine_url, echo=True)


### Model ###

#餐廳
class Restaurant(Base):
    __tablename__ = "restaurant"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(TEXT)
    create_name = Column(TEXT)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

#使用者
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(TEXT)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

#評論 & 評分
class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(TEXT)
    restaurantName =  Column(TEXT)  
    comment = Column(TEXT)
    score = Column(Integer)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

### SQL Function ###

def create_table():
    Base.metadata.create_all(engine)


def drop_table():
    Base.metadata.drop_all(engine)


def create_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

if __name__ == '__main__':
    drop_table()
    create_table()
