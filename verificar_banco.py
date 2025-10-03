import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

def verify_database():
    print("🔍 VERIFICANDO BANCO DE DADOS")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('cliver_seguros.db')
        cursor = conn.cursor()
        
        # Verificar se a tabela users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Tabela 'users' encontrada")
            
            # Verificar usuários
            cursor.execute("SELECT id, username, password, active FROM users")
            users = cursor.fetchall()
            
            print(f"📊 Total de usuários: {len(users)}")
            
            for user in users:
                print(f"   ID: {user[0]}, Username: {user[1]}, Ativo: {user[3]}")
                
                # Testar senha do admin
                if user[1] == 'admin':
                    print(f"   🔐 Testando senha do admin...")
                    if check_password_hash(user[2], 'admin'):
                        print("   ✅ Senha 'admin' está correta")
                    else:
                        print("   ❌ Senha 'admin' NÃO confere")
                        print("   🔧 Corrigindo senha do admin...")
                        
                        # Corrigir senha
                        new_password = generate_password_hash('admin')
                        cursor.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_password,))
                        conn.commit()
                        print("   ✅ Senha corrigida!")
        else:
            print("❌ Tabela 'users' NÃO encontrada")
            print("🔧 Criando tabela e usuário admin...")
            
            # Criar tabela
            cursor.execute('''CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )''')
            
            # Criar usuário admin
            admin_password = generate_password_hash('admin')
            cursor.execute('''INSERT INTO users (username, password, email, full_name, role, active) 
                             VALUES (?, ?, ?, ?, ?, ?)''', 
                          ('admin', admin_password, 'admin@cliverseguros.com.br', 'Administrador', 'admin', 1))
            
            conn.commit()
            print("✅ Tabela e usuário criados com sucesso!")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False

if __name__ == "__main__":
    verify_database()