# ===================================
# SISTEMA CLIVER SEGUROS - VERSÃO FINAL CORRIGIDA
# ===================================

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime, date
from functools import wraps
import os
import logging
import traceback
import sys

app = Flask(__name__)
app.secret_key = 'cliver_seguros_2025_secret_key'

# Middleware para debug de requisições
@app.before_request
def debug_request():
    print(f"\n🔍 MIDDLEWARE: {request.method} {request.url}")
    if request.method == 'POST':
        print(f"🔍 MIDDLEWARE: Form data: {dict(request.form)}")
        print(f"🔍 MIDDLEWARE: Content-Type: {request.content_type}")
    print("🔍 MIDDLEWARE: Continuando para a rota...\n")

# Configurar logging com mais detalhes
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('cliver_seguros.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuração do banco de dados SQLite
DATABASE_PATH = 'cliver_seguros.db'

def get_db_connection():
    """Estabelece conexão com o banco de dados SQLite com tratamento de erro"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        logger.debug(f"Conexão com banco estabelecida: {DATABASE_PATH}")
        return conn
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        return None

def safe_get_form_data(field_name, default_value=''):
    """Obtém dados do formulário de forma segura"""
    try:
        value = request.form.get(field_name, default_value)
        logger.debug(f"Campo '{field_name}': '{value}'")
        return value
    except Exception as e:
        logger.error(f"Erro ao obter campo {field_name}: {e}")
        return default_value

def login_required(f):
    """Decorator para verificar se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Acesso negado. Faça login primeiro.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_database():
    """Inicializa o banco de dados se não existir"""
    if not os.path.exists(DATABASE_PATH):
        logger.info("Criando banco de dados...")
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Criar tabela colaboradores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS colaboradores (
                id_colaborador INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                telefone TEXT,
                cargo TEXT NOT NULL,
                nivel_acesso TEXT NOT NULL CHECK(nivel_acesso IN ('ADMINISTRADOR', 'GERENTE', 'CORRETOR')),
                data_contratacao DATE,
                salario DECIMAL(10,2),
                percentual_comissao DECIMAL(5,2),
                ativo INTEGER DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar outras tabelas necessárias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf_cnpj TEXT UNIQUE NOT NULL,
                tipo_pessoa TEXT CHECK(tipo_pessoa IN ('F', 'J')) NOT NULL,
                email TEXT,
                telefone TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                data_nascimento DATE,
                profissao TEXT,
                renda DECIMAL(12,2),
                id_corretor INTEGER,
                observacoes TEXT,
                ativo INTEGER DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_corretor) REFERENCES colaboradores(id_colaborador)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seguradoras (
                id_seguradora INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT UNIQUE NOT NULL,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                contato_responsavel TEXT,
                percentual_comissao DECIMAL(5,2),
                observacoes TEXT,
                ativo INTEGER DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tipos_seguro (
                id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                categoria TEXT,
                ativo INTEGER DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apolices (
                id_apolice INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_apolice TEXT UNIQUE NOT NULL,
                id_cliente INTEGER NOT NULL,
                id_seguradora INTEGER NOT NULL,
                id_tipo_seguro INTEGER NOT NULL,
                valor_segurado DECIMAL(12,2) NOT NULL,
                premio DECIMAL(10,2) NOT NULL,
                data_inicio DATE NOT NULL,
                data_vencimento DATE NOT NULL,
                data_renovacao DATE,
                id_corretor INTEGER NOT NULL,
                comissao_corretor DECIMAL(8,2),
                status TEXT DEFAULT 'ATIVA' CHECK(status IN ('ATIVA', 'VENCIDA', 'CANCELADA', 'RENOVADA')),
                observacoes TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_seguradora) REFERENCES seguradoras(id_seguradora),
                FOREIGN KEY (id_tipo_seguro) REFERENCES tipos_seguro(id_tipo),
                FOREIGN KEY (id_corretor) REFERENCES colaboradores(id_colaborador)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sinistros (
                id_sinistro INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_sinistro TEXT UNIQUE NOT NULL,
                id_apolice INTEGER NOT NULL,
                data_ocorrencia DATE NOT NULL,
                data_comunicacao DATE NOT NULL,
                tipo_sinistro TEXT NOT NULL,
                descricao TEXT NOT NULL,
                valor_estimado DECIMAL(12,2),
                valor_franquia DECIMAL(10,2),
                valor_indenizacao DECIMAL(12,2),
                status TEXT DEFAULT 'ABERTO' CHECK(status IN ('ABERTO', 'EM_ANÁLISE', 'APROVADO', 'NEGADO', 'PAGO', 'FECHADO')),
                id_corretor_responsavel INTEGER,
                observacoes TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_apolice) REFERENCES apolices(id_apolice),
                FOREIGN KEY (id_corretor_responsavel) REFERENCES colaboradores(id_colaborador)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                id_tarefa INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                id_corretor_responsavel INTEGER NOT NULL,
                id_cliente INTEGER,
                id_apolice INTEGER,
                tipo_tarefa TEXT CHECK(tipo_tarefa IN ('RENOVAÇÃO', 'COBRANÇA', 'VISTORIA', 'SINISTRO', 'COMERCIAL', 'ADMINISTRATIVO')),
                prioridade TEXT DEFAULT 'MÉDIA' CHECK(prioridade IN ('BAIXA', 'MÉDIA', 'ALTA', 'URGENTE')),
                data_vencimento DATE,
                status TEXT DEFAULT 'PENDENTE' CHECK(status IN ('PENDENTE', 'EM_ANDAMENTO', 'CONCLUÍDA', 'CANCELADA')),
                observacoes TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_corretor_responsavel) REFERENCES colaboradores(id_colaborador),
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_apolice) REFERENCES apolices(id_apolice)
            )
        ''')
        
        # Inserir usuários de teste
        usuarios_teste = [
            ('Administrador Sistema', 'admin@cliver.com.br', 'admin', 'admin', '(11) 99999-9999', 'Administrador', 'ADMINISTRADOR', '2024-01-01', 15000.00, 0.00),
            ('João Silva', 'joao@cliver.com.br', 'joao', 'joao123', '(11) 98888-8888', 'Gerente Comercial', 'GERENTE', '2024-01-15', 12000.00, 2.00),
            ('Maria Santos', 'maria@cliver.com.br', 'maria', 'maria123', '(11) 97777-7777', 'Corretora Senior', 'CORRETOR', '2024-02-01', 8000.00, 5.00),
            ('Pedro Oliveira', 'pedro@cliver.com.br', 'pedro', 'pedro123', '(11) 96666-6666', 'Corretor Junior', 'CORRETOR', '2024-03-01', 6000.00, 3.00)
        ]
        
        for usuario in usuarios_teste:
            cursor.execute('''
                INSERT OR IGNORE INTO colaboradores 
                (nome, email, usuario, senha, telefone, cargo, nivel_acesso, data_contratacao, salario, percentual_comissao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', usuario)
        
        # Inserir alguns dados de teste básicos
        cursor.execute("INSERT OR IGNORE INTO tipos_seguro (nome, descricao, categoria) VALUES ('Auto', 'Seguro Automotivo', 'Veículos')")
        cursor.execute("INSERT OR IGNORE INTO tipos_seguro (nome, descricao, categoria) VALUES ('Residencial', 'Seguro Residencial', 'Imóveis')")
        cursor.execute("INSERT OR IGNORE INTO tipos_seguro (nome, descricao, categoria) VALUES ('Vida', 'Seguro de Vida', 'Pessoal')")
        
        cursor.execute("INSERT OR IGNORE INTO seguradoras (nome, cnpj, telefone, email, percentual_comissao) VALUES ('Seguradora ABC', '12.345.678/0001-90', '(11) 3333-4444', 'contato@abc.com.br', 20.00)")
        cursor.execute("INSERT OR IGNORE INTO seguradoras (nome, cnpj, telefone, email, percentual_comissao) VALUES ('Seguradora XYZ', '98.765.432/0001-10', '(11) 5555-6666', 'contato@xyz.com.br', 18.00)")
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados inicializado com sucesso!")
    else:
        logger.info("Banco de dados já existe!")

@app.route('/')
def index():
    """Página inicial - redireciona para login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login com tratamento robusto e logs detalhados"""
    
    if request.method == 'POST':
        print("\n" + "="*60)
        print("🔍 DEBUG: === INICIANDO PROCESSO DE LOGIN ===")
        print(f"🔍 DEBUG: Method: {request.method}")
        print(f"🔍 DEBUG: Content-Type: {request.content_type}")
        print(f"🔍 DEBUG: Form keys: {list(request.form.keys())}")
        print(f"🔍 DEBUG: Form data completo: {dict(request.form)}")
        
        try:
            # Obter dados do formulário de múltiplas formas
            username_en = request.form.get('username', '').strip()
            password_en = request.form.get('password', '').strip()
            username_pt = request.form.get('usuario', '').strip()
            password_pt = request.form.get('senha', '').strip()
            
            print(f"🔍 DEBUG: username (EN): '{username_en}'")
            print(f"🔍 DEBUG: password (EN): '{password_en}'")
            print(f"🔍 DEBUG: usuario (PT): '{username_pt}'")
            print(f"🔍 DEBUG: senha (PT): '{password_pt}'")
            
            # Determinar qual conjunto usar
            usuario = username_en if username_en else username_pt
            senha = password_en if password_en else password_pt
            
            print(f"🔍 DEBUG: Dados finais -> usuario: '{usuario}' | senha: '{senha}'")
            
            # Validar campos obrigatórios
            if not usuario or not senha:
                print(f"❌ DEBUG: Campos vazios detectados!")
                flash('Usuário e senha são obrigatórios', 'error')
                return render_template('login.html')
            
            print(f"✅ DEBUG: Campos validados com sucesso")
            
            # Conectar ao banco
            conn = get_db_connection()
            if not conn:
                print("❌ DEBUG: Falha na conexão com banco")
                flash('Erro de conexão com o banco de dados', 'error')
                return render_template('login.html')
            
            print(f"✅ DEBUG: Conexão com banco estabelecida")
            
            cursor = conn.cursor()
            
            # Executar query de autenticação
            query = "SELECT id_colaborador, nome, email, cargo, nivel_acesso, ativo FROM colaboradores WHERE usuario = ? AND senha = ? AND ativo = 1"
            print(f"🔍 DEBUG: Executando query com usuario='{usuario}' e senha='{senha}'")
            
            cursor.execute(query, (usuario, senha))
            user = cursor.fetchone()
            
            print(f"🔍 DEBUG: Resultado da query: {dict(user) if user else 'Nenhum usuário encontrado'}")
            
            conn.close()
            
            if user:
                # Login bem-sucedido
                print(f"✅ DEBUG: Login bem-sucedido para: {usuario}")
                
                session['user_id'] = user['id_colaborador']
                session['username'] = usuario
                session['nome'] = user['nome']
                session['email'] = user['email']
                session['cargo'] = user['cargo']
                session['nivel_acesso'] = user['nivel_acesso']
                
                print(f"✅ DEBUG: Sessão criada para: {user['nome']}")
                
                flash(f'Bem-vindo, {user["nome"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                print(f"❌ DEBUG: Login falhado - credenciais incorretas")
                flash('Usuário ou senha incorretos', 'error')
                return render_template('login.html')
                
        except Exception as e:
            print(f"❌ DEBUG: Erro no processo de login: {str(e)}")
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            flash('Erro interno no sistema', 'error')
            return render_template('login.html')
        
        finally:
            print("="*60 + "\n")
    
    # GET request ou falha no POST
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    nome = session.get('nome', 'Usuário')
    session.clear()
    flash(f'Logout realizado com sucesso, {nome}!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    try:
        conn = get_db_connection()
        if not conn:
            flash('Erro de conexão com o banco de dados', 'error')
            return redirect(url_for('login'))
        
        cursor = conn.cursor()
        
        # Estatísticas básicas
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE ativo = 1")
        total_clientes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM apolices WHERE status = 'ATIVA'")
        total_apolices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sinistros WHERE status IN ('ABERTO', 'EM_ANÁLISE')")
        sinistros_pendentes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'PENDENTE'")
        tarefas_pendentes = cursor.fetchone()[0]
        
        conn.close()
        
        estatisticas = {
            'total_clientes': total_clientes,
            'total_apolices': total_apolices,
            'sinistros_pendentes': sinistros_pendentes,
            'tarefas_pendentes': tarefas_pendentes
        }
        
        return render_template('dashboard.html', estatisticas=estatisticas)
        
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        flash('Erro ao carregar dashboard', 'error')
        return render_template('dashboard.html', estatisticas={})

@app.route('/teste')
def teste():
    """Página de teste para verificar funcionamento"""
    return f"""
    <h1>🧪 Teste CLIVER Seguros</h1>
    <p><strong>Status:</strong> Sistema funcionando!</p>
    <p><strong>Banco:</strong> {'✅ Conectado' if get_db_connection() else '❌ Erro'}</p>
    <p><strong>Sessão:</strong> {'✅ Logado' if 'user_id' in session else '❌ Não logado'}</p>
    <hr>
    <a href="/login">🔑 Login</a> | 
    <a href="/dashboard">📊 Dashboard</a> |
    <a href="/logout">🚪 Logout</a>
    """

# Rotas básicas para outras funcionalidades (mantendo compatibilidade)
@app.route('/clientes')
@login_required
def clientes():
    """Lista de clientes"""
    return render_template('clientes.html')

@app.route('/apolices')
@login_required
def apolices():
    """Lista de apólices"""
    return render_template('apolices.html')

@app.route('/sinistros')
@login_required
def sinistros():
    """Lista de sinistros"""
    return render_template('sinistros.html')

@app.route('/tarefas')
@login_required
def tarefas():
    """Lista de tarefas"""
    return render_template('tarefas.html')

@app.route('/relatorios')
@login_required
def relatorios():
    """Relatórios"""
    return render_template('relatorios.html')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SISTEMA CLIVER SEGUROS - VERSÃO CORRIGIDA")
    print("="*60)
    
    # Inicializar banco de dados
    init_database()
    
    print("\n🚀 Iniciando Sistema CLIVER Seguros...")
    print("📊 Dashboard: http://127.0.0.1:5001/dashboard")
    print("🔑 Login: http://127.0.0.1:5001/login")
    print("🧪 Teste: http://127.0.0.1:5001/teste")
    
    print("\n👥 Usuários disponíveis:")
    print("   admin/admin (Administrador)")
    print("   joao/joao123 (Gerente)")
    print("   maria/maria123 (Corretora Senior)")
    print("   pedro/pedro123 (Corretor Junior)")
    print("\n" + "="*60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)