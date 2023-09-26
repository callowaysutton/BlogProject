from flask import render_template, url_for, flash, redirect
from flask_login import login_user, current_user, login_required, logout_user
from app import app, db
from app.models import User
from app.forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Why would you be here otherwise??
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    # Passwords do not match...
    if (form.password.data != form.confirm_password.data):
        flash('Your passwords did not match!', 'danger')
        return redirect(url_for('register'))
    
    if form.validate_on_submit():
        # Hash the user's password and create a new User instance
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, password=hashed_password)

        # Add the new user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()  # Rollback changes in case of an error
            flash('An error occurred while creating your account. Please try again later.', 'danger')
            return redirect(url_for('register'))
            print(e)  # Print the error for debugging
    # else:
    #     flash('Username taken or passwords did not match!', 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Why would you be here otherwise??
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()


        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, form.password.data):
            # Set the user session
            login_user(user)
            flash('Login successful!', 'success')
            # You can implement a session-based login system here if needed
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required  # Ensure that only logged-in users can log out
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
