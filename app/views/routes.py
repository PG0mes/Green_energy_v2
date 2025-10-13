import os
from datetime import datetime
from flask import (Blueprint, render_template, request, redirect, url_for, 
                   flash, jsonify, g, session)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

# Models e Repositories
from app.models.fonte_energia import FonteEnergia, FonteEnergiaRepository
from app.models.user import UserRepository
from app.models.transacao import TransacaoRepository

# Controllers e Services
from app.data_processors.data_importer import GrowattDataImporter
from app.controllers.dashboard_controller import DashboardController
from app.controllers.performance_monitor import PerformanceMonitor
from app.controllers.generation_forecaster import GenerationForecaster
from app.services.calculos import calcular_excedente
from app.services.supabase_client import supabase
from app.services.blockchain_service import mint_gec_tokens, get_gec_balance

main = Blueprint('main', __name__)

# =============================================================================
# ROTAS DE AUTENTICAÇÃO E USUÁRIO
# =============================================================================

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_repo = UserRepository()
        user = user_repo.authenticate_user(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next') or url_for('main.index')
            flash(f'Bem-vindo, {user.name}!', 'success')
            return redirect(next_page)
        else:
            flash('Nome de usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('wallet_address', None)
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    # Sua lógica de registro aqui...
    return render_template('register.html')

# =============================================================================
# FUNÇÕES DE APOIO
# =============================================================================

@main.before_request
def obter_fontes():
    g.fontes = []
    if current_user.is_authenticated:
        fontes_db = FonteEnergiaRepository.listar_todas()
        g.fontes = [FonteEnergia.from_dict(f) for f in fontes_db]

# =============================================================================
# ROTAS DA APLICAÇÃO (FUNCIONALIDADES ORIGINAIS RESTAURADAS)
# =============================================================================

@main.route('/')
@login_required
def index():
    fontes = FonteEnergiaRepository.listar_todas()
    return render_template('index.html', fontes=fontes)

@main.route('/home')
@login_required
def home():
    return redirect(url_for('main.fontes_cadastradas'))

@main.route('/fontes')
@login_required
def fontes_cadastradas():
    fontes = FonteEnergiaRepository.listar_todas()
    return render_template('fontes_cadastradas.html', fontes=fontes)

@main.route('/fonte/nova', methods=['GET', 'POST'])
@login_required
def nova_fonte():
    if request.method == 'POST':
        try:
            data = {'nome': request.form['nome'], 'localizacao': request.form['localizacao'], 'capacidade': float(request.form['capacidade']), 'marca': request.form['marca'], 'modelo': request.form['modelo'], 'data_instalacao': request.form['data_instalacao']}
            result = supabase.table('fontes_energia').insert(data).execute()
            if not (result.data and len(result.data) > 0): raise Exception('Erro ao cadastrar fonte no Supabase.')
            fonte_id = result.data[0]['id']
            flash('Fonte de energia cadastrada com sucesso!', 'success')
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
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        flash('Fonte não encontrada!', 'danger')
        return redirect(url_for('main.index'))
    return render_template('detalhe_fonte.html', fonte=fonte)

@main.route('/fonte/<int:fonte_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_fonte(fonte_id):
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        try:
            fonte.nome, fonte.localizacao, fonte.capacidade, fonte.marca, fonte.modelo, fonte.data_instalacao = request.form['nome'], request.form['localizacao'], request.form['capacidade'], request.form['marca'], request.form['modelo'], request.form['data_instalacao']
            FonteEnergiaRepository.salvar(fonte)
            flash('Fonte atualizada com sucesso!', 'success')
            return redirect(url_for('main.detalhe_fonte', fonte_id=fonte.id))
        except Exception as e:
            flash(f'Erro ao atualizar fonte: {str(e)}', 'danger')
    return render_template('editar_fonte.html', fonte=fonte)

@main.route('/fonte/<int:fonte_id>/importar', methods=['GET', 'POST'])
@login_required
def importar_dados(fonte_id):
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        return redirect(url_for('main.index'))
    # Sua lógica de importação aqui...
    return render_template('importar_dados.html', fonte=fonte)

@main.route('/dashboard/<int:fonte_id>')
@login_required
def dashboard(fonte_id):
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        flash('Fonte não encontrada!', 'danger')
        return redirect(url_for('main.index'))
    
    metricas = DashboardController.calcular_metricas_gerais(fonte_id)
    alertas_ativos = PerformanceMonitor.obter_alertas(fonte_id, apenas_ativos=True)
    analise_performance = PerformanceMonitor.analisar_performance(fonte_id)
    detalhes_calculo = DashboardController.obter_detalhes_calculo_excedente(fonte_id)
    
    return render_template('dashboard.html', 
                          fonte=fonte, titulo=f"Dashboard - {fonte.nome}",
                          metricas=metricas, alertas_ativos=alertas_ativos,
                          analise_performance=analise_performance,
                          detalhes_calculo=detalhes_calculo)

@main.route('/fonte/<int:fonte_id>/monitoramento')
@login_required
def monitoramento(fonte_id):
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        return redirect(url_for('main.home'))
    analise = PerformanceMonitor.analisar_performance(fonte_id)
    alertas = PerformanceMonitor.obter_alertas(fonte_id)
    return render_template('monitoramento.html', 
                           fonte=fonte, analise=analise, alertas=alertas,
                           titulo=f"Monitoramento - {fonte.nome}")

@main.route('/fonte/<int:fonte_id>/previsao')
@login_required
def previsao_geracao(fonte_id):
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if not fonte:
        return redirect(url_for('main.home'))
    if not fonte.localizacao:
        flash('A fonte precisa ter uma localização definida para gerar previsões.', 'warning')
        return redirect(url_for('main.dashboard', fonte_id=fonte_id))
    return render_template('previsao.html', 
                           fonte=fonte, 
                           titulo=f"Previsão de Geração - {fonte.nome}")

# =============================================================================
# ROTAS DA FUNCIONALIDADE BLOCKCHAIN
# =============================================================================

@main.route('/creditos-solares')
@login_required
def creditos_solares():
    wallet_address = session.get('wallet_address')
    gec_balance = 0.0
    excedente_a_reivindicar = 0.0
    historico_transacoes = []

    if wallet_address:
        gec_balance = get_gec_balance(wallet_address)
        excedente_a_reivindicar = DashboardController.calcular_excedente_reivindicavel(wallet_address)
        historico_transacoes = TransacaoRepository.buscar_por_wallet_address(wallet_address)
    
    return render_template('creditos.html',
                           titulo="Créditos Solares", 
                           transacoes=historico_transacoes,
                           wallet_address=wallet_address,
                           gec_balance=gec_balance,
                           excedente_a_reivindicar=excedente_a_reivindicar)

# =============================================================================
# ROTAS DE API
# =============================================================================

@main.route('/api/connect-wallet', methods=['POST'])
@login_required
def connect_wallet():
    data = request.json
    wallet_address = data.get('address')
    if not wallet_address:
        return jsonify({"success": False, "message": "Endereço não fornecido."}), 400
    session['wallet_address'] = wallet_address
    print(f"Carteira {wallet_address} conectada para o usuário {current_user.name}.")
    return jsonify({"success": True, "message": "Carteira conectada!"})

@main.route('/api/reivindicar-creditos', methods=['POST'])
@login_required
def reivindicar_creditos():
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        return jsonify({"success": False, "message": "Nenhuma carteira conectada."}), 403
    
    quantidade_a_mintar = DashboardController.calcular_excedente_reivindicavel(wallet_address)
    quantidade_a_mintar = round(quantidade_a_mintar, 4)

    if quantidade_a_mintar <= 0:
        return jsonify({"success": False, "message": "Nenhum crédito disponível."})

    resultado_mint = mint_gec_tokens(wallet_address, quantidade_a_mintar)
    
    if resultado_mint and resultado_mint.get("success"):
        TransacaoRepository.salvar_transacao(
            wallet_address=wallet_address, kwh_excedente=quantidade_a_mintar,
            gec_recebido=quantidade_a_mintar, tx_hash=resultado_mint.get("tx_hash")
        )
    return jsonify(resultado_mint)

@main.route('/api/fonte/<int:fonte_id>/producao-diaria')
@login_required
def api_producao_diaria(fonte_id):
    dados = DashboardController.get_dados_producao_diaria(fonte_id)
    return jsonify(dados)

@main.route('/api/fonte/<int:fonte_id>/producao-horaria')
@login_required
def api_producao_horaria(fonte_id):
    dia = request.args.get('dia')
    dados = DashboardController.get_dados_producao_horaria(fonte_id, dia)
    return jsonify(dados)

@main.route('/api/fonte/<int:fonte_id>/previsao-geracao')
@login_required
def api_previsao_geracao(fonte_id):
    # (Sua lógica de API de previsão aqui)
    previsoes = GenerationForecaster.predict_generation(fonte_id)
    if not previsoes:
        return jsonify({'success': False, 'message': 'Não foi possível gerar previsões.'})
    return jsonify({'success': True, 'previsoes': previsoes})

@main.route('/fonte/<int:fonte_id>/alerta/<int:alerta_id>/resolver', methods=['POST'])
@login_required
def resolver_alerta(fonte_id, alerta_id):
    """Marca um alerta como resolvido após intervenção do usuário."""
    fonte = FonteEnergiaRepository.buscar_por_id(fonte_id)
    if fonte is None:
        flash('Fonte de energia não encontrada!', 'danger')
        return redirect(url_for('main.home'))
    
    if PerformanceMonitor.marcar_alerta_resolvido(fonte_id, alerta_id):
        flash('Manutenção registrada com sucesso! O monitoramento será retomado.', 'success')
    else:
        flash('Não foi possível registrar a manutenção.', 'danger')
    
    return redirect(url_for('main.monitoramento', fonte_id=fonte_id))