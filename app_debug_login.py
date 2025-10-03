from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'cliver_seguros_secret_key_2024'

def get_db():
    conn = sqlite3.connect('cliver_seguros.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    print("📍 Rota / acessada")
    if 'user_id' in session:
        print("   Usuário logado, redirecionando para dashboard")
        return redirect(url_for('dashboard'))
    print("   Usuário não logado, redirecionando para login")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(f"📍 Rota /login acessada - Método: {request.method}")
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"   📝 Dados recebidos: username='{username}', password='{password}'")
        
        if not username or not password:
            print("   ❌ Username ou password vazios")
            flash('Por favor, preencha todos os campos!', 'error')
            return render_template('login_clean.html')
        
        try:
            conn = get_db()
            user = conn.execute('SELECT * FROM users WHERE username = ? AND active = 1', 
                               (username,)).fetchone()
            conn.close()
            
            print(f"   🔍 Usuário encontrado no banco: {user is not None}")
            
            if user:
                print(f"   🔐 Verificando senha...")
                password_ok = check_password_hash(user['password'], password)
                print(f"   🔐 Senha correta: {password_ok}")
                
                if password_ok:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['user_role'] = user['role']
                    
                    print(f"   ✅ LOGIN SUCESSO! Sessão criada para user_id: {user['id']}")
                    
                    # Atualizar último login
                    conn = get_db()
                    conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', 
                                (user['id'],))
                    conn.commit()
                    conn.close()
                    
                    flash('Login realizado com sucesso!', 'success')
                    print("   🔄 Redirecionando para dashboard...")
                    return redirect(url_for('dashboard'))
                else:
                    print("   ❌ Senha incorreta")
                    flash('Senha incorreta!', 'error')
            else:
                print("   ❌ Usuário não encontrado ou inativo")
                flash('Usuário não encontrado!', 'error')
                
        except Exception as e:
            print(f"   💥 Erro no login: {e}")
            flash(f'Erro interno: {str(e)}', 'error')
    
    print("   📄 Renderizando template de login")
    return render_template('login_clean.html')

@app.route('/dashboard')
def dashboard():
    print("📍 Rota /dashboard acessada")
    
    if 'user_id' not in session:
        print("   ❌ Usuário não logado, redirecionando para login")
        return redirect(url_for('login'))
    
    print(f"   ✅ Usuário logado: {session.get('username')} (ID: {session.get('user_id')})")
    
    # Dados simples para o dashboard
    stats = {
        'total_clientes': 150,
        'total_apolices': 89,
        'sinistros_abertos': 12,
        'renovacoes_pendentes': 23
    }
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - CLIVER SEGUROS</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            .header {{ background: linear-gradient(135deg, #00B391, #007d6a); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
            .stat {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #00B391; }}
            .logout {{ background: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 DASHBOARD - CLIVER SEGUROS</h1>
                <p>Bem-vindo, {session.get('username')}!</p>
                <p>Função: {session.get('user_role')}</p>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <h3>{stats['total_clientes']}</h3>
                    <p>Clientes</p>
                </div>
                <div class="stat">
                    <h3>{stats['total_apolices']}</h3>
                    <p>Apólices</p>
                </div>
                <div class="stat">
                    <h3>{stats['sinistros_abertos']}</h3>
                    <p>Sinistros</p>
                </div>
                <div class="stat">
                    <h3>{stats['renovacoes_pendentes']}</h3>
                    <p>Renovações</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <h2>✅ LOGIN FUNCIONANDO PERFEITAMENTE!</h2>
                <p>Sistema CLIVER SEGUROS operacional</p>
                <a href="/logout" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Logout</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    print("📍 Rota /logout acessada")
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/test')
def test():
    return '''
    <h1>🧪 TESTE - CLIVER SEGUROS</h1>
    <p>Servidor funcionando na porta 5004!</p>
    <p><a href="/login">Ir para Login</a></p>
    '''

if __name__ == '__main__':
    print("🚀 INICIANDO SERVIDOR DE DEBUG")
    print("=" * 40)
    print("📊 Dashboard: http://localhost:5004/")
    print("🔑 Login: http://localhost:5004/login")
    print("🧪 Teste: http://localhost:5004/test")
    print("👤 Credenciais: admin / admin")
    print("=" * 40)
    
    app.run(debug=True, port=5004, host='0.0.0.0')