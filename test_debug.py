import urllib.request
import urllib.parse
import http.cookiejar

def test_login_debug():
    print("🧪 TESTANDO LOGIN NO SERVIDOR DEBUG (PORTA 5004)")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5004"
    
    # Cookie jar para manter sessão
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    
    try:
        # 1. GET na página de login
        print("1️⃣ Acessando /login (GET)...")
        req = urllib.request.Request(f"{base_url}/login")
        response = opener.open(req)
        print(f"   ✅ Status: {response.status}")
        
        # 2. POST para fazer login
        print("2️⃣ Fazendo login (POST)...")
        login_data = urllib.parse.urlencode({
            'username': 'admin',
            'password': 'admin'
        }).encode('utf-8')
        
        req = urllib.request.Request(f"{base_url}/login", data=login_data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        response = opener.open(req)
        
        print(f"   Status: {response.status}")
        print(f"   URL final: {response.url}")
        
        # Verificar se redirecionou
        if 'dashboard' in response.url:
            print("   ✅ SUCESSO! Redirecionado para dashboard")
            
            # Ler conteúdo do dashboard
            content = response.read().decode('utf-8')
            if 'LOGIN FUNCIONANDO PERFEITAMENTE' in content:
                print("   ✅ Dashboard carregado corretamente")
                return True
                
        else:
            print("   ❌ Não redirecionou para dashboard")
            content = response.read().decode('utf-8')
            print(f"   Conteúdo da resposta (primeiros 200 chars): {content[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        
    return False

if __name__ == "__main__":
    success = test_login_debug()
    
    if success:
        print("\n🎉 LOGIN FUNCIONA PERFEITAMENTE!")
        print("🔧 O problema pode estar no servidor principal (porta 5003)")
        print("💡 Sugestões:")
        print("   1. Use o servidor debug na porta 5004")
        print("   2. Ou corrija o servidor principal")
    else:
        print("\n❌ Problema também no servidor debug")
        print("🔧 Investigar código de autenticação")