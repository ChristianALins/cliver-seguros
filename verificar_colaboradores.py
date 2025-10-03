import sqlite3

def verificar_tabelas():
    conn = sqlite3.connect('cliver_seguros.db')
    cursor = conn.cursor()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    
    print("Tabelas existentes:")
    for tabela in tabelas:
        print(f"- {tabela[0]}")
        
    # Verificar se existe tabela colaboradores
    if ('colaboradores',) in tabelas:
        print("\n✅ Tabela 'colaboradores' encontrada!")
        cursor.execute("SELECT * FROM colaboradores LIMIT 3")
        dados = cursor.fetchall()
        print(f"Registros encontrados: {len(dados)}")
    else:
        print("\n❌ Tabela 'colaboradores' NÃO encontrada!")
        
    conn.close()

if __name__ == "__main__":
    verificar_tabelas()