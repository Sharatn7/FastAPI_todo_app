from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

'''Creating a database model for users and todos. '''
''' The __tablename__ attribute is used to define the name of the table in the database. '''

'''
    The user table has the following columns:
    Columns
    ----------
    id: int
        the id of the user
    email:str
        the email of the user
    username:str
        the username of the user
    first_name:str
        the first name of the user
    last_name:str
        the last name of the user
    hashed_password:str
        the hashed password of the user
'''


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)

    todos = relationship("Todos", back_populates="owner")


''' 
    The todos table has the following columns:
    Columns
    ----------
    id: int
        the id of the todo
    title:str
        the title of the todo
    description:str
        the description of the todo
    owner_id:int
        the id of the owner of the todo

    owner_id which is a foreign key to the id column of the users table, 
is used to separate todos of different users.
'''


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="todos")
