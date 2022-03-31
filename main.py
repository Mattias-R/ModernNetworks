from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import boto3
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'db1.czyppxeqjiq3.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'adminadmin'
app.config['MYSQL_DB'] = 'pythonlogin'

#s3 credentials
s3 = boto3.client('s3',
                  aws_access_key_id="ASIA32QL3DO7GI6BXRRM",
                  aws_secret_access_key="gtPNKvNyGB7BwP0Er7jfB7FLlD9ZgidNj0PV488y",
                  aws_session_token="FwoGZXIvYXdzEHYaDKUF6jtCF0EnNXwDriLXASw6g8/AeXX8FUxgbiRDHmMLJEPa6xY0cev8FFpGYf/M9EPScuIcNiHG8TiicbCAV0tdGQKq6GoM2gQARTAGOQPW+9yuXYncFCjj7YEJXsxqWbdQwEanQCI1XXf4XZfWF3oaPm4iOWyPGeONg6fFKH7XKcyxSuVy79k36Rv3FD1c5sm8bW904nbYrVpq5aDLDsWPcel84vwpeJqBkdCrJ4c52fVopdnKH/j0YkEhLt9l9hRXG0ASIKg5mO4CCVqCffB1mZD9mGR8Tm07NLoFOjH66mIZNraLKJekkZIGMi1wmYiexaJJn6wWVjFHJQpn3cXLQ/UQoZnlKI03+lIVSyxusEl1nOB4oyhzpoM="
                  )
BUCKET_NAME = 'kfcmaibach'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        img = request.files['file']
        if img:
            filename = secure_filename(img.filename)
            img.save(filename)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
            account = cursor.fetchone()
            print(account['username'])
            s3.upload_file(
                Bucket=BUCKET_NAME,
                Filename=filename,
                Key= str(session['id']) + '/' + filename
            )
            msg = "Upload Done ! "

    return render_template('profile.html', account=account)


if __name__ == "__main__":
    app.run(debug=True)


#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=80)
