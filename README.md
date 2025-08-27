  # GreenEnergy Management System
  
Um sistema de gerenciamento de energia solar desenvolvido com Flask, projetado para monitorar, analisar e prever a produção de fontes de energia limpa. A aplicação permite o cadastro e acompanhamento de placas solares, análise de performance, importação de dados e previsões de geração, ajudando usuários a otimizar o uso de sua energia.

Funcionalidades
Dashboard Interativo: Visualize a geração total de energia, potência de pico e média diária através de gráficos e métricas.

Cadastro e Gerenciamento de Fontes: Crie, edite e gerencie informações detalhadas de suas instalações de energia solar.

Previsão de Geração: Obtenha previsões de produção de energia solar com base em dados meteorológicos, utilizando a API OpenWeather.

Monitoramento de Performance: Analise o desempenho histórico das suas fontes de energia e receba alertas sobre anomalias.

Importação de Dados: Importe dados de produção de arquivos CSV (formato Growatt) para uma análise precisa.

Dados Simulados: Gere dados simulados para testes e demonstração do sistema, caso não tenha dados reais para importar.

Autenticação de Usuários: Acesso seguro com sistema de login para proteger as informações das suas fontes de energia.

Estrutura do Projeto
app/: Contém o código-fonte principal da aplicação.

controllers/: Lógica de negócios para o dashboard, monitoramento e previsão.

data_processors/: Scripts para importação e geração de dados (por exemplo, data_importer.py).

models/: Definições dos modelos de dados (fonte_energia.py).

services/: Serviços externos como a API de clima (weather_service.py).

templates/: Arquivos HTML para as interfaces do usuário.

static/: Arquivos estáticos como CSS, JavaScript e imagens.

data/: Armazenamento local de dados, como informações de fontes e previsões.

config/: Arquivos de configuração.

venv/: Ambiente virtual do Python.

# Como Executar o Projeto
#- Clone o repositório:
  git clone https://github.com/PGomes/Green_energy_v2.git
  cd Green_energy_v2

# - Crie e ative o ambiente virtual:
  python -m venv venv
  # No Windows
  venv\Scripts\activate
  # No macOS/Linux
  source venv/bin/activate

# - Instale as dependências:
  pip install -r requirements.txt

# - Configure as variáveis de ambiente:
  Crie um arquivo .env na raiz do projeto e adicione as variáveis necessárias, como a chave da API do OpenWeather.

  # Exemplo de conteúdo para o arquivo .env
  FLASK_APP=main.py
  FLASK_ENV=development
  SECRET_KEY='uma-chave-secreta-forte'
  WEATHER_API_KEY='sua-chave-api-do-openweather'

# - Execute a aplicação.
