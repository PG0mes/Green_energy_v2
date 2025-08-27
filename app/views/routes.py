from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g
from flask_login import login_user, logout_user, login_required, current_user
from app.models.fonte_energia import FonteEnergia, FonteEnergiaRepository
from app.models.user import UserRepository
from app.data_processors.data_importer import GrowattDataImporter
from app.controllers.dashboard_controller import DashboardController
from app.controllers.performance_monitor import PerformanceMonitor
from app.controllers.generation_forecaster import GenerationForecaster
from app.services.calculos import calcular_excedente  # Corrigir importação
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from app.services.supabase_client import supabase

main = Blueprint('main', __name__)

# Rotas de autenticação (não precisam de login)
@main.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'warning')
            return render_template('login.html')
        
        user_repo = UserRepository()
        user = user_repo.authenticate_user(username, password)
        
        if user:
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            flash(f'Bem-vindo, {user.name}!', 'success')
            return redirect(next_page)
        else:
            flash('Nome de usuário ou senha incorretos.', 'danger')
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro de usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        
        # Validações básicas
        if not all([username, email, password, confirm_password, name]):
            flash('Por favor, preencha todos os campos.', 'warning')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('register.html')
        
        # Criar usuário
        user_repo = UserRepository()
        user, error = user_repo.create_user(username, email, password, name)
        
        if user:
            flash('Usuário criado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash(f'Erro ao criar usuário: {error}', 'danger')
    
    return render_template('register.html')

@main.before_request
def obter_fontes():
    """Obtém todas as fontes para uso em todas as páginas (navbar)"""
    if request.endpoint and request.endpoint.startswith('main.'):
        fontes = FonteEnergiaRepository.listar_todas()
        fontes_objetos = []
        for fonte_dict in fontes:
            fonte = FonteEnergia.from_dict(fonte_dict)
            fontes_objetos.append(fonte)
        request.fontes = fontes_objetos

# Rotas principais do sistema (precisam de login)
@main.route('/')
@login_required
def index():
    """Página inicial - Lista todas as fontes"""
    fontes = FonteEnergiaRepository.listar_todas()
    return render_template('index.html', fontes=fontes)

@main.route('/fonte/nova', methods=['GET', 'POST'])
@login_required
def nova_fonte():
    """Cadastro de uma nova fonte de energia"""
    if request.method == 'POST':
        try:
            data = {
                'nome': request.form['nome'],
                'localizacao': request.form['localizacao'],
                'capacidade': float(request.form['capacidade']),
                'marca': request.form['marca'],
                'modelo': request.form['modelo'],
                'data_instalacao': request.form['data_instalacao']
            }
            # Inserir no Supabase
            result = supabase.table('fontes_energia').insert(data).execute()
            if result.data and len(result.data) > 0:
                fonte_id = result.data[0]['id']
            else:
                raise Exception('Erro ao cadastrar fonte no Supabase.')
            flash('Fonte de energia cadastrada com sucesso!', 'success')
            # Gerar dados simulados para desenvolvimento
            if request.form.get('gerar_dados_simulados') == 'on':
                GrowattDataImporter.gerar_dados_simulados(fonte_id)
                flash('Dados simulados gerados com sucesso!', 'success')
            return redirect(url_for('main.dashboard', fonte_id=fonte_id))
        except Exception as e:
            flash(f'Erro ao cadastrar fonte: {str(e)}', 'danger')
    return render_template('cadastro_fonte.html')

@main.route('/fonte/<int:fonte_id>')
@login_required
def detalhe_fonte(fonte_id):
    """Exibe detalhes de uma fonte específica"""
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        flash('Fonte não encontrada!', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('detalhe_fonte.html', fonte=fonte)

@main.route('/fonte/<int:fonte_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_fonte(fonte_id):
    """Edição de uma fonte existente"""
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        flash('Fonte não encontrada!', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            fonte.nome = request.form['nome']
            fonte.localizacao = request.form['localizacao']
            fonte.capacidade = request.form['capacidade']
            fonte.marca = request.form['marca']
            fonte.modelo = request.form['modelo']
            fonte.data_instalacao = request.form['data_instalacao']
            
            FonteEnergiaRepository.salvar(fonte)
            flash('Fonte atualizada com sucesso!', 'success')
            return redirect(url_for('main.detalhe_fonte', fonte_id=fonte.id))
        except Exception as e:
            flash(f'Erro ao atualizar fonte: {str(e)}', 'danger')
    
    return render_template('editar_fonte.html', fonte=fonte)

@main.route('/fonte/<int:fonte_id>/importar', methods=['GET', 'POST'])
@login_required
def importar_dados(fonte_id):
    """Importação de dados para uma fonte"""
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        flash('Fonte não encontrada!', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        if 'arquivo_csv' in request.files:
            arquivo = request.files['arquivo_csv']
            if arquivo.filename:
                # Salvar arquivo temporariamente
                filename = secure_filename(arquivo.filename)
                filepath = os.path.join('data', 'temp', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                arquivo.save(filepath)
                
                # Importar dados
                resultado = GrowattDataImporter.importar_csv(filepath, fonte_id)
                
                # Remover arquivo temporário
                os.unlink(filepath)
                
                if resultado['sucesso']:
                    flash(f"Dados importados com sucesso! {resultado['registros']} registros processados.", 'success')
                else:
                    flash(f"Erro na importação: {resultado['mensagem']}", 'danger')
                
                return redirect(url_for('main.dashboard', fonte_id=fonte_id))
            else:
                flash('Nenhum arquivo selecionado!', 'warning')
        elif request.form.get('gerar_simulados') == 'on':
            # Gerar dados simulados
            dias = int(request.form.get('dias_simulados', 30))
            resultado = GrowattDataImporter.gerar_dados_simulados(fonte_id, dias)
            
            if resultado['sucesso']:
                flash(f"Dados simulados gerados com sucesso! {resultado['registros']} registros criados.", 'success')
            else:
                flash(f"Erro na geração de dados: {resultado['mensagem']}", 'danger')
            
            return redirect(url_for('main.dashboard', fonte_id=fonte_id))
    
    return render_template('importar_dados.html', fonte=fonte)

@main.route('/dashboard/<int:fonte_id>/excedente')
@login_required
def excedente(fonte_id):
    """Subseção de Excedente - Exibe o cálculo do excedente gerado"""
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        flash('Fonte não encontrada!', 'danger')
        return redirect(url_for('main.index'))
    
    # Calcular o excedente gerado
    excedente_gerado = calcular_excedente(fonte_id)
    
    # Obter detalhes do cálculo (exemplo: geração total - consumo total)
    detalhes_calculo = DashboardController.obter_detalhes_calculo_excedente(fonte_id)
    
    return render_template('excedente.html', 
                           fonte=fonte, 
                           titulo=f"Excedente - {fonte.nome}",
                           excedente_gerado=excedente_gerado,
                           detalhes_calculo=detalhes_calculo)

@main.route('/dashboard/<int:fonte_id>')
@login_required
def dashboard(fonte_id):
    """Dashboard para visualização dos dados de geração"""
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        flash('Fonte não encontrada!', 'danger')
        return redirect(url_for('main.index'))
    
    # Verificar se existem dados reais
    dados_reais = False
    path_simulado = f'data/simulated/fonte_{fonte_id}_simulado.csv'
    processed_dir = 'data/processed'
    
    if os.path.exists(path_simulado):
        dados_reais = True
    
    if os.path.exists(processed_dir):
        processed_files = [f for f in os.listdir(processed_dir) 
                          if f.startswith(f'fonte_{fonte_id}_') and f.endswith('.csv')]
        if processed_files:
            dados_reais = True
    
    # Métricas gerais
    metricas = DashboardController.calcular_metricas_gerais(fonte_id)
    
    # Verificar se há alertas ativos para esta fonte
    alertas_ativos = PerformanceMonitor.obter_alertas(fonte_id, apenas_ativos=True)
    
    # Realizar análise de performance
    analise_performance = PerformanceMonitor.analisar_performance(fonte_id)
    
    if not dados_reais:
        flash('Exibindo dados simulados para demonstração. Para visualizar dados reais, importe ou gere dados simulados.', 'info')
    
    excedente_gerado = calcular_excedente(fonte_id)
    detalhes_calculo = DashboardController.obter_detalhes_calculo_excedente(fonte_id)
    return render_template('dashboard.html', 
                          fonte=fonte, 
                          titulo=f"Dashboard - {fonte.nome}",
                          alertas_ativos=alertas_ativos,
                          analise_performance=analise_performance,
                          metricas=metricas,
                          excedente_gerado=excedente_gerado,
                          detalhes_calculo=detalhes_calculo)

@main.route('/api/fonte/<int:fonte_id>/producao-diaria')
@login_required
def api_producao_diaria(fonte_id):
    """API para obter dados de produção diária"""
    dados = DashboardController.get_dados_producao_diaria(fonte_id)
    return jsonify(dados)

@main.route('/api/fonte/<int:fonte_id>/producao-horaria')
@login_required
def api_producao_horaria(fonte_id):
    """API para obter dados de produção horária"""
    dia = request.args.get('dia')
    dados = DashboardController.get_dados_producao_horaria(fonte_id, dia)
    return jsonify(dados)

@main.route('/home')
@login_required
def home():
    """Página inicial do sistema"""
    fontes = FonteEnergiaRepository.listar_todas()
    return render_template('fontes_cadastradas.html', fontes=fontes)

@main.route('/fontes')
@login_required
def fontes_cadastradas():
    """Página de fontes cadastradas"""
    fontes = FonteEnergiaRepository.listar_todas()
    return render_template('fontes_cadastradas.html', fontes=fontes)

@main.route('/fonte/<int:fonte_id>/monitoramento')
@login_required
def monitoramento(fonte_id):
    """Exibe o monitoramento de performance da fonte de energia"""
    # Buscar a fonte pelo ID
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if fonte is None:
        flash('Fonte de energia não encontrada!', 'danger')
        return redirect(url_for('main.home'))
    
    # Realizar análise de performance
    analise = PerformanceMonitor.analisar_performance(fonte_id)
    
    # Obter histórico de alertas
    alertas = PerformanceMonitor.obter_alertas(fonte_id)
    
    # Renderizar a página de monitoramento
    return render_template('monitoramento.html', 
                           fonte=fonte, 
                           analise=analise, 
                           alertas=alertas,
                           titulo=f"Monitoramento - {fonte.nome}")

@main.route('/fonte/<int:fonte_id>/alerta/<int:alerta_id>/resolver', methods=['POST'])
@login_required
def resolver_alerta(fonte_id, alerta_id):
    """Marca um alerta como resolvido após intervenção do usuário"""
    # Verificar a fonte
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if fonte is None:
        flash('Fonte de energia não encontrada!', 'danger')
        return redirect(url_for('main.home'))
    
    # Marcar o alerta como resolvido
    if PerformanceMonitor.marcar_alerta_resolvido(fonte_id, alerta_id):
        flash('Manutenção registrada com sucesso! O monitoramento será retomado.', 'success')
    else:
        flash('Não foi possível registrar a manutenção.', 'danger')
    
    # Redirecionar de volta para a página de monitoramento
    return redirect(url_for('main.monitoramento', fonte_id=fonte_id))

@main.route('/api/fonte/<int:fonte_id>/performance')
@login_required
def api_performance(fonte_id):
    """API para obter dados de performance para visualização em gráficos"""
    # Realizar análise de performance
    analise = PerformanceMonitor.analisar_performance(fonte_id)
    
    # Retornar dados no formato JSON para uso em gráficos
    return jsonify(analise)

@main.route('/api/fonte/<int:fonte_id>/previsao-geracao')
@login_required
def api_previsao_geracao(fonte_id):
    """API para obter previsão de geração baseada em dados meteorológicos"""
    # Verificar se é para forçar atualização
    force_refresh = request.args.get('refresh', '').lower() == 'true'
    
    # Se for para forçar atualização, limpar previsão salva
    if force_refresh:
        GenerationForecaster.clear_forecast(fonte_id)
        
    # Verificar se já existe uma previsão salva
    forecast_dados = GenerationForecaster.get_saved_forecast(fonte_id)
    
    # Flag para indicar se os dados são simulados
    is_simulated = False
    
    # Se não existir ou estiver desatualizada, gerar nova previsão
    if not forecast_dados:
        # Gerar nova previsão
        previsoes = GenerationForecaster.predict_generation(fonte_id)
        if not previsoes:
            return jsonify({
                'success': False,
                'message': 'Não foi possível gerar previsões de geração',
                'previsoes': []
            })
            
        # Verificar se os dados são simulados (verificando a origem)
        if any('simulado' in str(previsao.get('source', '')).lower() for previsao in previsoes):
            is_simulated = True
        
        # Formatar a resposta
        forecast_dados = {
            'fonte_id': fonte_id,
            'data_previsao': datetime.now().isoformat(),
            'previsoes': previsoes,
            'is_simulated': is_simulated
        }
    else:
        # Verificar se os dados salvos são simulados
        if forecast_dados.get('is_simulated', False):
            is_simulated = True
    
    return jsonify({
        'success': True,
        'message': 'Previsão de geração obtida com sucesso',
        'previsoes': forecast_dados['previsoes'],
        'is_simulated': is_simulated
    })

@main.route('/fonte/<int:fonte_id>/previsao')
@login_required
def previsao_geracao(fonte_id):
    """Exibe a página de previsão de geração para uma fonte"""
    # Buscar a fonte pelo ID
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if fonte is None:
        flash('Fonte de energia não encontrada!', 'danger')
        return redirect(url_for('main.home'))
    
    # Verificar se a fonte tem localização definida
    if not fonte.localizacao:
        flash('A fonte precisa ter uma localização definida para gerar previsões meteorológicas.', 'warning')
        return redirect(url_for('main.dashboard', fonte_id=fonte_id))
    
    # Renderizar a página de previsão
    return render_template('previsao.html', 
                           fonte=fonte, 
                           titulo=f"Previsão de Geração - {fonte.nome}")