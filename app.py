# IMPORTS
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, json
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, HiddenField, BooleanField, SubmitField, validators
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

# CONFIG LOCAL MYSQL
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'torrey'
# app.config['MYSQL_PASSWORD'] = 'Tfresh.2217'
# app.config['MYSQL_DB'] = 'py_flask_app'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# GET SECRET_KEY
app.secret_key = os.environ.get('SECRET_KEY')

# CONFIG HEROKU MYSQL
app.config['MYSQL_HOST'] = 'us-cdbr-iron-east-04.cleardb.net'
app.config['MYSQL_USER'] = 'b8510b849508af'
app.config['MYSQL_PASSWORD'] = '93d2ce70'
app.config['MYSQL_DB'] = 'heroku_d9cecbb9ca72dc8'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

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

# DASHBOARD CALL FORM
class CallForm(Form):
    phoneNumber = StringField('phoneNumber', [validators.Length(min=10, max=10)])
    message = StringField('message', [validators.Length(min=6, max=300)])
    recordConversation = BooleanField('Record Conversation')
    SaveToHistory = BooleanField('Save To History')
    makeCall = BooleanField('Make A Call')
    sendText = BooleanField('Send A Text')
    saveToHistory = BooleanField('Save To History')

# DASHBOARD ROUTE
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    form = CallForm(request.form)
    if request.method == 'POST' and form.saveToHistory.data:
        # GET CALL FORM FIELDS
        username = request.form['currentUser']
        phoneNumber = request.form['phoneNumber']
        if form.makeCall.data:
            method = "Call"
        else:
            method = "Text"
        message = request.form['message']

        # CREATE CURSOR
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO contacts(username, phone_number, method, message) VALUES(%s, %s, %s, %s)
            """, (username, phoneNumber, method, message))

        # COMMIT TO DB
        mysql.connection.commit()

        # FETCHES DATA
        data = cur.fetchall()

        # CLOSE CONNECTION
        cur.close()

    if request.method == 'POST' and form.makeCall.data:

        # GET CALL FORM FIELDS
        phoneNumber = request.form['phoneNumber']
        message = request.form['message']

        # CONFIG TWILIO
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        os.environ['TO_PHONE_NUMBER'] = phoneNumber
        os.environ['MESSAGE'] = message

        call = client.calls.create(
                                url=os.getenv('VOICE_URL'),
                                from_=os.getenv('FROM_PHONE_NUMBER'),
                                to=os.getenv('TO_PHONE_NUMBER')
                                )
        print(call.sid)

        return render_template('dashboard.html', form=form)

    if request.method == 'POST' and form.sendText.data:

        # GET CALL FORM FIELDS
        phoneNumber = request.form['phoneNumber']
        message = request.form['message']

        # CONFIG TWILIO
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        os.environ['TO_PHONE_NUMBER'] = phoneNumber
        os.environ['MESSAGE'] = message

        message = client.messages \
            .create(
                 body=os.getenv('MESSAGE'),
                 from_=os.getenv('FROM_PHONE_NUMBER'),
                 to=os.getenv('TO_PHONE_NUMBER')
             )

        print(message.sid)
        return render_template('dashboard.html', form=form)
    else:
        return render_template('dashboard.html')

# TWIML RESPONSE ROUTE
# @app.route("/voice", methods=['GET', 'POST'])
# def voice():
#
#     # CONFIG TWILIO
#     account_sid = os.getenv('TWILIO_ACCOUNT_SID')
#     auth_token = os.getenv('TWILIO_AUTH_TOKEN')
#     client = Client(account_sid, auth_token)
#
#     # GET CALL FORM FIELDS
#     phoneNumber = request.form['phoneNumber']
#     message = request.form['message']
#
#     # Start our TwiML response
#     resp = VoiceResponse()
#
#     os.environ['MESSAGE'] = message
#
#     # Read a message aloud to the caller
#     resp.say(os.getenv('MESSAGE'))
#
#     return str(resp)

# DASHBOARD MENU ROUTES
# HISTORY ROUTE
@app.route('/history', methods=['GET'])
@is_logged_in
def history():

    # CREATE CURSOR
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT * FROM contacts
        """)

    # COMMIT TO DB
    mysql.connection.commit()

    # FETCH DATA
    data = cur.fetchall()

    # CLOSE CONNECTION
    cur.close()
    return render_template('history.html', data=data)

# EDIT PROFILE ROUTE
@app.route('/delete')
@is_logged_in
def delete():
    return render_template('delete.html')

if __name__ == '__main__':
    # GET SECRET_KEY
    app.secret_key = os.environ.get('SECRET_KEY')
    app.run(debug=True)
