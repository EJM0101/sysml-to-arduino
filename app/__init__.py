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
    app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Import des modèles ICI avant db.init_app
    from app.models.sysml_models import Requirement, Block
    
    db.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()  # Crée toutes les tables

    from app.routes import main_routes
    app.register_blueprint(main_routes)

    return app

app = create_app()