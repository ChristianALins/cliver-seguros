import requests
import sys

def test_single_route(route):
    """Testa uma rota específica com sessão"""
    base_url = "http://localhost:5003"
    
    # Fazer login primeiro
    session = requests.Session()
    
    print(f"🔐 Fazendo login para testar {route}...")
    login_data = {"username": "admin", "password": "admin"}
    response = session.post(f"{base_url}/login", data=login_data)
    
    if response.status_code != 200:
        print(f"❌ Erro no login! Status: {response.status_code}")
        return
    
    print("✅ Login realizado com sucesso!")
    
    # Testar a rota específica
    print(f"\n🧪 Testando {route}...")
    try:
        response = session.get(f"{base_url}{route}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ ERRO 500 - Detalhes:")
            print(response.text[:500] + "...")
        elif response.status_code == 200:
            print("✅ Sucesso!")
            print(f"Conteúdo parcial: {response.text[:200]}...")
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    route = sys.argv[1] if len(sys.argv) > 1 else "/novo_cliente"
    test_single_route(route)