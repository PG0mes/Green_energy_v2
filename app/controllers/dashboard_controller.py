import os
import json
from datetime import datetime, timedelta

# Importações condicionais
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    class MockPandas:
        def __getattr__(self, name): return None
    pd = MockPandas()

# --- IMPORTAÇÃO QUE FALTAVA ---
from app.models.transacao import TransacaoRepository


class DashboardController:
    """Controlador para processamento de dados do dashboard"""
    
    @staticmethod
    def get_dados_fonte(fonte_id):
        """Obtém todos os dados disponíveis para uma fonte específica"""
        # (O conteúdo deste método permanece o mesmo)
        if not PANDAS_AVAILABLE:
            return None
        path_simulado = f'data/simulated/fonte_{fonte_id}_simulado.csv'
        processed_files = []
        processed_dir = 'data/processed'
        if os.path.exists(processed_dir):
            processed_files = [f for f in os.listdir(processed_dir) 
                              if f.startswith(f'fonte_{fonte_id}_') and f.endswith('.csv')]
        dfs = []
        if os.path.exists(path_simulado):
            df_simulado = pd.read_csv(path_simulado)
            df_simulado['data_hora'] = pd.to_datetime(df_simulado['data_hora'])
            dfs.append(df_simulado)
        for file in processed_files:
            file_path = os.path.join(processed_dir, file)
            df = pd.read_csv(file_path)
            df['data_hora'] = pd.to_datetime(df['data_hora'])
            dfs.append(df)
        if dfs:
            df_combined = pd.concat(dfs, ignore_index=True)
            df_combined = df_combined.drop_duplicates(subset=['data_hora'])
            df_combined = df_combined.sort_values('data_hora')
            return df_combined
        else:
            try:
                from app.data_processors.data_importer import GrowattDataImporter
                resultado = GrowattDataImporter.gerar_dados_simulados(fonte_id, dias=30)
                if resultado['sucesso'] and os.path.exists(resultado['caminho_arquivo']):
                    df_simulado = pd.read_csv(resultado['caminho_arquivo'])
                    df_simulado['data_hora'] = pd.to_datetime(df_simulado['data_hora'])
                    return df_simulado
            except Exception as e:
                print(f"Erro ao gerar dados simulados automaticamente: {str(e)}")
        return None
    
    @staticmethod
    def calcular_metricas_gerais(fonte_id):
        """Calcula métricas gerais para o dashboard, incluindo GERAÇÃO e CONSUMO."""
        if not PANDAS_AVAILABLE:
            return DashboardController._gerar_metricas_ficticias()
            
        df = DashboardController.get_dados_fonte(fonte_id)
        
        if df is None or df.empty:
            return DashboardController._gerar_metricas_ficticias()
        
        # --- Métricas de GERAÇÃO (já existentes) ---
        total_energia = df['energia_kwh'].sum()
        potencia_maxima = df['potencia_kw'].max()
        
        df['data'] = pd.to_datetime(df['data_hora']).dt.date
        energia_por_dia = df.groupby('data')['energia_kwh'].sum()
        media_diaria = energia_por_dia.mean()
        dias_monitorados = len(energia_por_dia)
        ultima_atualizacao = df['data_hora'].max()

        # --- LÓGICA DE SIMULAÇÃO DE CONSUMO ADICIONADA AQUI ---
        # Simula que o consumo é 80% da energia gerada, com uma pequena variação aleatória.
        import random
        consumo_total = total_energia * 0.8 * random.uniform(0.95, 1.05)
        consumo_medio_diario = media_diaria * 0.8 * random.uniform(0.95, 1.05)
        # ---------------------------------------------------------
        
        return {
            'total_energia': round(total_energia, 2),
            'potencia_maxima': round(potencia_maxima, 2),
            'media_diaria': round(media_diaria, 2),
            'dias_monitorados': dias_monitorados,
            'ultima_atualizacao': ultima_atualizacao.strftime('%d/%m/%Y %H:%M'),

            # --- NOVAS MÉTRICAS DE CONSUMO ---
            'consumo_total': round(consumo_total, 2),
            'consumo_medio_diario': round(consumo_medio_diario, 2),
            'consumo_por_tipo': "N/A" # Deixamos como "Não Aplicável" por enquanto
        }
    
    @staticmethod
    def _gerar_metricas_ficticias():
        """Gera métricas fictícias para demonstração quando não há dados reais"""
        # (O conteúdo deste método permanece o mesmo)
        import random
        dias_monitorados = random.randint(25, 35)
        media_diaria = random.uniform(12.5, 18.2)
        total_energia = media_diaria * dias_monitorados
        potencia_maxima = random.uniform(4.2, 5.8)
        return {
            'total_energia': round(total_energia, 2),
            'potencia_maxima': round(potencia_maxima, 2),
            'media_diaria': round(media_diaria, 2),
            'dias_monitorados': dias_monitorados,
            'ultima_atualizacao': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
    
    @staticmethod
    def get_dados_producao_diaria(fonte_id):
        """Obtém dados de produção diária para gráficos"""
        # (O conteúdo deste método permanece o mesmo)
        if not PANDAS_AVAILABLE:
            return DashboardController._gerar_dados_diarios_ficticios()
        df = DashboardController.get_dados_fonte(fonte_id)
        if df is None or df.empty:
            return DashboardController._gerar_dados_diarios_ficticios()
        df['data'] = df['data_hora'].dt.date
        producao_diaria = df.groupby('data')['energia_kwh'].sum().reset_index()
        resultado = []
        for _, row in producao_diaria.iterrows():
            resultado.append({
                'data': row['data'].strftime('%d/%m/%Y'),
                'energia': round(row['energia_kwh'], 2)
            })
        return resultado
    
    @staticmethod
    def _gerar_dados_diarios_ficticios():
        """Gera dados fictícios de produção diária para demonstração"""
        # (O conteúdo deste método permanece o mesmo)
        resultado = []
        hoje = datetime.now()
        for i in range(14, 0, -1):
            data = hoje - timedelta(days=i)
            base = 15.0
            if data.weekday() >= 5:
                fator_dia = 0.8
            else:
                fator_dia = 1.0
            import random
            variacao = random.uniform(0.7, 1.3)
            energia = round(base * fator_dia * variacao, 2)
            resultado.append({
                'data': data.strftime('%d/%m/%Y'),
                'energia': energia
            })
        return resultado
    
    @staticmethod
    def get_dados_producao_horaria(fonte_id, dia=None):
        """Obtém dados de produção por hora para um dia específico"""
        # (O conteúdo deste método permanece o mesmo, com uma pequena correção)
        if not PANDAS_AVAILABLE:
            return DashboardController._gerar_dados_horarios_ficticios()
        df = DashboardController.get_dados_fonte(fonte_id)
        if df is None or df.empty:
            return DashboardController._gerar_dados_horarios_ficticios()
        if dia is None:
            dia = df['data_hora'].dt.date.max()
        else:
            dia = datetime.strptime(dia, '%Y-%m-%d').date()
        df_dia = df[df['data_hora'].dt.date == dia].copy() # Usar .copy() para evitar SettingWithCopyWarning
        if df_dia.empty:
            return DashboardController._gerar_dados_horarios_ficticios()
        df_dia['hora'] = df_dia['data_hora'].dt.hour
        producao_horaria = df_dia.groupby('hora')['potencia_kw'].mean().reset_index()
        resultado = []
        for hora in range(24):
            energia = 0
            hora_df = producao_horaria[producao_horaria['hora'] == hora]
            if not hora_df.empty:
                energia = round(hora_df['potencia_kw'].iloc[0], 2)
            resultado.append({
                'hora': f"{hora:02d}:00",
                'potencia': energia
            })
        return resultado
        
    @staticmethod
    def _gerar_dados_horarios_ficticios():
        """Gera dados fictícios de produção horária para demonstração"""
        # (O conteúdo deste método permanece o mesmo)
        resultado = []
        padrao_solar = [0, 0, 0, 0, 0, 0.1, 0.2, 0.5, 1.2, 2.1, 2.8, 3.4, 3.7, 3.5, 3.2, 2.8, 2.0, 1.3, 0.6, 0.1, 0, 0, 0, 0]
        import random
        for hora in range(24):
            base = padrao_solar[hora]
            variacao = random.uniform(0.8, 1.2)
            potencia = round(base * variacao, 2)
            resultado.append({ 'hora': f"{hora:02d}:00", 'potencia': potencia })
        return resultado

    @staticmethod
    def obter_detalhes_calculo_excedente(fonte_id):
        """Retorna detalhes do cálculo do excedente."""
        # (O conteúdo deste método permanece o mesmo)
        try:
            from app.services.calculos import (obter_producao, obter_consumo, calcular_excedente)
        except Exception:
            return {'producao': 0.0, 'consumo': 0.0, 'excedente': 0.0, 'passos': ['Não foi possível carregar as funções de cálculo.']}
        producao = float(obter_producao(fonte_id))
        consumo = float(obter_consumo(fonte_id))
        excedente = float(calcular_excedente(fonte_id))
        passos = [
            'Funções utilizadas: obter_producao(fonte_id), obter_consumo(fonte_id), calcular_excedente(fonte_id)',
            f'Produção total (kWh): {producao}', f'Consumo total (kWh): {consumo}',
            'Fórmula: excedente = max(0, produção - consumo)',
            f'Cálculo: excedente = max(0, {producao} - {consumo}) = {excedente} kWh',
        ]
        return {'producao': producao, 'consumo': consumo, 'excedente': excedente, 'passos': passos}

    # --- MÉTODO CORRIGIDO ---
    # A indentação foi ajustada para que ele fique DENTRO da classe DashboardController
    @staticmethod
    def calcular_excedente_reivindicavel(wallet_address):
        """
        Calcula a energia excedente gerada desde a última reivindicação de uma carteira.
        """
        # Assumindo que a carteira está ligada à fonte_id=1.
        fonte_id = 1
        
        ultima_transacao = TransacaoRepository.get_ultima_reivindicacao_por_wallet(wallet_address)
        data_inicio = None
        if ultima_transacao:
            data_inicio = datetime.strptime(ultima_transacao['data'], '%Y-%m-%d %H:%M:%S')

        df_geracao = DashboardController.get_dados_fonte(fonte_id)
        if df_geracao is None or df_geracao.empty:
            return 0.0

        df_geracao['data_hora'] = pd.to_datetime(df_geracao['data_hora'])

        if data_inicio:
            df_filtrado = df_geracao[df_geracao['data_hora'] > data_inicio]
        else:
            df_filtrado = df_geracao

        excedente_calculado = df_filtrado['energia_kwh'].sum()
        
        return round(excedente_calculado, 4)