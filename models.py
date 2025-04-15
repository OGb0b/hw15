from sqlalchemy import (Column, Integer, String, Text, ForeignKey, DECIMAL, TIMESTAMP, CheckConstraint, column, VARCHAR)
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.sql.ddl import CreateTable
import warnings


warnings.filterwarnings('ignore')
Base = declarative_base()


class Books(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(VARCHAR(100), nullable=False)
    author = Column(VARCHAR(50), nullable=False)
    published_year = Column(Integer)
    quantity = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_quantity_positive'),
    )

    def __repr__(self):
        return f""""<Books(id={self.id}, title={self.title}, author={self.author}, published_year={self.published_year},
                quantity={self.quantity})>"""

class Readers(Base):
    __tablename__ = 'readers'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(100), nullable=False)
    email = Column(VARCHAR(100), unique=True)

    def __repr__(self):
        return f"<Readers(id={self.id}, name={self.name}, email={self.email})>"

class BorrowedBooks(Base):
    __tablename__ = 'borrowedbooks'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    reader_id = Column(Integer, ForeignKey('readers.id'))
    borrow_date = Column(TIMESTAMP, default=datetime.now)
    return_date = Column(TIMESTAMP, nullable=True)

    book = relationship('Books', back_populates='borrowedbooks')
    reader = relationship('Readers', back_populates='borrowedbooks')

    def __repr__(self):
        return f""""<BorrowedBooks(id={self.id}, book_id{self.book_id}, reader_id={self.reader_id}, 
                borrow_date={self.borrow_date}, return_date={self.return_date})>"""


