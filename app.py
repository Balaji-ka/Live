import joblib
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
#from gevent.pywsgi import WSGIServer
#import os
import pandas as pd

import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

import requests
import json

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
#API_KEY = "P9sLoqpS9-1CbZz_qeAMOsjFuLCIFBunc_aAEZy95xcQ"
#token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 #API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
#mltoken = token_response.json()["access_token"]

#header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/help')
def help():
    return render_template("help.html")





@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
            else:
                print("password is incorrect")
                return redirect(url_for('login'))

        return render_template("login.html", form=form)
    return render_template("login.html", form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")
    return render_template('signup.html', form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/disindex")

def disindex():
    return render_template("disindex.html")





@app.route("/liver")
@login_required
def liver():
    return render_template("liver.html")



def ValuePred(to_predict_list, size):
    to_predict = np.array(to_predict_list).reshape(1,size)
    if(size==7):
        loaded_model = joblib.load('liver_model.pkl')
        result = loaded_model.predict(to_predict)

    return result[0]


@app.route('/predictliver', methods=["POST"])
def predictliver():
    if request.method == "POST":
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        to_predict_list = list(map(float, to_predict_list))
        if len(to_predict_list) == 7:
            result = ValuePred(to_predict_list, 7)

    if int(result) == 1:
        prediction = "Patient has a high risk of Liver Disease, please consult your doctor immediately"
    else:
        prediction = "Patient has a low risk of Kidney Disease"
    return render_template("liver_result.html", prediction_text=prediction,li=to_predict_list)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#port= os.getenv('VCAP_APP_PORT','8080')

if __name__ == "__main__":
    app.run(debug=True)
    #app.secret_key = os.urandom(12)
    #app.run(debug=True,host='0.0.0.0',port=port)


