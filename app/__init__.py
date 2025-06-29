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
    
    # Initialisation des extensions
    db.init_app(app)
    bootstrap.init_app(app)
    
    # Import et enregistrement des blueprints
    from app.routes import main_routes
    app.register_blueprint(main_routes)
    
    # Création des tables
    with app.app_context():
        db.create_all()
    
    return app

# Instance de l'application pour Gunicorn
app = create_app()