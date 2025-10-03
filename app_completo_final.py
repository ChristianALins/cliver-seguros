from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'cliver_seguros_secret_key_2024'

# Configuração do banco de dados
DATABASE = 'cliver_seguros.db'

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Tabela de usuários
    c.execute('''CREATE TABLE IF NOT EXISTS users (
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
    
    # Inserir usuário admin padrão
    admin_password = generate_password_hash('admin')
    c.execute('''INSERT OR IGNORE INTO users (username, password, email, full_name, role) 
                 VALUES (?, ?, ?, ?, ?)''', 
              ('admin', admin_password, 'admin@cliverseguros.com.br', 'Administrador', 'admin'))
    
    # Tabela de clientes
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE,
        email TEXT,
        telefone TEXT,
        endereco TEXT,
        data_nascimento DATE,
        status TEXT DEFAULT 'ativo',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de seguradoras
    c.execute('''CREATE TABLE IF NOT EXISTS seguradoras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cnpj TEXT,
        contato_nome TEXT,
        contato_telefone TEXT,
        contato_email TEXT,
        status TEXT DEFAULT 'ativa',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de tipos de seguro
    c.execute('''CREATE TABLE IF NOT EXISTS tipos_seguro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        categoria TEXT,
        ativo INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de apólices
    c.execute('''CREATE TABLE IF NOT EXISTS apolices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_apolice TEXT UNIQUE NOT NULL,
        cliente_id INTEGER,
        seguradora_id INTEGER,
        tipo_seguro_id INTEGER,
        valor_premio DECIMAL(10,2),
        valor_franquia DECIMAL(10,2),
        data_inicio DATE,
        data_vencimento DATE,
        status TEXT DEFAULT 'ativa',
        observacoes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id),
        FOREIGN KEY (seguradora_id) REFERENCES seguradoras (id),
        FOREIGN KEY (tipo_seguro_id) REFERENCES tipos_seguro (id)
    )''')
    
    # Tabela de sinistros
    c.execute('''CREATE TABLE IF NOT EXISTS sinistros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        protocolo TEXT UNIQUE NOT NULL,
        apolice_id INTEGER,
        data_ocorrencia DATE,
        data_comunicacao DATE,
        tipo_sinistro TEXT,
        descricao TEXT,
        valor_estimado DECIMAL(10,2),
        valor_franquia DECIMAL(10,2),
        status TEXT DEFAULT 'aberto',
        observacoes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (apolice_id) REFERENCES apolices (id)
    )''')
    
    # Tabela de renovações
    c.execute('''CREATE TABLE IF NOT EXISTS renovacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apolice_id INTEGER,
        data_vencimento_anterior DATE,
        data_nova_vigencia DATE,
        novo_valor_premio DECIMAL(10,2),
        status TEXT DEFAULT 'pendente',
        data_renovacao DATE,
        observacoes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (apolice_id) REFERENCES apolices (id)
    )''')
    
    # Inserir dados de exemplo
    inserir_dados_exemplo(c)
    
    conn.commit()
    conn.close()

def inserir_dados_exemplo(cursor):
    """Insere dados de exemplo no banco"""
    
    # Seguradoras de exemplo
    seguradoras_exemplo = [
        ('Porto Seguro', '05.991.235/0001-59', 'Maria Santos', '(11) 3003-9303', 'maria@portoseguro.com.br'),
        ('Bradesco Seguros', '92.693.118/0001-60', 'João Silva', '(11) 4002-4112', 'joao@bradescoseguros.com.br'),
        ('SulAmérica', '01.578.308/0001-30', 'Ana Costa', '(11) 4020-1111', 'ana@sulamerica.com.br')
    ]
    
    cursor.executemany('''INSERT OR IGNORE INTO seguradoras 
                         (nome, cnpj, contato_nome, contato_telefone, contato_email) 
                         VALUES (?, ?, ?, ?, ?)''', seguradoras_exemplo)
    
    # Tipos de seguro de exemplo
    tipos_seguro_exemplo = [
        ('Auto', 'Seguro para veículos automotores', 'Veículos'),
        ('Residencial', 'Seguro para residências e condomínios', 'Habitação'),
        ('Vida', 'Seguro de vida individual e familiar', 'Pessoas'),
        ('Empresarial', 'Seguro para empresas e estabelecimentos comerciais', 'Empresas'),
        ('Viagem', 'Seguro para viagens nacionais e internacionais', 'Viagem')
    ]
    
    cursor.executemany('''INSERT OR IGNORE INTO tipos_seguro 
                         (nome, descricao, categoria) 
                         VALUES (?, ?, ?)''', tipos_seguro_exemplo)
    
    # Clientes de exemplo
    clientes_exemplo = [
        ('João Silva Santos', '123.456.789-00', 'joao.santos@email.com', '(11) 99999-1111', 'Rua A, 123, São Paulo, SP', '1980-05-15'),
        ('Maria Oliveira Costa', '987.654.321-00', 'maria.costa@email.com', '(11) 99999-2222', 'Rua B, 456, São Paulo, SP', '1985-08-22'),
        ('Pedro Ferreira Lima', '555.666.777-88', 'pedro.lima@email.com', '(11) 99999-3333', 'Rua C, 789, São Paulo, SP', '1975-12-10')
    ]
    
    cursor.executemany('''INSERT OR IGNORE INTO clientes 
                         (nome, cpf, email, telefone, endereco, data_nascimento) 
                         VALUES (?, ?, ?, ?, ?, ?)''', clientes_exemplo)

def get_db():
    """Retorna conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def require_login(f):
    """Decorator para verificar se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print("ACESSO NEGADO - usuario nao logado")
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('login'))
        print(f"ACESSO AUTORIZADO para user_id: {session.get('user_id')}")
        return f(*args, **kwargs)
    return decorated_function

# ROTAS PRINCIPAIS

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/test')
def test():
    """Rota de teste para verificar se o sistema está funcionando"""
    return '''
    <h1>Sistema Cliver Seguros - Teste</h1>
    <p>O sistema está funcionando!</p>
    <ul>
        <li><a href="/login">Login</a></li>
        <li><a href="/dashboard">Dashboard</a></li>
        <li><a href="/clientes">Clientes</a></li>
        <li><a href="/apolices">Apólices</a></li>
        <li><a href="/relatorios">Relatórios</a></li>
    </ul>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(f"LOGIN - Rota /login acessada - Metodo: {request.method}")
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"   LOGIN - Dados recebidos: username='{username}', password='{password}'")
        
        if not username or not password:
            print("   LOGIN ERRO - Username ou password vazios")
            flash('Por favor, preencha todos os campos!', 'error')
            return render_template('login_clean.html')
        
        try:
            conn = get_db()
            user = conn.execute('SELECT * FROM users WHERE username = ? AND active = 1', 
                               (username,)).fetchone()
            conn.close()
            
            print(f"   LOGIN - Usuario encontrado no banco: {user is not None}")
            
            if user:
                print(f"   LOGIN - Verificando senha...")
                password_ok = check_password_hash(user['password'], password)
                print(f"   LOGIN - Senha correta: {password_ok}")
                
                if password_ok:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['user_role'] = user['role']
                    
                    print(f"   LOGIN SUCESSO! Sessao criada para user_id: {user['id']}")
                    
                    # Atualizar último login
                    conn = get_db()
                    conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', 
                                (user['id'],))
                    conn.commit()
                    conn.close()
                    
                    flash('Login realizado com sucesso!', 'success')
                    print("   LOGIN - Redirecionando para dashboard...")
                    return redirect(url_for('dashboard'))
                else:
                    print("   LOGIN ERRO - Senha incorreta")
                    flash('Senha incorreta!', 'error')
            else:
                print("   LOGIN ERRO - Usuario nao encontrado ou inativo")
                flash('Usuário não encontrado!', 'error')
                
        except Exception as e:
            print(f"   LOGIN ERRO - Erro no login: {e}")
            flash(f'Erro interno: {str(e)}', 'error')
    
    print("   LOGIN - Renderizando template de login")
    return render_template('login_clean.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@require_login
def dashboard():
    conn = get_db()
    
    # Estatísticas para o dashboard
    stats = {}
    stats['total_clientes'] = conn.execute('SELECT COUNT(*) as count FROM clientes WHERE status = "ativo"').fetchone()['count']
    stats['total_apolices'] = conn.execute('SELECT COUNT(*) as count FROM apolices WHERE status = "ativa"').fetchone()['count']
    stats['sinistros_abertos'] = conn.execute('SELECT COUNT(*) as count FROM sinistros WHERE status = "aberto"').fetchone()['count']
    stats['renovacoes_pendentes'] = conn.execute('SELECT COUNT(*) as count FROM renovacoes WHERE status = "pendente"').fetchone()['count']
    
    # Apólices próximas ao vencimento (30 dias)
    vencimento_proximo = conn.execute('''
        SELECT a.*, c.nome as cliente_nome, s.nome as seguradora_nome
        FROM apolices a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN seguradoras s ON a.seguradora_id = s.id
        WHERE a.data_vencimento BETWEEN DATE('now') AND DATE('now', '+30 days')
        AND a.status = 'ativa'
        ORDER BY a.data_vencimento
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard_simple.html', stats=stats, vencimentos=vencimento_proximo)

# ROTAS DE CLIENTES

@app.route('/clientes')
@require_login
def listar_clientes():
    conn = get_db()
    clientes = conn.execute('''
        SELECT * FROM clientes 
        WHERE status = 'ativo' 
        ORDER BY nome
    ''').fetchall()
    conn.close()
    return render_template('clientes_simple.html', clientes=clientes)

@app.route('/clientes/novo', methods=['GET', 'POST'])
@app.route('/novo_cliente', methods=['GET', 'POST'])
@require_login
def novo_cliente():
    if request.method == 'POST':
        conn = get_db()
        try:
            conn.execute('''
                INSERT INTO clientes (nome, cpf, email, telefone, endereco, data_nascimento)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                request.form['nome'],
                request.form['cpf'],
                request.form['email'],
                request.form['telefone'],
                request.form['endereco'],
                request.form['data_nascimento']
            ))
            conn.commit()
            flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_clientes'))
        except sqlite3.IntegrityError:
            flash('CPF já cadastrado no sistema!', 'error')
        finally:
            conn.close()
    
    return render_template('novo_cliente_simple.html')

@app.route('/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
@require_login
def editar_cliente(cliente_id):
    conn = get_db()
    
    if request.method == 'POST':
        try:
            conn.execute('''
                UPDATE clientes 
                SET nome=?, cpf=?, email=?, telefone=?, endereco=?, data_nascimento=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                request.form['nome'],
                request.form['cpf'],
                request.form['email'],
                request.form['telefone'],
                request.form['endereco'],
                request.form['data_nascimento'],
                cliente_id
            ))
            conn.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('listar_clientes'))
        except sqlite3.IntegrityError:
            flash('CPF já cadastrado no sistema!', 'error')
        finally:
            conn.close()
    
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
    conn.close()
    
    if not cliente:
        flash('Cliente não encontrado!', 'error')
        return redirect(url_for('listar_clientes'))
    
    return render_template('editar_cliente_simple.html', cliente=cliente)

# ROTAS DE APÓLICES

@app.route('/apolices')
@require_login
def listar_apolices():
    conn = get_db()
    apolices = conn.execute('''
        SELECT a.*, c.nome as cliente_nome, s.nome as seguradora_nome, ts.nome as tipo_seguro_nome
        FROM apolices a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN seguradoras s ON a.seguradora_id = s.id
        JOIN tipos_seguro ts ON a.tipo_seguro_id = ts.id
        WHERE a.status = 'ativa'
        ORDER BY a.data_vencimento
    ''').fetchall()
    conn.close()
    return render_template('apolices_simple.html', apolices=apolices)

@app.route('/apolices/vencimento')
@require_login
def apolices_vencimento():
    """Página de apólices próximas ao vencimento"""
    conn = get_db()
    apolices = conn.execute('''
        SELECT a.*, c.nome as cliente_nome, s.nome as seguradora_nome
        FROM apolices a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN seguradoras s ON a.seguradora_id = s.id
        WHERE a.data_vencimento BETWEEN DATE('now') AND DATE('now', '+60 days')
        AND a.status = 'ativa'
        ORDER BY a.data_vencimento
    ''').fetchall()
    conn.close()
    return render_template('apolices_vencimento.html', apolices=apolices)

@app.route('/apolices/nova', methods=['GET', 'POST'])
@app.route('/nova_apolice', methods=['GET', 'POST'])
@require_login
def nova_apolice():
    conn = get_db()
    
    if request.method == 'POST':
        try:
            conn.execute('''
                INSERT INTO apolices (numero_apolice, cliente_id, seguradora_id, tipo_seguro_id,
                                    valor_premio, valor_franquia, data_inicio, data_vencimento, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['numero_apolice'],
                request.form['cliente_id'],
                request.form['seguradora_id'],
                request.form['tipo_seguro_id'],
                request.form['valor_premio'],
                request.form['valor_franquia'],
                request.form['data_inicio'],
                request.form['data_vencimento'],
                request.form.get('observacoes', '')
            ))
            conn.commit()
            flash('Apólice cadastrada com sucesso!', 'success')
            return redirect(url_for('listar_apolices'))
        except sqlite3.IntegrityError:
            flash('Número de apólice já cadastrado!', 'error')
        finally:
            conn.close()
    
    # Carregar dados para formulário
    clientes = conn.execute('SELECT * FROM clientes WHERE status = "ativo" ORDER BY nome').fetchall()
    seguradoras = conn.execute('SELECT * FROM seguradoras WHERE status = "ativa" ORDER BY nome').fetchall()
    tipos_seguro = conn.execute('SELECT * FROM tipos_seguro WHERE ativo = 1 ORDER BY nome').fetchall()
    conn.close()
    
    return render_template('nova_apolice_simple.html', 
                         clientes=clientes, seguradoras=seguradoras, tipos_seguro=tipos_seguro)

@app.route('/apolices/<int:apolice_id>/editar', methods=['GET', 'POST'])
@require_login
def editar_apolice(apolice_id):
    """Editar uma apólice existente"""
    conn = get_db()
    
    if request.method == 'POST':
        try:
            conn.execute('''
                UPDATE apolices 
                SET numero_apolice=?, cliente_id=?, seguradora_id=?, tipo_seguro_id=?,
                    valor_premio=?, valor_franquia=?, data_inicio=?, data_vencimento=?, observacoes=?
                WHERE id=?
            ''', (
                request.form['numero_apolice'],
                request.form['cliente_id'],
                request.form['seguradora_id'],
                request.form['tipo_seguro_id'],
                request.form['valor_premio'],
                request.form['valor_franquia'],
                request.form['data_inicio'],
                request.form['data_vencimento'],
                request.form.get('observacoes', ''),
                apolice_id
            ))
            conn.commit()
            flash('Apólice atualizada com sucesso!', 'success')
            return redirect(url_for('listar_apolices'))
        except Exception as e:
            flash(f'Erro ao atualizar apólice: {str(e)}', 'error')
        finally:
            conn.close()
    
    # Carregar dados para edição
    apolice = conn.execute('''
        SELECT * FROM apolices WHERE id = ?
    ''', (apolice_id,)).fetchone()
    
    if not apolice:
        flash('Apólice não encontrada!', 'error')
        return redirect(url_for('listar_apolices'))
    
    clientes = conn.execute('SELECT * FROM clientes WHERE status = "ativo" ORDER BY nome').fetchall()
    seguradoras = conn.execute('SELECT * FROM seguradoras WHERE status = "ativa" ORDER BY nome').fetchall()
    tipos_seguro = conn.execute('SELECT * FROM tipos_seguro WHERE ativo = 1 ORDER BY nome').fetchall()
    conn.close()
    
    return render_template('editar_apolice_simple.html', 
                         apolice=apolice, clientes=clientes, seguradoras=seguradoras, tipos_seguro=tipos_seguro)

# ROTAS DE SINISTROS

@app.route('/sinistros')
@require_login
def listar_sinistros():
    conn = get_db()
    sinistros = conn.execute('''
        SELECT s.*, a.numero_apolice, c.nome as cliente_nome
        FROM sinistros s
        JOIN apolices a ON s.apolice_id = a.id
        JOIN clientes c ON a.cliente_id = c.id
        ORDER BY s.data_ocorrencia DESC
    ''').fetchall()
    conn.close()
    return render_template('sinistros_simple.html', sinistros=sinistros)

@app.route('/sinistros/novo', methods=['GET', 'POST'])
@app.route('/novo_sinistro', methods=['GET', 'POST'])
@require_login
def novo_sinistro():
    conn = get_db()
    
    if request.method == 'POST':
        # Gerar protocolo automático
        protocolo = f"SIN-{datetime.now().year}-{datetime.now().strftime('%m%d%H%M')}"
        
        try:
            conn.execute('''
                INSERT INTO sinistros (protocolo, apolice_id, data_ocorrencia, data_comunicacao,
                                    tipo_sinistro, descricao, valor_estimado, valor_franquia, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                protocolo,
                request.form['apolice_id'],
                request.form['data_ocorrencia'],
                request.form['data_comunicacao'],
                request.form['tipo_sinistro'],
                request.form['descricao'],
                request.form['valor_estimado'],
                request.form['valor_franquia'],
                request.form.get('observacoes', '')
            ))
            conn.commit()
            flash(f'Sinistro cadastrado com sucesso! Protocolo: {protocolo}', 'success')
            return redirect(url_for('listar_sinistros'))
        except Exception as e:
            flash(f'Erro ao cadastrar sinistro: {str(e)}', 'error')
        finally:
            conn.close()
    
    # Carregar apólices ativas
    apolices = conn.execute('''
        SELECT a.*, c.nome as cliente_nome
        FROM apolices a
        JOIN clientes c ON a.cliente_id = c.id
        WHERE a.status = 'ativa'
        ORDER BY c.nome
    ''').fetchall()
    conn.close()
    
    return render_template('novo_sinistro_simple.html', apolices=apolices)

# ROTAS DE CONSULTAS

@app.route('/consultas')
@require_login
def consultas():
    return render_template('consultas.html')

@app.route('/consultas/cliente')
@require_login
def consulta_cliente():
    busca = request.args.get('busca_cliente', '')
    resultados = []
    
    if busca:
        conn = get_db()
        resultados = conn.execute('''
            SELECT * FROM clientes 
            WHERE nome LIKE ? OR cpf LIKE ? OR email LIKE ?
            AND status = 'ativo'
        ''', (f'%{busca}%', f'%{busca}%', f'%{busca}%')).fetchall()
        conn.close()
    
    return jsonify([dict(row) for row in resultados])

@app.route('/consultas/apolice')
@require_login
def consulta_apolice():
    numero = request.args.get('busca_apolice', '')
    resultado = None
    
    if numero:
        conn = get_db()
        resultado = conn.execute('''
            SELECT a.*, c.nome as cliente_nome, s.nome as seguradora_nome, ts.nome as tipo_seguro_nome
            FROM apolices a
            JOIN clientes c ON a.cliente_id = c.id
            JOIN seguradoras s ON a.seguradora_id = s.id
            JOIN tipos_seguro ts ON a.tipo_seguro_id = ts.id
            WHERE a.numero_apolice LIKE ?
        ''', (f'%{numero}%',)).fetchone()
        conn.close()
    
    return jsonify(dict(resultado) if resultado else {})

# ROTAS DE RELATÓRIOS

@app.route('/relatorios')
@require_login
def relatorios():
    """Dashboard de relatórios com resumo geral"""
    conn = get_db()
    
    # Estatísticas gerais
    stats = {
        'total_apolices': conn.execute('SELECT COUNT(*) as count FROM apolices').fetchone()['count'],
        'total_clientes': conn.execute('SELECT COUNT(*) as count FROM clientes').fetchone()['count'],
        'valor_total_premios': conn.execute('SELECT COALESCE(SUM(valor_premio), 0) as total FROM apolices WHERE status = "ativa"').fetchone()['total'],
        'sinistros_abertos': conn.execute('SELECT COUNT(*) as count FROM sinistros WHERE status = "aberto"').fetchone()['count']
    }
    
    conn.close()
    return render_template('relatorios_completos.html', stats=stats)

@app.route('/relatorios/vendas')
@require_login
def relatorio_vendas():
    """Relatório detalhado de vendas"""
    conn = get_db()
    
    try:
        # Dados para relatório de vendas - últimos 12 meses
        vendas_mes = conn.execute('''
            SELECT 
                strftime('%Y-%m', created_at) as mes,
                COUNT(*) as quantidade,
                COALESCE(SUM(valor_premio), 0) as valor_total
            FROM apolices 
            WHERE created_at >= DATE('now', '-12 months')
            GROUP BY strftime('%Y-%m', created_at)
            ORDER BY mes DESC
        ''').fetchall()
        
        # Top tipos de seguro - últimos 3 meses
        top_tipos = conn.execute('''
            SELECT 
                ts.nome, 
                COUNT(*) as quantidade, 
                COALESCE(SUM(a.valor_premio), 0) as valor_total,
                ROUND(AVG(a.valor_premio), 2) as valor_medio
            FROM apolices a
            JOIN tipos_seguro ts ON a.tipo_seguro_id = ts.id
            WHERE a.created_at >= DATE('now', '-3 months')
            GROUP BY ts.id, ts.nome
            ORDER BY quantidade DESC
            LIMIT 10
        ''').fetchall()
        
        # Vendas por seguradora
        vendas_seguradora = conn.execute('''
            SELECT 
                s.nome,
                COUNT(*) as quantidade,
                COALESCE(SUM(a.valor_premio), 0) as valor_total
            FROM apolices a
            JOIN seguradoras s ON a.seguradora_id = s.id
            WHERE a.created_at >= DATE('now', '-6 months')
            GROUP BY s.id, s.nome
            ORDER BY valor_total DESC
            LIMIT 5
        ''').fetchall()
        
    except Exception as e:
        print(f"ERRO no relatório de vendas: {e}")
        vendas_mes = []
        top_tipos = []
        vendas_seguradora = []
    
    conn.close()
    
    return render_template('relatorio_vendas_simple.html', 
                         vendas_mes=vendas_mes, 
                         top_tipos=top_tipos,
                         vendas_seguradora=vendas_seguradora)

@app.route('/relatorios/comissoes')
@require_login
def relatorio_comissoes():
    """Relatório de comissões e performance"""
    conn = get_db()
    
    try:
        # Dados reais de vendas por usuário (simulando corretores)
        vendas_usuario = conn.execute('''
            SELECT 
                COUNT(*) as vendas,
                COALESCE(SUM(valor_premio), 0) as valor_vendas,
                ROUND(COALESCE(SUM(valor_premio), 0) * 0.10, 2) as comissao,
                10 as percentual
            FROM apolices 
            WHERE created_at >= DATE('now', '-1 month')
        ''').fetchone()
        
        # Dados por tipo de seguro
        comissoes_tipo = conn.execute('''
            SELECT 
                ts.nome as tipo,
                COUNT(*) as vendas,
                COALESCE(SUM(a.valor_premio), 0) as valor_vendas,
                ROUND(COALESCE(SUM(a.valor_premio), 0) * 0.10, 2) as comissao
            FROM apolices a
            JOIN tipos_seguro ts ON a.tipo_seguro_id = ts.id
            WHERE a.created_at >= DATE('now', '-1 month')
            GROUP BY ts.id, ts.nome
            ORDER BY valor_vendas DESC
        ''').fetchall()
        
        # Simulação de dados de corretores individuais
        comissoes = [
            {
                'corretor': 'Maria Silva', 
                'vendas': max(1, int(vendas_usuario['vendas'] * 0.4)), 
                'valor_vendas': round(vendas_usuario['valor_vendas'] * 0.4, 2), 
                'comissao': round(vendas_usuario['comissao'] * 0.4, 2), 
                'percentual': 10
            },
            {
                'corretor': 'João Santos', 
                'vendas': max(1, int(vendas_usuario['vendas'] * 0.35)), 
                'valor_vendas': round(vendas_usuario['valor_vendas'] * 0.35, 2), 
                'comissao': round(vendas_usuario['comissao'] * 0.35, 2), 
                'percentual': 10
            },
            {
                'corretor': 'Ana Costa', 
                'vendas': max(1, int(vendas_usuario['vendas'] * 0.25)), 
                'valor_vendas': round(vendas_usuario['valor_vendas'] * 0.25, 2), 
                'comissao': round(vendas_usuario['comissao'] * 0.25, 2), 
                'percentual': 10
            }
        ]
        
    except Exception as e:
        print(f"ERRO no relatório de comissões: {e}")
        comissoes = []
        comissoes_tipo = []
    
    conn.close()
    
    return render_template('relatorio_comissoes_simple.html', 
                         comissoes=comissoes,
                         comissoes_tipo=comissoes_tipo)

@app.route('/relatorios/sinistros')
@require_login
def relatorio_sinistros():
    """Relatório de sinistros por período"""
    conn = get_db()
    
    try:
        # Sinistros por mês
        sinistros_mes = conn.execute('''
            SELECT 
                strftime('%Y-%m', data_ocorrencia) as mes,
                COUNT(*) as quantidade,
                COALESCE(SUM(valor_estimado), 0) as valor_total
            FROM sinistros 
            WHERE data_ocorrencia >= DATE('now', '-12 months')
            GROUP BY strftime('%Y-%m', data_ocorrencia)
            ORDER BY mes DESC
        ''').fetchall()
        
        # Sinistros por tipo
        sinistros_tipo = conn.execute('''
            SELECT 
                tipo_sinistro,
                COUNT(*) as quantidade,
                COALESCE(SUM(valor_estimado), 0) as valor_total,
                status
            FROM sinistros
            WHERE data_ocorrencia >= DATE('now', '-6 months')
            GROUP BY tipo_sinistro, status
            ORDER BY quantidade DESC
        ''').fetchall()
        
        # Top seguradoras com sinistros
        sinistros_seguradora = conn.execute('''
            SELECT 
                seg.nome as seguradora,
                COUNT(*) as quantidade,
                COALESCE(SUM(s.valor_estimado), 0) as valor_total
            FROM sinistros s
            JOIN apolices a ON s.apolice_id = a.id
            JOIN seguradoras seg ON a.seguradora_id = seg.id
            WHERE s.data_ocorrencia >= DATE('now', '-6 months')
            GROUP BY seg.id, seg.nome
            ORDER BY quantidade DESC
            LIMIT 5
        ''').fetchall()
        
    except Exception as e:
        print(f"ERRO no relatório de sinistros: {e}")
        sinistros_mes = []
        sinistros_tipo = []
        sinistros_seguradora = []
    
    conn.close()
    
    return render_template('relatorio_sinistros_simple.html',
                         sinistros_mes=sinistros_mes,
                         sinistros_tipo=sinistros_tipo,
                         sinistros_seguradora=sinistros_seguradora)

# ROTAS DE CONFIGURAÇÕES

@app.route('/configuracoes')
@require_login
def configuracoes():
    return render_template('configuracoes.html')

@app.route('/seguradoras')
@require_login
def listar_seguradoras():
    conn = get_db()
    seguradoras = conn.execute('SELECT * FROM seguradoras ORDER BY nome').fetchall()
    conn.close()
    return render_template('seguradoras_simple.html', seguradoras=seguradoras)

@app.route('/tipos-seguro')
@require_login
def listar_tipos_seguro():
    conn = get_db()
    tipos = conn.execute('SELECT * FROM tipos_seguro WHERE ativo = 1 ORDER BY nome').fetchall()
    conn.close()
    return render_template('tipos_seguro_simple.html', tipos=tipos)

# ROTA PARA API - Dados do Dashboard
@app.route('/api/dashboard-stats')
@require_login
def dashboard_stats():
    conn = get_db()
    
    stats = {
        'clientes_total': conn.execute('SELECT COUNT(*) as count FROM clientes WHERE status = "ativo"').fetchone()['count'],
        'apolices_ativas': conn.execute('SELECT COUNT(*) as count FROM apolices WHERE status = "ativa"').fetchone()['count'],
        'sinistros_abertos': conn.execute('SELECT COUNT(*) as count FROM sinistros WHERE status = "aberto"').fetchone()['count'],
        'renovacoes_mes': conn.execute('SELECT COUNT(*) as count FROM renovacoes WHERE status = "pendente"').fetchone()['count'],
        'vendas_mes_valor': conn.execute('SELECT COALESCE(SUM(valor_premio), 0) as total FROM apolices WHERE strftime("%Y-%m", created_at) = strftime("%Y-%m", "now")').fetchone()['total']
    }
    
    conn.close()
    return jsonify(stats)

# TRATAMENTO DE ERROS
@app.errorhandler(404)
def page_not_found(error):
    """Tratamento personalizado para erro 404"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Página Não Encontrada - Cliver Seguros</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 50px; text-align: center; }
            .error-container { max-width: 500px; margin: 0 auto; }
            .error-code { font-size: 72px; color: #00B391; margin-bottom: 20px; }
            .error-message { font-size: 18px; color: #666; margin-bottom: 30px; }
            .btn { background: #00B391; color: white; padding: 10px 20px; 
                   text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-code">404</div>
            <div class="error-message">Página não encontrada</div>
            <p>A página que você está procurando não existe.</p>
            <a href="/" class="btn">Voltar ao Início</a>
        </div>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def internal_error(error):
    """Tratamento personalizado para erro 500"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Erro Interno - Cliver Seguros</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 50px; text-align: center; }
            .error-container { max-width: 500px; margin: 0 auto; }
            .error-code { font-size: 72px; color: #dc3545; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-code">500</div>
            <h2>Erro Interno do Servidor</h2>
            <p>Ocorreu um erro interno. Tente novamente.</p>
            <a href="/" style="background: #00B391; color: white; padding: 10px 20px; 
               text-decoration: none; border-radius: 5px;">Voltar ao Início</a>
        </div>
    </body>
    </html>
    ''', 500

# Rotas com nomes específicos para templates

@app.route('/clientes_simple')
@require_login
def clientes_simple():
    return listar_clientes()

@app.route('/apolices_simple')
@require_login  
def apolices_simple():
    return listar_apolices()

@app.route('/sinistros_simple')
@require_login
def sinistros_simple():
    return listar_sinistros()

# ROTAS DE COLABORADORES

@app.route('/colaboradores')
@require_login
def listar_colaboradores():
    conn = get_db()
    colaboradores = conn.execute('''
        SELECT * FROM colaboradores 
        WHERE status = 'ativo' 
        ORDER BY nome_colaborador
    ''').fetchall()
    conn.close()
    return render_template('colaboradores_simple.html', colaboradores=colaboradores)

@app.route('/colaboradores/novo', methods=['GET', 'POST'])
@app.route('/novo_colaborador', methods=['GET', 'POST'])
@require_login
def novo_colaborador():
    if request.method == 'POST':
        nome = request.form['nome_colaborador']
        email = request.form['email_colaborador']
        telefone = request.form.get('telefone', '')
        cargo = request.form['cargo']
        salario = float(request.form.get('salario', 0))
        data_admissao = request.form.get('data_admissao')
        cpf = request.form.get('cpf', '')
        endereco = request.form.get('endereco', '')
        
        conn = get_db()
        try:
            conn.execute('''
                INSERT INTO colaboradores 
                (nome_colaborador, email_colaborador, telefone, cargo, salario, data_admissao, cpf, endereco)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, email, telefone, cargo, salario, data_admissao, cpf, endereco))
            conn.commit()
            flash('Colaborador cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_colaboradores'))
        except sqlite3.IntegrityError:
            flash('E-mail já cadastrado!', 'error')
        finally:
            conn.close()
    
    return render_template('colaborador_form_simple.html')

@app.route('/colaboradores/<int:colaborador_id>/editar', methods=['GET', 'POST'])
@app.route('/editar_colaborador/<int:colaborador_id>', methods=['GET', 'POST'])
@require_login
def editar_colaborador(colaborador_id):
    conn = get_db()
    
    if request.method == 'POST':
        nome = request.form['nome_colaborador']
        email = request.form['email_colaborador']
        telefone = request.form.get('telefone', '')
        cargo = request.form['cargo']
        salario = float(request.form.get('salario', 0))
        data_admissao = request.form.get('data_admissao')
        cpf = request.form.get('cpf', '')
        endereco = request.form.get('endereco', '')
        
        try:
            conn.execute('''
                UPDATE colaboradores SET 
                nome_colaborador=?, email_colaborador=?, telefone=?, cargo=?, 
                salario=?, data_admissao=?, cpf=?, endereco=?
                WHERE id_colaborador=?
            ''', (nome, email, telefone, cargo, salario, data_admissao, cpf, endereco, colaborador_id))
            conn.commit()
            flash('Colaborador atualizado com sucesso!', 'success')
            return redirect(url_for('listar_colaboradores'))
        except sqlite3.IntegrityError:
            flash('E-mail já cadastrado por outro colaborador!', 'error')
        finally:
            conn.close()
    
    colaborador = conn.execute('''
        SELECT * FROM colaboradores WHERE id_colaborador = ?
    ''', (colaborador_id,)).fetchone()
    conn.close()
    
    if not colaborador:
        flash('Colaborador não encontrado!', 'error')
        return redirect(url_for('listar_colaboradores'))
    
    return render_template('colaborador_form_simple.html', colaborador=colaborador)

if __name__ == '__main__':
    try:
        # Inicializar banco de dados
        print("Inicializando banco de dados...")
        init_db()
        print("Banco de dados inicializado com sucesso!")
        
        print("=" * 50)
        print("SISTEMA CLIVER SEGUROS INICIADO")
        print("=" * 50)
        print("Dashboard: http://localhost:5003/")
        print("Login: admin / admin")
        print("Sistema completo com todas as funcionalidades!")
        print("=" * 50)
        print("Pressione Ctrl+C para parar o servidor")
        print("=" * 50)
        
        # Configurar Flask para ser mais robusto
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        
        # Iniciar servidor
        app.run(debug=True, port=5003, host='0.0.0.0', threaded=True)
        
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuário.")
    except Exception as e:
        print(f"ERRO ao iniciar o servidor: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")