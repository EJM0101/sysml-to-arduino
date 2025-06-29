from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models.db'
    app.config['SECRET_KEY'] = 'your-secret-key-123'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    Bootstrap(app)
    
    with app.app_context():
        db.create_all()
    
    from app.routes import main_routes
    app.register_blueprint(main_routes)
    
    return app