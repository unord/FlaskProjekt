from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

#Databasen for bruger på hjemmesiden
class User(UserMixin, db.Model):
    __tablename__ = "User"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    cart_items: so.Mapped["cart"] = relationship(back_populates="user")

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
#Lavede til at hash password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
#Til at tjekke hashed password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
#Database for bøger
class book(db.Model):
    __tablename__ = "book"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=False, nullable=False)
    author: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=False, nullable=False)
    release_year: so.Mapped[int] = so.mapped_column(sa.Integer, index=True, nullable=False)
    pris: so.Mapped[int] = so.mapped_column(sa.Integer, index=True, nullable=False)
    cart_items: so.Mapped["cart"] = relationship(back_populates="book")


    def __repr__(self):
        return f'<Book {self.name}>'
    
#Kurvens database
class cart(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    user_id: so.Mapped[int] = so.mapped_column(ForeignKey("User.id"), nullable=False)
    book_id: so.Mapped[int] = so.mapped_column(ForeignKey("book.id"), nullable=False)

    user: so.Mapped["User"] = relationship(back_populates="cart_items")
    book: so.Mapped["book"] = relationship()

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))