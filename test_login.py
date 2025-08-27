#!/usr/bin/env python3
"""
Teste do sistema de login
"""

import requests
import json

def test_login_system():
    """Testa o sistema de login"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testando sistema de login...")
    print("=" * 50)
    
    # Teste 1: Acessar página de login
    print("1. Acessando página de login...")
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Página de login acessível")
        else:
            print(f"❌ Erro ao acessar login: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # Teste 2: Acessar página de registro
    print("\n2. Acessando página de registro...")
    try:
        response = requests.get(f"{base_url}/register")
        if response.status_code == 200:
            print("✅ Página de registro acessível")
        else:
            print(f"❌ Erro ao acessar registro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    # Teste 3: Tentar acessar página principal sem login (deve redirecionar)
    print("\n3. Testando acesso à página principal sem login...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False)
        if response.status_code == 302:  # Redirecionamento
            print("✅ Redirecionamento para login funcionando")
        else:
            print(f"❌ Redirecionamento não funcionou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar redirecionamento: {e}")
    
    # Teste 4: Tentar login com credenciais inválidas
    print("\n4. Testando login com credenciais inválidas...")
    try:
        data = {
            'username': 'usuario_inexistente',
            'password': 'senha_errada'
        }
        response = requests.post(f"{base_url}/login", data=data)
        if response.status_code == 200:
            print("✅ Login com credenciais inválidas retornou 200 (esperado)")
        else:
            print(f"❌ Login com credenciais inválidas retornou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar login: {e}")
    
    # Teste 5: Verificar se o arquivo users.json existe
    print("\n5. Verificando arquivo users.json...")
    try:
        with open('data/users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
            print(f"✅ Arquivo users.json encontrado com {len(users)} usuário(s)")
            for user in users:
                print(f"   - Usuário: {user['username']} ({user['name']})")
    except FileNotFoundError:
        print("❌ Arquivo users.json não encontrado")
    except Exception as e:
        print(f"❌ Erro ao ler users.json: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Para testar o login completo:")
    print("1. Execute: python main.py")
    print("2. Acesse: http://localhost:5000/login")
    print("3. Use as credenciais: admin / admin123")
    print("4. Verifique se aparece o ícone de perfil na navbar")
    print("5. Tente acessar outras páginas sem login para ver o redirecionamento")

if __name__ == "__main__":
    test_login_system()
