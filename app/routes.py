from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, Items, RegistrationForm, AddBookForm
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import db
from app.models import User, book, cart
from flask_login import logout_user, login_required
from urllib.parse import urlsplit

@app.route('/')
@app.route('/index')
@login_required
def index():
    form = Items()
    books = book.query.all()
    return render_template("index.html", title='Home Page', form=form, books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/kurv', methods=['GET', 'POST'])
def kurv():
    cart_items = cart.query.filter_by(user_id=current_user.id).all()
    return render_template('kurv.html', title='Kurv', cart_items=cart_items)

@app.route('/tiloej/kurv/<int:book_id>', methods=['GET', 'POST'])
def tilføj_til_kurv(book_id):
    product = book.query.get_or_404(book_id)
    quantity = int(request.form.get('quantity', 1))

    cart_item = cart.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = cart(user_id=current_user.id, quantity=quantity, book_id=product.id)
        db.session.add(cart_item)
        db.session.commit()    
   
    return redirect(url_for("kurv"))

@app.route('/fjern/kurv/<int:book_id>', methods=['GET', 'POST'])
def fjern_fra_kurv(cart_item_id):
    cart_item = cart.query.get_or_404(cart_item_id)
    if cart_item.user_id != current_user.id:
        return redirect(url_for('kurv'))

    db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for("kurv"))

@app.route('/addbook', methods=['GET', 'POST'])
def addbook():
    form = AddBookForm()
    if form.validate_on_submit():
        Book = book(name=form.book_name.data, author=form.book_author.data, release_year=form.book_release.data, pris=form.book_pris.data)
        db.session.add(Book)
        db.session.commit()
        flash('Congratulations, your book is now registered!')
    return render_template('addbook.html', title='addbook', form=form)