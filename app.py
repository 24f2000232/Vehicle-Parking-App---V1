from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/create_user')
def create_user():
    return render_template('create_user.html')

@app.route('/editparkinglot')
def editparkinglot():
    return render_template('editParkingLot.html')

if __name__ == '__main__':
    app.run(debug = True)
