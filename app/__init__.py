from flask import Flask
from flask_login import LoginManager
from config.config import config

def create_app(config_name='default'):
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configuração do Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import UserRepository
        user_repo = UserRepository()
        return user_repo.get_user_by_id(int(user_id))
    
    # Registro dos blueprints
    from app.views.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app