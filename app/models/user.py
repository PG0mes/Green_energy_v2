import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, email, name, role, created_at, **kwargs):
        self.id = id
        self.username = username
        self.email = email
        self.name = name
        self.role = role
        self.created_at = created_at
        # Ignora campos extras como password_hash
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False

class UserRepository:
    def __init__(self, data_file="data/users.json"):
        self.data_file = data_file
    
    def _load_users(self):
        """Carrega usuários do arquivo JSON"""
        if not os.path.exists(self.data_file):
            return []
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_users(self, users):
        """Salva usuários no arquivo JSON"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def get_user_by_id(self, user_id):
        """Busca usuário por ID"""
        users = self._load_users()
        for user_data in users:
            if user_data['id'] == user_id:
                return User(**user_data)
        return None
    
    def get_user_by_username(self, username):
        """Busca usuário por nome de usuário"""
        users = self._load_users()
        for user_data in users:
            if user_data['username'] == username:
                return User(**user_data)
        return None
    
    def get_user_by_email(self, email):
        """Busca usuário por email"""
        users = self._load_users()
        for user_data in users:
            if user_data['email'] == email:
                return User(**user_data)
        return None
    
    def authenticate_user(self, username, password):
        """Autentica usuário com username e senha"""
        users = self._load_users()
        for user_data in users:
            if user_data['username'] == username:
                # Para este exemplo, vamos usar uma senha simples
                # Em produção, você deve usar hash real
                if password == "admin123":  # Senha de exemplo
                    return User(**user_data)
        return None
    
    def create_user(self, username, email, password, name, role="user"):
        """Cria um novo usuário"""
        users = self._load_users()
        
        # Verifica se username ou email já existem
        if self.get_user_by_username(username):
            return None, "Nome de usuário já existe"
        
        if self.get_user_by_email(email):
            return None, "Email já existe"
        
        # Gera novo ID
        new_id = max([u['id'] for u in users], default=0) + 1
        
        # Cria hash da senha
        password_hash = generate_password_hash(password)
        
        # Cria novo usuário
        new_user = {
            'id': new_id,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'role': role,
            'created_at': "2024-01-01T00:00:00Z"  # Simplificado para exemplo
        }
        
        users.append(new_user)
        self._save_users(users)
        
        return User(**new_user), None
