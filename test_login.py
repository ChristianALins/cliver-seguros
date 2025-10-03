import requests
import json

# Teste de login via POST
url = 'http://127.0.0.1:5000/login'

# Teste com os campos em inglês (como está no template)
data = {
    'username': 'admin',
    'password': 'admin'
}

print("=== TESTE DE LOGIN ===")
print(f"URL: {url}")
print(f"Dados: {data}")

try:
    response = requests.post(url, data=data, allow_redirects=False)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        print("✅ Login bem-sucedido! Redirecionamento detectado.")
        print(f"Location: {response.headers.get('Location', 'N/A')}")
    else:
        print("❌ Login falhou.")
        print(f"Content: {response.text[:500]}...")

except Exception as e:
    print(f"❌ Erro na requisição: {e}")

print("\n=== TESTE COM CAMPOS EM PORTUGUÊS ===")
data2 = {
    'usuario': 'admin',
    'senha': 'admin'
}
print(f"Dados: {data2}")

try:
    response2 = requests.post(url, data=data2, allow_redirects=False)
    print(f"Status: {response2.status_code}")
    
    if response2.status_code == 302:
        print("✅ Login bem-sucedido!")
        print(f"Location: {response2.headers.get('Location', 'N/A')}")
    else:
        print("❌ Login falhou.")

except Exception as e:
    print(f"❌ Erro na requisição: {e}")