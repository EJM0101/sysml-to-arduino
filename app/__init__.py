from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
bootstrap = Bootstrap()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models.db'
    app.config['SECRET_KEY'] = 'votre_cle_secrete_reel'  # Changez ceci en production
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)  # Activation CSRF
    
    with app.app_context():
        db.create_all()
    
    from app.routes import main_routes
    app.register_blueprint(main_routes)
    
    return app

app = create_app()