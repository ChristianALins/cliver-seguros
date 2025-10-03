import urllib.request
import urllib.parse
import http.cookiejar
import json

def test_login_detailed():
    print("🔍 DIAGNÓSTICO DETALHADO DO LOGIN")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5003"
    
    # Criar um cookie jar para manter a sessão
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    
    try:
        # 1. Primeiro acessar a página de login (GET)
        print("1️⃣ Acessando página de login (GET)...")
        req = urllib.request.Request(f"{base_url}/login")
        response = opener.open(req)
        
        print(f"   Status: {response.status}")
        print(f"   Headers: {dict(response.headers)}")
        
        content = response.read().decode('utf-8')
        print(f"   Conteúdo encontrado: {'CLIVER SEGUROS' in content}")
        print(f"   Formulário encontrado: {'<form' in content}")
        
        # 2. Fazer login (POST)
        print("\n2️⃣ Fazendo login (POST)...")
        login_data = urllib.parse.urlencode({
            'username': 'admin',
            'password': 'admin'
        }).encode('utf-8')
        
        req = urllib.request.Request(f"{base_url}/login", data=login_data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('Referer', f"{base_url}/login")
        
        response = opener.open(req)
        
        print(f"   Status: {response.status}")
        print(f"   URL final: {response.url}")
        
        # Se redirecionou, foi sucesso
        if response.url.endswith('/dashboard') or 'dashboard' in response.url:
            print("   ✅ LOGIN SUCESSO - Redirecionado para dashboard")
            
            # Tentar acessar o dashboard
            print("\n3️⃣ Acessando dashboard...")
            req = urllib.request.Request(f"{base_url}/dashboard")
            response = opener.open(req)
            content = response.read().decode('utf-8')
            
            if 'dashboard' in content.lower() or 'cliver' in content.lower():
                print("   ✅ Dashboard acessado com sucesso")
                return True
            else:
                print("   ❌ Erro ao acessar dashboard")
                return False
        else:
            print("   ❌ LOGIN FALHOU - Não redirecionou")
            content = response.read().decode('utf-8')
            if 'erro' in content.lower() or 'inválid' in content.lower():
                print("   Mensagem de erro encontrada na resposta")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro durante o teste: {e}")
        return False

def test_direct_dashboard():
    print("\n4️⃣ Testando acesso direto ao dashboard (sem login)...")
    try:
        response = urllib.request.urlopen("http://127.0.0.1:5003/dashboard", timeout=5)
        if response.url.endswith('/login'):
            print("   ✅ Redirecionamento para login funcionando (segurança OK)")
        else:
            print("   ⚠️ Dashboard acessível sem login (problema de segurança)")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    success = test_login_detailed()
    test_direct_dashboard()
    
    if success:
        print("\n🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("💡 Se ainda há problemas no navegador, tente:")
        print("   1. Limpar cache e cookies")
        print("   2. Usar modo incógnito")
        print("   3. Verificar se não há bloqueadores")
    else:
        print("\n⚠️ PROBLEMA DETECTADO NO LOGIN!")
        print("🔧 Verificando possíveis soluções...")