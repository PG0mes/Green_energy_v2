import os
from web3 import Web3
from dotenv import load_dotenv
import json

print("--- INICIANDO TESTE DE CONEXÃO ---")

# Carrega as variáveis do arquivo .env
load_dotenv()
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = "0xf4986525C69B335d504437DF5C0715831eD02fF9" # O endereço do nosso contrato

# O ABI do contrato (simplificado para o teste)
MINIMAL_ABI = """
[
    { "name": "owner", "type": "function", "stateMutability": "view", "inputs": [], "outputs": [ { "internalType": "address", "name": "", "type": "address" } ] }
]
"""

if not SEPOLIA_RPC_URL or not PRIVATE_KEY:
    print("❌ ERRO: Não foi possível encontrar SEPOLIA_RPC_URL ou PRIVATE_KEY no arquivo .env")
else:
    print("✅ Variáveis de ambiente carregadas.")
    print(f"   - URL RPC: ...{SEPOLIA_RPC_URL[-10:]}") # Mostra apenas o final da URL
    
    try:
        # 1. Conectar ao nó
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
        if not w3.is_connected():
            raise Exception("Falha ao conectar com o provedor RPC.")
        print("✅ Conexão com o nó da blockchain (Alchemy) bem-sucedida!")

        # 2. Carregar a carteira do backend
        backend_account = w3.eth.account.from_key(PRIVATE_KEY)
        print(f"✅ Carteira do backend carregada: {backend_account.address}")

        # 3. Tentar interagir com o contrato
        checksum_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
        abi = json.loads(MINIMAL_ABI)
        contract = w3.eth.contract(address=checksum_address, abi=abi)
        print("✅ Objeto do contrato criado com sucesso.")

        # 4. Chamar uma função de leitura do contrato (não gasta gás)
        print("...Tentando chamar a função 'owner()' do contrato...")
        contract_owner = contract.functions.owner().call()
        print(f"✅ SUCESSO! O dono do contrato na blockchain é: {contract_owner}")

        # 5. Verificação final
        if contract_owner == backend_account.address:
            print("\n--- DIAGNÓSTICO: TUDO CERTO! ---")
            print("A carteira do backend é a dona do contrato. A conexão está perfeita.")
        else:
            print("\n--- DIAGNÓSTICO: ERRO DE PERMISSÃO! ---")
            print("A conexão funcionou, mas a carteira do backend não é a dona do contrato.")

    except Exception as e:
        print(f"\n--- DIAGNÓSTICO: FALHA NA CONEXÃO! ---")
        print(f"❌ O teste falhou com o seguinte erro: {e}")