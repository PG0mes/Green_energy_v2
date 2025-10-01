import os
from flask import Flask
from flask_login import LoginManager
from config.config import config
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env na raiz do projeto
load_dotenv()

def create_app(config_name='default'):
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # --- GARANTIA DE SECRET_KEY ---
    # Define a chave secreta a partir do .env, com um valor padrão de segurança.
    # Isso garante que a sessão (e o Flask-Login) funcione corretamente.
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'uma-chave-secreta-de-fallback-muito-segura')
    
    # Vamos imprimir para ter 100% de certeza do que está sendo usado.
    print(f"DEBUG: SECRET_KEY em uso: {app.config['SECRET_KEY']}")
    # -----------------------------
    
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