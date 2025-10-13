# app/models/transacao.py

import os
import json
from datetime import datetime

class TransacaoRepository:
    TRANSACOES_FILE = os.path.join('data', 'transacoes.json')

    @classmethod
    def _ler_transacoes(cls):
        if not os.path.exists(cls.TRANSACOES_FILE):
            return []
        with open(cls.TRANSACOES_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    @classmethod
    def salvar_transacao(cls, wallet_address, kwh_excedente, gec_recebido, tx_hash): # Alterado de fonte_id para wallet_address
        transacoes = cls._ler_transacoes()
        
        nova_transacao = {
            "id": len(transacoes) + 1,
            "wallet_address": wallet_address, # Alterado de fonte_id
            "data": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "kwh_excedente": kwh_excedente,
            "gec_recebido": gec_recebido,
            "status": "Processado",
            "tx_hash": tx_hash
        }
        
        transacoes.append(nova_transacao)
        
        os.makedirs(os.path.dirname(cls.TRANSACOES_FILE), exist_ok=True)
        with open(cls.TRANSACOES_FILE, 'w', encoding='utf-8') as f:
            json.dump(transacoes, f, indent=4, ensure_ascii=False)
            
        return nova_transacao

    @classmethod
    def buscar_por_wallet_address(cls, wallet_address): # Renomeado de buscar_por_fonte_id
        """Busca todas as transações para um endereço de carteira específico."""
        transacoes = cls._ler_transacoes()
        return [t for t in transacoes if t.get('wallet_address') == wallet_address]

    @classmethod
    def get_ultima_reivindicacao_por_wallet(cls, wallet_address): # Renomeado de get_ultima_reivindicacao
        """Retorna a transação de reivindicação mais recente para uma carteira."""
        transacoes_carteira = cls.buscar_por_wallet_address(wallet_address)
        if not transacoes_carteira:
            return None
        return sorted(transacoes_carteira, key=lambda t: t['data'], reverse=True)[0]