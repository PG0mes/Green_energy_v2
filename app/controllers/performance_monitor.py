import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class PerformanceMonitor:
    @staticmethod
    def analisar_performance(fonte_id):
        """Analisa a performance de uma fonte de energia"""
        try:
            # Verificar arquivos de dados
            path_simulado = f'data/simulated/fonte_{fonte_id}_simulado.csv'
            processed_dir = 'data/processed'
            processed_files = [f for f in os.listdir(processed_dir) 
                             if f.startswith(f'fonte_{fonte_id}_') and f.endswith('.csv')] if os.path.exists(processed_dir) else []
            
            # Carregar dados
            if processed_files:
                # Usar dados reais se disponíveis
                df = pd.read_csv(os.path.join(processed_dir, processed_files[0]))
            elif os.path.exists(path_simulado):
                # Usar dados simulados como fallback
                df = pd.read_csv(path_simulado)
            else:
                return {
                    'sucesso': False,
                    'mensagem': 'Nenhum dado disponível para análise',
                    'performance_status': 'indisponível'
                }
            
            # Calcular métricas básicas
            metricas = {
                'media_diaria': df['geracao'].mean(),
                'maxima_diaria': df['geracao'].max(),
                'minima_diaria': df['geracao'].min(),
                'desvio_padrao': df['geracao'].std(),
                'total_gerado': df['geracao'].sum()
            }
            
            # Análise de tendência
            df['data'] = pd.to_datetime(df['data'])
            df['dia_semana'] = df['data'].dt.dayofweek
            
            # Calcular média por dia da semana
            media_por_dia = df.groupby('dia_semana')['geracao'].mean()
            
            # Identificar dias com performance abaixo da média
            media_geral = df['geracao'].mean()
            dias_baixa_performance = df[df['geracao'] < media_geral * 0.8]
            
            # Determinar status de performance
            if len(dias_baixa_performance) > len(df) * 0.3:  # Mais de 30% dos dias com baixa performance
                performance_status = 'crítico'
            elif len(dias_baixa_performance) > len(df) * 0.1:  # Mais de 10% dos dias com baixa performance
                performance_status = 'atenção'
            else:
                performance_status = 'normal'
            
            return {
                'sucesso': True,
                'metricas': metricas,
                'media_por_dia': media_por_dia.to_dict(),
                'dias_baixa_performance': len(dias_baixa_performance),
                'ultima_atualizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'performance_status': performance_status
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro na análise de performance: {str(e)}',
                'performance_status': 'indisponível'
            }
    
    @staticmethod
    def obter_alertas(fonte_id, apenas_ativos=False):
        """Obtém alertas de performance para uma fonte"""
        try:
            # Simular alguns alertas para demonstração
            alertas = [
                {
                    'id': 1,
                    'fonte_id': fonte_id,
                    'tipo': 'baixa_geracao',
                    'mensagem': 'Geração abaixo do esperado nos últimos 3 dias',
                    'data_criacao': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    'resolvido': False
                },
                {
                    'id': 2,
                    'fonte_id': fonte_id,
                    'tipo': 'variacao_anormal',
                    'mensagem': 'Variação anormal detectada na geração',
                    'data_criacao': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                    'resolvido': True
                }
            ]
            
            if apenas_ativos:
                alertas = [a for a in alertas if not a['resolvido']]
            
            return alertas
            
        except Exception as e:
            return []
    
    @staticmethod
    def marcar_alerta_resolvido(fonte_id, alerta_id):
        """Marca um alerta como resolvido"""
        try:
            # Em uma implementação real, isso atualizaria um banco de dados
            # Por enquanto, apenas simula o sucesso
            return True
        except Exception:
            return False
