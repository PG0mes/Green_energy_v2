import os
import json
import logging
from web3 import Web3
from dotenv import load_dotenv

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis
load_dotenv()

# --- CONFIGURAÇÕES ---
CONTRACT_ADDRESS = "0x4A0b55E82DAE1CF41C8C01Ef1bE2f906958e62B0"
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# ABI Reduzida (Apenas o necessário para economizar espaço e evitar erros de parsing)
CONTRACT_ABI = [
    {"inputs": [{"internalType": "address","name": "to","type": "address"},{"internalType": "uint256","name": "amount","type": "uint256"}],"name": "mint","outputs": [],"stateMutability": "nonpayable","type": "function"},
    {"inputs": [{"internalType": "address","name": "account","type": "address"}],"name": "balanceOf","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},
    {"inputs": [],"name": "owner","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"}
]

w3 = None
contract = None
backend_account = None

def inicializar_blockchain():
    """Inicializa e diagnostica a conexão com a Blockchain."""
    global w3, contract, backend_account
    
    print("\n" + "="*50)
    print("🔄 INICIALIZANDO SERVIÇO BLOCKCHAIN...")

    if not SEPOLIA_RPC_URL or not PRIVATE_KEY:
        logger.error("❌ ERRO: Variáveis SEPOLIA_RPC_URL ou PRIVATE_KEY não encontradas no .env")
        return False

    try:
        # 1. Conexão
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
        if not w3.is_connected():
            raise Exception("Não foi possível conectar ao Node RPC (Verifique a URL da Alchemy/Infura).")
        
        # 2. Configuração da Conta
        backend_account = w3.eth.account.from_key(PRIVATE_KEY)
        saldo_wei = w3.eth.get_balance(backend_account.address)
        saldo_eth = w3.from_wei(saldo_wei, 'ether')

        print(f"👤 CARTEIRA DO SISTEMA: {backend_account.address}")
        print(f"💰 SALDO ATUAL: {saldo_eth} ETH")

        if saldo_eth < 0.001:
            print("⚠️ ALERTA CRÍTICO: Saldo muito baixo! O erro 'insufficient funds' vai acontecer.")
            print("   -> Envie Sepolia ETH para este endereço acima.")

        # 3. Contrato
        checksum_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
        contract = w3.eth.contract(address=checksum_address, abi=CONTRACT_ABI)

        # 4. Verificação de Propriedade (Ownership)
        try:
            dono_contrato = contract.functions.owner().call()
            if dono_contrato != backend_account.address:
                print(f"❌ ERRO DE PERMISSÃO: A carteira do sistema NÃO é a dona do contrato.")
                print(f"   - Dono atual: {dono_contrato}")
                print(f"   - Sua carteira: {backend_account.address}")
                print("   -> A função 'mint' vai falhar e gastar gás à toa.")
            else:
                print("✅ PERMISSÕES: A carteira é a dona do contrato. Mint liberado.")
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível verificar o dono do contrato: {e}")

        print("="*50 + "\n")
        return True

    except Exception as e:
        logger.error(f"❌ FALHA FATAL na inicialização da blockchain: {e}")
        return False

# Inicializa ao importar
inicializado = inicializar_blockchain()

def mint_gec_tokens(to_address, amount):
    """Cunha novos tokens para um endereço."""
    if not inicializado or not w3 or not contract:
        return {"success": False, "message": "Sistema Blockchain offline ou mal configurado."}

    try:
        print(f"\n🚀 INICIANDO MINT: {amount} GEC para {to_address}...")
        
        # Validações básicas
        if amount <= 0:
            return {"success": False, "message": "Quantidade deve ser maior que zero."}

        checksum_to = Web3.to_checksum_address(to_address)
        amount_wei = w3.to_wei(str(amount), 'ether')
        
        # 1. Verificar saldo antes de tentar (para evitar o erro -32003 feio)
        saldo_atual = w3.eth.get_balance(backend_account.address)
        taxa_estimada = w3.to_wei(0.0005, 'ether') # Estimativa conservadora
        if saldo_atual < taxa_estimada:
             return {"success": False, "message": f"SALDO INSUFICIENTE no Backend. Tem: {w3.from_wei(saldo_atual,'ether')} ETH."}

        # 2. Construir Transação
        nonce = w3.eth.get_transaction_count(backend_account.address)
        
        # Tenta estimar o gás (se falhar aqui, é erro de lógica/permissão, não de saldo)
        try:
            gas_estimate = contract.functions.mint(checksum_to, amount_wei).estimate_gas({
                'from': backend_account.address
            })
            gas_limit = int(gas_estimate * 1.2) # Adiciona 20% de margem
        except Exception as e:
            print(f"⚠️ Falha ao estimar gás (provavelmente não é o dono): {e}")
            gas_limit = 300000 # Valor manual de segurança
        
        tx_data = contract.functions.mint(checksum_to, amount_wei).build_transaction({
            'chainId': 11155111, # Sepolia ID
            'gas': gas_limit,
            'gasPrice': w3.eth.gas_price,
            'from': backend_account.address,
            'nonce': nonce
        })

        # 3. Assinar e Enviar
        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"⏳ Transação enviada! Hash: {tx_hash.hex()}")
        print("   Aguardando confirmação...")

        # 4. Aguardar Recibo
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt.status == 1:
            print(f"✅ SUCESSO! Confirmado no bloco {receipt.blockNumber}")
            return {
                "success": True, 
                "message": f"Mint de {amount} GEC realizado com sucesso!",
                "tx_hash": tx_hash.hex()
            }
        else:
            print("❌ FALHA: A transação foi revertida pela blockchain.")
            return {"success": False, "message": "Transação revertida. Verifique se você é o dono do contrato."}

    except Exception as e:
        logger.error(f"❌ ERRO NO PROCESSO DE MINT: {e}")
        return {"success": False, "message": str(e)}

def get_gec_balance(address):
    """Busca o saldo de tokens GEC de uma carteira."""
    if not contract: return 0.0
    try:
        checksum_addr = Web3.to_checksum_address(address)
        balance_wei = contract.functions.balanceOf(checksum_addr).call()
        return float(w3.from_wei(balance_wei, 'ether'))
    except Exception as e:
        logger.error(f"Erro ao ler saldo: {e}")
        return 0.0