import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (do .env na raiz do projeto Flask)
load_dotenv()

# --- CONFIGURAÇÃO DO CONTRATO ---
CONTRACT_ADDRESS = "0xF4986525C69B335d504437Df5c0715831ed02ff9"
CONTRACT_ABI = """
[
    { "inputs": [ { "internalType": "address", "name": "initialOwner", "type": "address" } ], "stateMutability": "nonpayable", "type": "constructor" },
    { "name": "Approval", "type": "event", "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "owner", "type": "address" }, { "indexed": true, "internalType": "address", "name": "spender", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "value", "type": "uint256" } ] },
    { "name": "OwnershipTransferred", "type": "event", "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "previousOwner", "type": "address" }, { "indexed": true, "internalType": "address", "name": "newOwner", "type": "address" } ] },
    { "name": "Transfer", "type": "event", "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "from", "type": "address" }, { "indexed": true, "internalType": "address", "name": "to", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "value", "type": "uint256" } ] },
    { "name": "allowance", "type": "function", "stateMutability": "view", "inputs": [ { "internalType": "address", "name": "owner", "type": "address" }, { "internalType": "address", "name": "spender", "type": "address" } ], "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ] },
    { "name": "approve", "type": "function", "stateMutability": "nonpayable", "inputs": [ { "internalType": "address", "name": "spender", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ] },
    { "name": "balanceOf", "type": "function", "stateMutability": "view", "inputs": [ { "internalType": "address", "name": "account", "type": "address" } ], "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ] },
    { "name": "decimals", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [ { "internalType": "uint8", "name": "", "type": "uint8" } ] },
    { "name": "decreaseAllowance", "type": "function", "stateMutability": "nonpayable", "inputs": [ { "internalType": "address", "name": "spender", "type": "address" }, { "internalType": "uint256", "name": "subtractedValue", "type": "uint256" } ], "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ] },
    { "name": "increaseAllowance", "type": "function", "stateMutability": "nonpayable", "inputs": [ { "internalType": "address", "name": "spender", "type": "address" }, { "internalType": "uint256", "name": "addedValue", "type": "uint256" } ], "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ] },
    { "name": "mint", "type": "function", "stateMutability": "nonpayable", "inputs": [ { "internalType": "address", "name": "to", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "outputs": [] },
    { "name": "name", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [ { "internalType": "string", "name": "", "type": "string" } ] },
    { "name": "owner", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [ { "internalType": "address", "name": "", "type": "address" } ] },
    { "name": "renounceOwnership", "type": "function", "stateMutability": "nonpayable", "inputs": [], "outputs": [] },
    { "name": "symbol", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [ { "internalType": "string", "name": "", "type": "string" } ] },
    { "name": "totalSupply", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ] },
    { "name": "transfer", "type": "function", "stateMutability": "nonpayable", "inputs": [ { "internalType": "address", "name": "to", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ] },
    { "name": "transferFrom", "type": "function", "stateMutability": "nonpayable", "inputs": [ { "internalType": "address", "name": "from", "type": "address" }, { "internalType": "address", "name": "to", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ] },
    { "name": "transferOwnership", "type": "function", "stateMutability": "nonpayable", "inputs": [ { "internalType": "address", "name": "newOwner", "type": "address" } ], "outputs": [] }
]
"""

# --- CONEXÃO COM A BLOCKCHAIN ---
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
BACKEND_WALLET_PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3 = None
contract = None
backend_account = None

if SEPOLIA_RPC_URL and BACKEND_WALLET_PRIVATE_KEY:
    try:
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
        backend_account = w3.eth.account.from_key(BACKEND_WALLET_PRIVATE_KEY)
        checksum_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
        abi = json.loads(CONTRACT_ABI)
        contract = w3.eth.contract(address=checksum_address, abi=abi)
        
        # --- VERIFICAÇÃO DE PROPRIEDADE ---
        contract_owner = contract.functions.owner().call()
        if contract_owner == backend_account.address:
            print("✅ Verificação de propriedade bem-sucedida: a carteira do backend é a dona do contrato.")
        else:
            print("❌ ERRO CRÍTICO DE PERMISSÃO:")
            print(f"    - Dono do Contrato na Blockchain: {contract_owner}")
            print(f"    - Carteira do Backend (do .env): {backend_account.address}")
            print("    - As carteiras são DIFERENTES. A função de mint VAI FALHAR.")
            print("    - SOLUÇÃO: Garanta que a PRIVATE_KEY no .env da raiz do projeto seja da mesma conta que publicou o contrato.")
        
        print("✅ Conexão com a blockchain e contrato GreenEnergyCredit bem-sucedida!")

    except Exception as e:
        print(f"❌ Erro ao inicializar o serviço de blockchain: {e}")
else:
    print("⚠️ AVISO: Variáveis de ambiente para blockchain não definidas.")


def mint_gec_tokens(to_address, amount):
    if not all([w3, contract, backend_account]):
        return {"success": False, "message": "Serviço de blockchain não inicializado corretamente."}

    try:
        checksum_to_address = Web3.to_checksum_address(to_address)
        amount_in_wei = w3.to_wei(str(amount), 'ether')
        nonce = w3.eth.get_transaction_count(backend_account.address)
        
        tx_data = contract.functions.mint(checksum_to_address, amount_in_wei).build_transaction({
            'chainId': 11155111,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'from': backend_account.address,
            'nonce': nonce
        })

        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=BACKEND_WALLET_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transação de mint enviada! Hash: {tx_hash.hex()}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 0:
            raise Exception(f"A transação falhou (foi revertida) na blockchain. Verifique o Etherscan para detalhes.")

        print(f"Transação confirmada com sucesso no bloco: {receipt.blockNumber}")
        return {
            "success": True, 
            "message": f"{amount} GEC mintados com sucesso para {to_address}",
            "tx_hash": tx_hash.hex()
        }
    except Exception as e:
        print(f"❌ ERRO ao tentar mintar tokens: {e}")
        return {"success": False, "message": f"Erro no processo de mint: {str(e)}"}

def get_gec_balance(address):
    if not all([w3, contract]):
        return 0.0
    try:
        checksum_address = Web3.to_checksum_address(address)
        balance_in_wei = contract.functions.balanceOf(checksum_address).call()
        balance = w3.from_wei(balance_in_wei, 'ether')
        return float(balance)
    except Exception as e:
        print(f"❌ Erro ao buscar saldo para o endereço {address}: {e}")
        return 0.0