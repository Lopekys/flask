import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from validate_email import validate_email
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'  
app.config['SESSION_FILE_DIR'] = 'ses'
app.permanent_session_lifetime = timedelta(days=1)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
Session(app)
CORS(app)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

server_smtp = os.environ.get('SERVER_SMTP')
smtp_login = os.environ.get('SMTP_LOGIN')
smtp_password = os.environ.get('SMTP_PASSWORD')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tepelhone = db.Column(db.String(120), unique=True, nullable=True)

    name = db.Column(db.String(120), nullable=True)
    midlname = db.Column(db.String(120), nullable=True)
    surname = db.Column(db.String(120), nullable=True)

    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


@app.route("/")
def index():
    return render_template('redirectToindex.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['ctl00$Main$Email']
        tepelhone = request.form['ctl00$Main$Mobile']
        name = request.form['ctl00$Main$FirstName']
        midlname = request.form['ctl00$Main$MiddleName']
        surname = request.form['ctl00$Main$Surname']
        is_valid = validate_email(email)
        if not is_valid:
            return "Invalid email address"

        # генерируем логин и пароль
        username = secrets.token_hex(4)
        password = secrets.token_hex(4)

        # сохраняем данные в базе данных
        user = User(email=email, tepelhone=tepelhone, username=username, password=password, name=name,
                    midlname=midlname, surname=surname)
        db.session.add(user)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['ctl00$Main$Login1$Username']
        password = request.form['ctl00$Main$Login1$Password']
        # проверяем данные в базе данных
        user = User.query.filter_by(username=username, password=password).first()
        if user is not None:
            session['user_id'] = user.id  
            session.permanent = True 
            return render_template('redirectToStep3.html')
        else:
            return render_template('ErrorLogin.html')


@app.route('/AAAAB3NzaC1yc2EAAAADD')
def users():
    # Показать пользователей
    all_users = User.query.all()
    return render_template('users.html', users=all_users)


@app.route('/delete_data', methods=['POST'])
def delete_data():
    # выполнение запроса на удаление данных из таблицы
    db.session.query(User).delete()
    db.session.commit()
    return users()


@app.route('/static/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)
    

@app.route('/tostep4', methods=['GET', 'POST'])
def step4():
    user_id = session.get('user_id')
    if user_id is None:
        return render_template('redirectToLogin.html')
    return f"'Your id '{session['user_id']}"
    
if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0')
