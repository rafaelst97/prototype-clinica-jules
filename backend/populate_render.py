"""
Script para popular o banco de dados do Render remotamente
Execute localmente: python populate_render.py
"""

import requests
import sys

# URL do backend no Render
BACKEND_URL = "https://clinica-saude-backend.onrender.com"

def popular_banco():
    """Popula o banco de dados via endpoint da API"""
    
    print("🔄 Conectando ao backend do Render...")
    
    # 1. Verificar se o backend está online
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if health.status_code != 200:
            print("❌ Backend não está respondendo corretamente")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar no backend: {e}")
        return False
    
    print("✅ Backend está online!")
    
    # 2. Popular dados de teste
    print("\n🔄 Populando banco de dados com dados de teste...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/admin/popular-dados",
            timeout=30  # 30 segundos (pode demorar)
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCESSO! Banco de dados populado!")
            print("\n📊 Dados criados:")
            for key, value in result.get("dados_criados", {}).items():
                print(f"   - {key}: {value}")
            
            print("\n🔑 Credenciais de teste:")
            for tipo, creds in result.get("credenciais_teste", {}).items():
                print(f"\n   {tipo.upper()}:")
                print(f"   Email: {creds['email']}")
                print(f"   Senha: {creds['senha']}")
            
            return True
        else:
            print(f"❌ Erro ao popular: {response.status_code}")
            print(response.json())
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def limpar_banco():
    """Limpa todos os dados do banco"""
    
    print("⚠️  ATENÇÃO: Isso vai DELETAR todos os dados!")
    confirm = input("Digite 'CONFIRMAR' para prosseguir: ")
    
    if confirm != "CONFIRMAR":
        print("❌ Operação cancelada")
        return False
    
    print("\n🔄 Limpando banco de dados...")
    
    try:
        response = requests.delete(
            f"{BACKEND_URL}/admin/limpar-dados",
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Banco de dados limpo com sucesso!")
            return True
        else:
            print(f"❌ Erro ao limpar: {response.status_code}")
            print(response.json())
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   POPULAR BANCO DE DADOS - Clínica Saúde+ (Render)")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--limpar":
        limpar_banco()
    else:
        popular_banco()
    
    print("\n" + "=" * 60)
