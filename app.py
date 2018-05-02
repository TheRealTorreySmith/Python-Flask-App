# IMPORTS
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from twilio.rest import Client
from twilio.twiml.voice_response import Play, VoiceResponse, Say
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
import os

app = Flask(__name__)

# CONFIG MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'torrey'
app.config['MYSQL_PASSWORD'] = 'Tfresh.2217'
app.config['MYSQL_DB'] = 'py_flask_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

# INITIALIZE MYSQL
mysql = MySQL(app)

# LANDING PAGE ROUTE
@app.route('/')
def landing():
    return render_template('landing.html')

# DROPDOWN MENU ROUTES
# ABOUT ROUTE
@app.route('/about')
def about():
    return render_template('about.html')

# SHARE ROUTE
@app.route('/share')
def share():
    return render_template('share.html')

# CONTACT ROUTE
@app.route('/contact')
def contact():
    return render_template('contact.html')

# REGISTER FORM
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=6, max=18)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match!')
        ])
    confirm = PasswordField('Confirm Password')

# REGISTER ROUTE
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # CREATE CURSOR
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)
            """, (name, email, username, password))

        # COMMIT TO DB
        mysql.connection.commit()

        # CLOSE CONNECTION
        cur.close()

        # FLASH MESSAGE
        flash('You are now registered and can login!', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# USER LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # GET FORM FIELDS
        username = request.form['username']
        password_candidate = request.form['password']

        # CREATE CURSOR
        cur = mysql.connection.cursor()

        # GET USER BY USERNAME
        result = cur.execute("""
            SELECT * FROM users WHERE username = %s
            """, [username])

        if result > 0:
            # GET STORED HASH
            data = cur.fetchone()
            password = data['password']

            # COMPARE PASSWORDS
            if sha256_crypt.verify(password_candidate, password):

                # PASSED
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login!'
                return render_template('login.html', error=error)

            # CLOSE CONNECTION
            cur.close()
        else:
            error = 'Username not found!'
            return render_template('login.html', error=error)

    return render_template('login.html')

# CHECK IF USER IS LOGGED IN
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# LOGOUT ROUTE
@app.route('/logout')
def logout():
    session.clear()
    flash('You successfully logged out!', 'success')
    return redirect(url_for('login'))

# RESET PASSWORD
@app.route('/setpass', methods=['GET', 'POST'])
def setpass():
    if request.method == 'POST' and request.form['new-password'] == request.form['confirm-password']:

        # GET FORM FIELDS
        username = request.form['username']
        old_password = request.form['old-password']
        new_password = request.form['new-password']
        confirm_password = request.form['confirm-password']

        # CREATE CURSOR
        cur = mysql.connection.cursor()

        # GET USER BY USERNAME
        result = cur.execute("""
            SELECT * FROM users WHERE username = %s
            """, [username])

        if result > 0:

            # GET STORED HASH
            data = cur.fetchone()
            password = data['password']

            # COMPARE PASSWORDS
            if sha256_crypt.verify(old_password, password):

                new_hash_pass = sha256_crypt.encrypt(str(new_password))

                # PASSED
                update = cur.execute("""
                    UPDATE users
                    SET password = %s
                    WHERE username = %s
                    """, [new_hash_pass, username])

                # COMMIT TO DB
                mysql.connection.commit()

                # CLOSE CONNECTION
                cur.close()

                flash('Your password has successfully been changed!', 'success')
                return redirect(url_for('login'))
            else:
                error = 'Invalid username or password!'
                return render_template('setpass.html', error=error)

        else:
            error = 'Username not found!'
            return render_template('setpass.html', error=error)

    return render_template('setpass.html')

# DASHBOARD ROUTE
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    if request.method == 'POST':
       # CONFIG TWILIO
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        call = client.calls.create(
                                url='https://demo.twilio.com/welcome/voice/',
                                from_=os.getenv('FROM_PHONE_NUMBER'),
                                to=os.getenv('TO_PHONE_NUMBER')
                            )

        print(call.sid)
    
    # response = VoiceResponse()
    # response.say('Hello World')
    # response.play('https://api.twilio.com/Cowbell.mp3')
    #
    # print(response)
        return render_template('dashboard.html')

# HISTORY ROUTE

@app.route('/history')
@is_logged_in
def history():
    return render_template('history.html')

# DELETE ROUTE
@app.route('/delete')
@is_logged_in
def delete():
    return render_template('delete.html')

if __name__ == '__main__':
    # GET SECRET_KEY
    app.secret_key = os.environ.get('SECRET_KEY', None)
    app.run(debug=True)
