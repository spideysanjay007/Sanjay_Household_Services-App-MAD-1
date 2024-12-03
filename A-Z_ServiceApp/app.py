from flask import Flask, render_template
from models import db
app = Flask(__name__)

app.config['SECRET_KEY'] = "secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()

from routes import *

if __name__ == '__main__':
    db.create_all()
    app.run(debug= True)  