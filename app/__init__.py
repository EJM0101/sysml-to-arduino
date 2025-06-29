from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
bootstrap = Bootstrap()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models.db'
    app.config['SECRET_KEY'] = 'your-secret-key-123'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    bootstrap.init_app(app)
    
    from app.routes import main_routes
    app.register_blueprint(main_routes)
    
    return app

# Création de l'application pour Gunicorn
app = create_app()