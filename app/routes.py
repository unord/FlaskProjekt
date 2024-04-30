from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm, Items

@app.route('/')
@app.route('/index')
def index():
    form = Items()
    user = {'username': 'wah wah'}

    return render_template('index.html', title='Home', user=user, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)

@app.route('/kurv', methods=['GET', 'POST'])
def kurv():
    form = LoginForm()
    return render_template('kurv.html', title='Kurv', form=form)