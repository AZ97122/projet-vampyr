# Point d'entrée principal

from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from auth import auth_bp
from routes_vm import vm_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vampire.db'
app.config['JWT_SECRET_KEY'] = 'vampire-super-secret-key'

db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(vm_bp, url_prefix='/api')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
