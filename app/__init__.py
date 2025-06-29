from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect, generate_csrf  # Ajout de l'import manquant

db = SQLAlchemy()
bootstrap = Bootstrap()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models.db'
    app.config['SECRET_KEY'] = 'votre_cle_secrete_ici_renforcee'  # Clé plus complexe
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # Durée de validité du token

    # Import des modèles avant initialisation
    from app.models.sysml_models import Requirement, Block

    # Initialisation des extensions
    db.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)  # Activation CSRF

    # Création des tables
    with app.app_context():
        db.create_all()

    # Enregistrement des blueprints
    from app.routes import main_routes
    app.register_blueprint(main_routes)

    # Protection CSRF globale (version corrigée)
    @app.after_request
    def add_csrf_token(response):
        response.set_cookie('csrf_token', generate_csrf())
        return response

    return app

app = create_app()