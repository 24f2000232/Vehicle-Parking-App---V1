from flask import Flask
from db_config import db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.secret_key = 'supersecret'
db.init_app(app)

from models.models import *
from controllers.routes import *

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@test.com').first():
        admin = User(email='admin@test.com', password='admin123', name='Admin',
                     address='HQ', pincode=123456, role='admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
