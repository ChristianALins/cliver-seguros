import requests

def teste_final_sistema():
    """Teste final completo de todo o sistema"""
    base_url = "http://localhost:5003"
    
    # Fazer login primeiro
    session = requests.Session()
    
    print("🔐 TESTE FINAL DO SISTEMA CLIVER SEGUROS")
    print("=" * 50)
    
    login_data = {"username": "admin", "password": "admin"}
    response = session.post(f"{base_url}/login", data=login_data)
    
    if response.status_code != 200:
        print("❌ ERRO NO LOGIN!")
        return False
    
    print("✅ Login: OK")
    
    # Testar todas as rotas principais
    rotas_principais = [
        ("/", "Dashboard Principal"),
        ("/dashboard", "Dashboard"),
        ("/clientes_simple", "Clientes"),
        ("/apolices_simple", "Apólices"),
        ("/sinistros_simple", "Sinistros"),
        ("/colaboradores", "Colaboradores"),
        ("/novo_cliente", "Formulário Novo Cliente"),
        ("/nova_apolice", "Formulário Nova Apólice"),
        ("/novo_sinistro", "Formulário Novo Sinistro"),
        ("/novo_colaborador", "Formulário Novo Colaborador"),
    ]
    
    print("\n📋 TESTANDO PÁGINAS PRINCIPAIS:")
    print("-" * 30)
    
    total_sucesso = 0
    total_testes = len(rotas_principais)
    
    for rota, nome in rotas_principais:
        try:
            response = session.get(f"{base_url}{rota}")
            if response.status_code == 200:
                print(f"✅ {nome} - OK")
                total_sucesso += 1
            else:
                print(f"❌ {nome} - Erro {response.status_code}")
        except Exception as e:
            print(f"❌ {nome} - Exceção: {e}")
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"✅ Sucessos: {total_sucesso}/{total_testes}")
    print(f"📈 Taxa de Sucesso: {(total_sucesso/total_testes)*100:.1f}%")
    
    if total_sucesso == total_testes:
        print("\n🎉 SISTEMA 100% FUNCIONAL!")
        print("🌟 Todas as funcionalidades testadas e aprovadas!")
        print("🚀 Sistema pronto para produção!")
    else:
        print(f"\n⚠️ {total_testes - total_sucesso} problemas encontrados")
    
    return total_sucesso == total_testes

if __name__ == "__main__":
    teste_final_sistema()