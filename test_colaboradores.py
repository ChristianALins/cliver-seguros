import requests
import time

def test_colaboradores_completo():
    """Testa todas as funcionalidades de colaboradores"""
    base_url = "http://localhost:5003"
    
    # Fazer login primeiro
    session = requests.Session()
    
    print("🔐 Fazendo login...")
    login_data = {"username": "admin", "password": "admin"}
    response = session.post(f"{base_url}/login", data=login_data)
    
    if response.status_code != 200:
        print("❌ Erro no login!")
        return False
    
    print("✅ Login realizado com sucesso!")
    
    # Testar rotas de colaboradores
    routes_colaboradores = [
        ("/colaboradores", "Listagem de Colaboradores"),
        ("/novo_colaborador", "Novo Colaborador"),
        ("/colaboradores/novo", "Novo Colaborador (alternativo)"),
    ]
    
    print("\n🧪 Testando funcionalidades de colaboradores...")
    for route, name in routes_colaboradores:
        try:
            response = session.get(f"{base_url}{route}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name} ({route}) - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} ({route}) - Erro: {e}")
    
    # Verificar se há dados de colaboradores na listagem
    print("\n🔍 Verificando dados de colaboradores...")
    response = session.get(f"{base_url}/colaboradores")
    if "João Silva" in response.text and "Maria Santos" in response.text:
        print("✅ Dados de exemplo encontrados na listagem")
    else:
        print("❌ Dados de exemplo não encontrados")
    
    print("\n✅ Teste de colaboradores completo!")
    return True

if __name__ == "__main__":
    test_colaboradores_completo()