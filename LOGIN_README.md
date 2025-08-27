# Sistema de Login - Green Energy

## 📋 Visão Geral

Este sistema de login foi implementado usando Flask-Login para fornecer autenticação de usuários na aplicação Green Energy. **O login é agora obrigatório para acessar qualquer funcionalidade do sistema.**

## 🚀 Funcionalidades

### ✅ Implementado
- **Login de usuário** com validação de credenciais
- **Registro de novos usuários** com validações
- **Logout** seguro
- **Proteção de rotas** com `@login_required` em TODAS as rotas principais
- **Interface responsiva** para login e registro
- **Navbar superior** com ícone de perfil do usuário
- **Sistema de sessões** persistente
- **Redirecionamento automático** para login quando não autenticado

### 🔐 Autenticação
- Usuário padrão: `admin` / `admin123`
- Hash de senhas com Werkzeug
- Validação de formulários
- Mensagens de erro e sucesso
- **Login obrigatório** para todo o sistema

## 📁 Arquivos Criados/Modificados

### Novos Arquivos
- `data/users.json` - Armazena dados dos usuários
- `app/models/user.py` - Modelo de usuário e repositório
- `app/templates/login.html` - Template de login (sem credenciais visíveis)
- `app/templates/register.html` - Template de registro
- `test_login.py` - Script de teste do sistema
- `LOGIN_README.md` - Esta documentação

### Arquivos Modificados
- `app/__init__.py` - Configuração do Flask-Login com redirecionamento
- `app/views/routes.py` - Todas as rotas principais agora requerem login
- `app/templates/base.html` - Navbar com perfil e mensagem de login obrigatório
- `requirements.txt` - Dependência Flask-Login

## 🛠️ Instalação e Configuração

### 1. Instalar Dependências
```bash
pip install Flask-Login
```

### 2. Verificar Configuração
O arquivo `config/config.py` já possui uma chave secreta configurada.

### 3. Executar Aplicação
```bash
python main.py
```

## 🧪 Testando o Sistema

### 1. Acessar Login
- URL: `http://localhost:5000/login`
- Credenciais: `admin` / `admin123`

### 2. Verificar Funcionalidades
- ✅ Login com credenciais corretas
- ✅ Redirecionamento após login
- ✅ Ícone de perfil na navbar
- ✅ Dropdown com informações do usuário
- ✅ Logout funcional
- ✅ **Redirecionamento automático para login quando não autenticado**

### 3. Executar Testes
```bash
python test_login.py
```

## 🔒 Segurança

### Implementado
- Hash de senhas com salt
- Proteção CSRF (Flask-WTF)
- Sessões seguras
- Validação de formulários
- **Proteção de todas as rotas principais**
- **Redirecionamento automático para login**

### Recomendações para Produção
- Usar variáveis de ambiente para chaves secretas
- Implementar rate limiting
- Adicionar autenticação de dois fatores
- Logs de auditoria de login

## 🎨 Interface do Usuário

### Navbar Superior
- **Usuário não autenticado**: Links "Entrar" e "Cadastrar"
- **Usuário autenticado**: Dropdown com perfil, configurações e logout

### Páginas de Autenticação
- **Login**: Formulário simples com validação (sem credenciais visíveis)
- **Registro**: Formulário completo com validações
- **Design responsivo** com Bootstrap 5

### Mensagens de Sistema
- **Alerta de login obrigatório** quando usuário não autenticado
- **Botão direto para login** nas mensagens de alerta

## 🔧 Personalização

### Adicionar Novos Usuários
1. Editar `data/users.json`
2. Ou usar a interface de registro

### Modificar Validações
- Editar `app/models/user.py`
- Ajustar regras de senha e usuário

### Alterar Design
- Modificar templates HTML
- Ajustar CSS em `base.html`

## 🐛 Solução de Problemas

### Erro: "No module named 'flask_login'"
```bash
pip install Flask-Login
```

### Erro: "SECRET_KEY not set"
Verificar se `config/config.py` está configurado corretamente.

### Usuário não consegue fazer login
1. Verificar se o arquivo `users.json` existe
2. Confirmar credenciais corretas
3. Verificar logs da aplicação

### Erro: "TypeError: User.__init__() got an unexpected keyword argument 'password_hash'"
- ✅ **RESOLVIDO**: O modelo User agora aceita campos extras com `**kwargs`

## 📚 Recursos Adicionais

### Documentação Flask-Login
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)

### Melhorias Futuras
- Recuperação de senha
- Verificação de email
- Perfis de usuário personalizáveis
- Controle de acesso baseado em roles

## 🤝 Contribuição

Para contribuir com melhorias no sistema de login:
1. Teste as funcionalidades existentes
2. Documente as mudanças propostas
3. Mantenha a compatibilidade com o sistema atual
4. Siga os padrões de código estabelecidos

---

**Desenvolvido para o projeto Green Energy - TCC Sistemas de Informação**
