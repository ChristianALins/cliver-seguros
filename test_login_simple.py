import urllib.request
import urllib.parse

# Teste simples de login
url = 'http://127.0.0.1:5000/login'

# Dados de teste
test_data = [
    {'username': 'admin', 'password': 'admin'},
    {'usuario': 'admin', 'senha': 'admin'}
]

print("=== TESTE DE LOGIN CLIVER ===")

for i, data in enumerate(test_data):
    print(f"\n--- Teste {i+1}: {data} ---")
    
    try:
        # Codificar dados
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        
        # Criar requisição
        req = urllib.request.Request(url, data=post_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        # Enviar requisição
        with urllib.request.urlopen(req) as response:
            print(f"Status: {response.getcode()}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.getcode() == 200:
                content = response.read().decode('utf-8')
                if 'dashboard' in content.lower() or 'bem-vindo' in content.lower():
                    print("✅ Login bem-sucedido!")
                else:
                    print("❌ Login falhou - permaneceu na página de login")
            else:
                print(f"Status inesperado: {response.getcode()}")
                
    except urllib.error.HTTPError as e:
        if e.code == 302:
            print("✅ Login bem-sucedido! (Redirecionamento)")
            print(f"Location: {e.headers.get('Location', 'N/A')}")
        else:
            print(f"❌ Erro HTTP {e.code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

print("\n=== VERIFICAÇÃO DIRETA NO BANCO ===")
import sqlite3

try:
    conn = sqlite3.connect('cliver_seguros.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM colaboradores WHERE usuario = 'admin' AND senha = 'admin' AND ativo = 1")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print("✅ Usuário admin/admin encontrado no banco!")
        
        cursor.execute("SELECT id_colaborador, nome, nivel_acesso FROM colaboradores WHERE usuario = 'admin'")
        user = cursor.fetchone()
        print(f"   ID: {user[0]}, Nome: {user[1]}, Nível: {user[2]}")
    else:
        print("❌ Usuário admin/admin NÃO encontrado no banco!")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro ao verificar banco: {e}")