import requests
import time

def test_routes():
    """Testa todas as rotas que estavam com problema de 404"""
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
    
    # Testar rotas principais
    routes_to_test = [
        ("/", "Dashboard"),
        ("/dashboard", "Dashboard"),
        ("/clientes_simple", "Clientes Simple"),
        ("/apolices_simple", "Apólices Simple"), 
        ("/sinistros_simple", "Sinistros Simple"),
        ("/novo_cliente", "Novo Cliente"),
        ("/nova_apolice", "Nova Apólice"),
        ("/novo_sinistro", "Novo Sinistro"),
    ]
    
    print("\n🧪 Testando rotas principais...")
    for route, name in routes_to_test:
        try:
            response = session.get(f"{base_url}{route}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name} ({route}) - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} ({route}) - Erro: {e}")
    
    # Testar rotas de edição (se houver clientes/apólices)
    print("\n🔧 Testando rotas de edição...")
    
    # Verificar se há clientes
    response = session.get(f"{base_url}/clientes_simple")
    if "editar_cliente" in response.text:
        print("✅ Links de editar cliente encontrados")
    
    # Verificar se há apólices
    response = session.get(f"{base_url}/apolices_simple")
    if "editar_apolice" in response.text:
        print("✅ Links de editar apólice encontrados")
    
    # Verificar se há sinistros
    response = session.get(f"{base_url}/sinistros_simple")
    if "editar_sinistro" in response.text:
        print("✅ Links de editar sinistro encontrados")
    
    print("\n✅ Teste completo! Verificar os resultados acima.")
    return True

if __name__ == "__main__":
    test_routes()