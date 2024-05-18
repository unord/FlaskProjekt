from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm, AddBookForm
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import db
from app.models import User, book, cart
from flask_login import logout_user, login_required
from urllib.parse import urlsplit

#Første rute som følger til vores index (shoppen)
@app.route('/')
@app.route('/index')
@login_required
def index():
    form = LoginForm()
#gemmer på alt fra database tabellen "book"
    books = book.query.all()

#Hvilket template den skal render og hvilke variabler den skal gemme
    return render_template("index.html", title='Home Page', books=books, form=form)

#Login ruten
@app.route('/login', methods=['GET', 'POST'])
#Login funktionen
def login():
#vi tjekker først om personen er logget ind i så fald bliver det sendt til index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
#Vi bruger "LoginForm" fra forms.py til at få input felter og submit knap
    form = LoginForm()
#Når man trykker på submit kanppen så ser den om User.username data er det samme som der står i input
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
#hvis man ikke er logget ind sender den en til login skærmen
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
#Her bruger den Flask_login til at logge folk ind med variablen user som den gemte før og ser om de vil huskes til en anden gang
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
#Den skrifter til index ruten efter man er logget ind
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

#Registrerings ruten 
@app.route('/register', methods=['GET', 'POST'])
def register():
#her der tjekker den om man er logget ind, hvis man er logget ind bliver man sendt til index i stedet
    if current_user.is_authenticated:
        return redirect(url_for('index'))
#vi bruger registationform fra forms.py
    form = RegistrationForm()

#når submit knappen bliver trykket sender den username input, email input og password og sender de ind til database tabellen User og commit til databasen
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

#kurv ruten
@app.route('/kurv', methods=['GET', 'POST'])
@login_required
def kurv():
#Vi definere variablen cart_items til den bestemte persons 
    cart_items = cart.query.filter_by(user_id=current_user.id).all()
    return render_template('kurv.html', title='Kurv', cart_items=cart_items)

#Ruten til at tilføje til en kurv med metoderne GET POST som tager fra og sender til serveren
@app.route('/tiloej/kurv/<int:book_id>', methods=['GET', 'POST'])
def tilføj_til_kurv(book_id):
#Her finder vi en bog fra databasen og hvis dne ikke kan findes så retunere den en 404 fejl i stedet
    product = book.query.get_or_404(book_id)
#Her henter dne fra html filen de informationer som quantity skal bruge
    quantity = int(request.form.get('quantity', 1))

#Her leder den i databasen efter brugerens id og bogens id, her bruges first til at få det første resultat eller intet resultat
    cart_item = cart.query.filter_by(user_id=current_user.id, book_id=product.id).first()

#Hvis dette allerede findes i databasen så sætter den oven i den eksisterende quantity
    if cart_item:
        cart_item.quantity += quantity
    else:
#Hvis dette ikke allerede eksistere sættere den infornmationen ind i databasen
        cart_item = cart(user_id=current_user.id, quantity=quantity, book_id=product.id)
        db.session.add(cart_item)
    db.session.commit()    
   
    return redirect(url_for("index"))

#Url til at fjerne fra kurven med metoden POST som sender data til serveren
@app.route('/fjern/kurv/<int:cart_item_id>', methods=['POST'])
def fjern_fra_kurv(cart_item_id):
#den tjekker om den eksistere produkterne er i cart databasen
    cart_item = cart.query.get_or_404(cart_item_id)

#Hvis id'et i cart databasen ikke er det samme som brugerens id så brugeren kun kan ændre sin egen kurv
    if cart_item.user_id != current_user.id:
        return redirect(url_for('kurv'))
    
#den fjerner fra cart databasen
    db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for("kurv"))

#Rute til at tilføje bøger ind i bog databasen
@app.route('/addbook', methods=['GET', 'POST'])
@login_required
def addbook():
#Bruger form for addbook
    form = AddBookForm()
#Når man trykker submit sendes alle informationerne ind i bog databasen
    if form.validate_on_submit():
        Book = book(name=form.book_name.data, author=form.book_author.data, release_year=form.book_release.data, pris=form.book_pris.data)
        db.session.add(Book)
        db.session.commit()
        flash('Congratulations, your book is now registered!')
    return render_template('addbook.html', title='addbook', form=form)