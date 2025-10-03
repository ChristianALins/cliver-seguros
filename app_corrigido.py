# ===================================
# SISTEMA CLIVER SEGUROS - CORRIGIDO
# ===================================

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime, date
from functools import wraps
import os
import logging
import traceback

app = Flask(__name__)
app.secret_key = 'cliver_seguros_2025_secret_key'

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco de dados SQLite
DATABASE_PATH = 'cliver_seguros.db'

def get_db_connection():
    """Estabelece conexão com o banco de dados SQLite com tratamento de erro"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        return None

def safe_get_form_data(field_name, default_value=''):
    """Obter dados do formulário de forma segura"""
    try:
        value = request.form.get(field_name, default_value)
        return value.strip() if value else default_value
    except Exception as e:
        logger.error(f"Erro ao obter campo {field_name}: {e}")
        return default_value

def login_required(f):
    """Decorator para exigir login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para exigir nível administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('nivel_acesso') != 'ADMINISTRADOR':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# INICIALIZAÇÃO DO BANCO
# ============================================

def init_database():
    """Inicializa o banco de dados com tratamento robusto de erros"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Não foi possível conectar ao banco de dados")
            return False
        
        cursor = conn.cursor()
        
        # Colaboradores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS colaboradores (
                id_colaborador INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                telefone TEXT,
                cargo TEXT,
                nivel_acesso TEXT DEFAULT 'CORRETOR',
                data_contratacao DATE,
                salario DECIMAL(10,2),
                percentual_comissao DECIMAL(5,2) DEFAULT 10.00,
                ativo INTEGER DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                cpf_cnpj TEXT NOT NULL UNIQUE,
                tipo_pessoa TEXT CHECK (tipo_pessoa IN ('F', 'J')) DEFAULT 'F',
                data_nascimento DATE,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                observacoes TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1,
                id_colaborador_responsavel INTEGER,
                FOREIGN KEY (id_colaborador_responsavel) REFERENCES colaboradores(id_colaborador)
            )
        ''')
        
        # Seguradoras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seguradoras (
                id_seguradora INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT,
                telefone TEXT,
                email TEXT,
                site TEXT,
                endereco TEXT,
                contato_comercial TEXT,
                percentual_comissao_padrao DECIMAL(5,2) DEFAULT 10.00,
                ativa INTEGER DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tipos de Seguro
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tipos_seguro (
                id_tipo_seguro INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                categoria TEXT,
                comissao_minima DECIMAL(5,2) DEFAULT 5.00,
                comissao_maxima DECIMAL(5,2) DEFAULT 25.00,
                ativo INTEGER DEFAULT 1
            )
        ''')
        
        # Apólices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apolices (
                id_apolice INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_apolice TEXT NOT NULL UNIQUE,
                id_cliente INTEGER NOT NULL,
                id_seguradora INTEGER NOT NULL,
                id_tipo_seguro INTEGER NOT NULL,
                id_colaborador INTEGER NOT NULL,
                valor_premio DECIMAL(15,2) NOT NULL,
                percentual_comissao DECIMAL(5,2) NOT NULL,
                valor_comissao DECIMAL(15,2) NOT NULL,
                data_inicio_vigencia DATE NOT NULL,
                data_fim_vigencia DATE NOT NULL,
                data_emissao DATE DEFAULT CURRENT_DATE,
                status_apolice TEXT DEFAULT 'ATIVA',
                forma_pagamento TEXT,
                valor_franquia DECIMAL(15,2) DEFAULT 0,
                observacoes TEXT,
                renovacao_automatica INTEGER DEFAULT 0,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_seguradora) REFERENCES seguradoras(id_seguradora),
                FOREIGN KEY (id_tipo_seguro) REFERENCES tipos_seguro(id_tipo_seguro),
                FOREIGN KEY (id_colaborador) REFERENCES colaboradores(id_colaborador)
            )
        ''')
        
        # Sinistros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sinistros (
                id_sinistro INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_sinistro TEXT NOT NULL UNIQUE,
                id_apolice INTEGER NOT NULL,
                data_ocorrencia DATE NOT NULL,
                data_comunicacao DATE DEFAULT CURRENT_DATE,
                descricao TEXT NOT NULL,
                tipo_sinistro TEXT,
                local_ocorrencia TEXT,
                valor_reclamado DECIMAL(15,2),
                valor_indenizado DECIMAL(15,2),
                status_sinistro TEXT DEFAULT 'ABERTO',
                responsavel_analise TEXT,
                observacoes TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_apolice) REFERENCES apolices(id_apolice)
            )
        ''')
        
        # Tarefas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                id_tarefa INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                tipo_tarefa TEXT,
                id_cliente INTEGER,
                id_colaborador INTEGER NOT NULL,
                id_apolice INTEGER,
                data_vencimento DATETIME,
                data_conclusao DATETIME,
                status TEXT DEFAULT 'PENDENTE',
                prioridade TEXT DEFAULT 'MEDIA',
                resultado TEXT,
                proxima_acao TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_colaborador) REFERENCES colaboradores(id_colaborador),
                FOREIGN KEY (id_apolice) REFERENCES apolices(id_apolice)
            )
        ''')
        
        # Verificar e inserir dados iniciais
        cursor.execute("SELECT COUNT(*) FROM colaboradores")
        if cursor.fetchone()[0] == 0:
            logger.info("Inserindo dados iniciais...")
            
            # Colaboradores
            cursor.execute('''
                INSERT INTO colaboradores (nome, email, usuario, senha, cargo, nivel_acesso, percentual_comissao, ativo) VALUES
                ('Administrador Sistema', 'admin@cliver.com.br', 'admin', 'admin', 'Administrador', 'ADMINISTRADOR', 0.00, 1),
                ('João Silva', 'joao@cliver.com.br', 'joao', 'joao123', 'Gerente de Vendas', 'GERENTE', 5.00, 1),
                ('Maria Santos', 'maria@cliver.com.br', 'maria', 'maria123', 'Corretora Senior', 'CORRETOR', 12.00, 1),
                ('Pedro Oliveira', 'pedro@cliver.com.br', 'pedro', 'pedro123', 'Corretor Junior', 'CORRETOR', 10.00, 1)
            ''')
            
            # Seguradoras
            cursor.execute('''
                INSERT INTO seguradoras (nome, cnpj, telefone, email, percentual_comissao_padrao, ativa) VALUES
                ('Porto Seguro', '61.198.164/0001-60', '(11) 3003-9303', 'comercial@portoseguro.com.br', 15.00, 1),
                ('Bradesco Seguros', '92.682.038/0001-00', '(11) 4002-4002', 'vendas@bradescoseguros.com.br', 12.00, 1),
                ('SulAmérica Seguros', '01.685.053/0001-56', '(11) 4004-4004', 'comercial@sulamerica.com.br', 18.00, 1),
                ('Allianz Seguros', '61.074.175/0001-38', '(11) 2178-2178', 'parceiros@allianz.com.br', 14.00, 1),
                ('Zurich Seguros', '61.079.978/0001-83', '(11) 3004-3004', 'corretores@zurich.com.br', 16.00, 1)
            ''')
            
            # Tipos de Seguro
            cursor.execute('''
                INSERT INTO tipos_seguro (nome, descricao, categoria, comissao_minima, comissao_maxima, ativo) VALUES
                ('Seguro Auto', 'Cobertura completa para veículos automotores', 'AUTOMOVEL', 10.00, 20.00, 1),
                ('Seguro Residencial', 'Proteção para residências e condomínios', 'RESIDENCIAL', 8.00, 18.00, 1),
                ('Seguro de Vida', 'Cobertura por morte e invalidez', 'VIDA', 15.00, 30.00, 1),
                ('Seguro Empresarial', 'Proteção para empresas e estabelecimentos', 'EMPRESARIAL', 12.00, 25.00, 1),
                ('Seguro Viagem', 'Cobertura para viagens nacionais e internacionais', 'VIAGEM', 20.00, 40.00, 1),
                ('Seguro Saúde', 'Planos de assistência médica e hospitalar', 'SAUDE', 5.00, 15.00, 1)
            ''')
            
            # Clientes
            cursor.execute('''
                INSERT INTO clientes (nome_completo, cpf_cnpj, tipo_pessoa, data_nascimento, telefone, email, endereco, cidade, estado, cep, id_colaborador_responsavel, ativo) VALUES
                ('Ana Costa Silva', '123.456.789-01', 'F', '1985-03-15', '(11) 99999-1111', 'ana.silva@email.com', 'Rua das Flores, 123', 'São Paulo', 'SP', '01234-567', 3, 1),
                ('Carlos Mendes Souza', '987.654.321-02', 'F', '1978-07-22', '(11) 99999-2222', 'carlos.souza@email.com', 'Av. Paulista, 1000', 'São Paulo', 'SP', '01310-100', 3, 1),
                ('Empresa Tech LTDA', '12.345.678/0001-90', 'J', NULL, '(11) 3333-4444', 'contato@empresatech.com.br', 'Rua do Comércio, 500', 'São Paulo', 'SP', '04567-890', 4, 1),
                ('Maria Fernanda Lima', '456.789.123-03', 'F', '1990-12-08', '(11) 99999-3333', 'maria.lima@email.com', 'Rua das Palmeiras, 789', 'São Paulo', 'SP', '05678-901', 4, 1)
            ''')
            
            # Apólices
            cursor.execute('''
                INSERT INTO apolices (numero_apolice, id_cliente, id_seguradora, id_tipo_seguro, id_colaborador, valor_premio, percentual_comissao, valor_comissao, data_inicio_vigencia, data_fim_vigencia, status_apolice, forma_pagamento) VALUES
                ('APL001-2025', 1, 1, 1, 3, 2500.00, 15.00, 375.00, '2025-01-01', '2026-01-01', 'ATIVA', 'ANUAL'),
                ('APL002-2025', 2, 2, 2, 3, 1800.00, 12.00, 216.00, '2025-02-01', '2026-02-01', 'ATIVA', 'MENSAL'),
                ('APL003-2025', 3, 3, 4, 4, 8500.00, 18.00, 1530.00, '2025-03-01', '2026-03-01', 'ATIVA', 'SEMESTRAL'),
                ('APL004-2024', 4, 1, 3, 4, 1200.00, 25.00, 300.00, '2024-12-01', '2025-12-01', 'ATIVA', 'ANUAL'),
                ('APL005-2024', 1, 4, 5, 3, 450.00, 35.00, 157.50, '2024-11-15', '2025-01-15', 'VENCIDA', 'À VISTA')
            ''')
            
            # Tarefas
            cursor.execute('''
                INSERT INTO tarefas (titulo, descricao, tipo_tarefa, id_cliente, id_colaborador, id_apolice, data_vencimento, status, prioridade) VALUES
                ('Contato para renovação - Ana Costa', 'Entrar em contato com a cliente para renovação da apólice de auto', 'RENOVACAO', 1, 3, 1, '2025-11-15 14:00:00', 'PENDENTE', 'ALTA'),
                ('Follow-up proposta - Carlos Souza', 'Acompanhar proposta de seguro residencial enviada', 'FOLLOW_UP', 2, 3, NULL, '2025-10-05 10:00:00', 'PENDENTE', 'MEDIA'),
                ('Visita técnica - Empresa Tech', 'Realizar visita técnica para avaliação de risco empresarial', 'VISITA', 3, 4, 3, '2025-10-10 09:00:00', 'PENDENTE', 'ALTA'),
                ('Ligação pós-venda - Maria Lima', 'Verificar satisfação com o atendimento e serviços', 'LIGACAO', 4, 4, NULL, '2025-10-02 16:00:00', 'PENDENTE', 'BAIXA')
            ''')
            
            # Sinistros
            cursor.execute('''
                INSERT INTO sinistros (numero_sinistro, id_apolice, data_ocorrencia, descricao, tipo_sinistro, local_ocorrencia, valor_reclamado, status_sinistro) VALUES
                ('SIN001-2025', 1, '2025-09-15', 'Colisão traseira no trânsito da cidade', 'COLISAO', 'Av. Paulista com Rua Augusta - São Paulo/SP', 3500.00, 'EM_ANALISE'),
                ('SIN002-2025', 2, '2025-09-20', 'Vazamento em tubulação causou danos na residência', 'DANOS_AGUA', 'Residência do segurado', 1200.00, 'APROVADO')
            ''')
        
        conn.commit()
        logger.info("✅ Banco de dados inicializado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# ============================================
# ROTAS PRINCIPAIS
# ============================================

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login com tratamento robusto"""
    if request.method == 'POST':
        print("🔍 DEBUG: === INICIANDO PROCESSO DE LOGIN ===")
        print(f"🔍 DEBUG: Form data completo: {dict(request.form)}")
        print(f"🔍 DEBUG: Content-Type: {request.content_type}")
        print(f"🔍 DEBUG: Method: {request.method}")
        
        logger.info("=== INICIANDO PROCESSO DE LOGIN ===")
        logger.info(f"Form data completo: {dict(request.form)}")
        
        try:
            # Obter dados do formulário
            username_en = request.form.get('username', '')
            password_en = request.form.get('password', '')
            username_pt = request.form.get('usuario', '')
            password_pt = request.form.get('senha', '')
            
            print(f"🔍 DEBUG: username (EN): '{username_en}' | password (EN): '{password_en}'")
            print(f"🔍 DEBUG: usuario (PT): '{username_pt}' | senha (PT): '{password_pt}'")
            
            logger.info(f"username (EN): '{username_en}' | password (EN): '{password_en}'")
            logger.info(f"usuario (PT): '{username_pt}' | senha (PT): '{password_pt}'")
            
            # Determinar qual conjunto de dados usar
            usuario = username_en.strip() if username_en else username_pt.strip()
            senha = password_en.strip() if password_en else password_pt.strip()
            
            print(f"🔍 DEBUG: Dados finais: usuario='{usuario}', senha='{senha}'")
            logger.info(f"Dados finais: usuario='{usuario}', senha='{senha}'")
            
            if not usuario or not senha:
                print(f"🔍 DEBUG: Campos vazios detectados - usuario: '{usuario}', senha: '{senha}'")
                logger.warning(f'Login falhado - campos vazios')
                flash('Usuário e senha são obrigatórios', 'error')
                return render_template('login.html')
            
            # Conectar ao banco
            conn = get_db_connection()
            if not conn:
                logger.error("Falha na conexão com banco")
                flash('Erro de conexão com o banco de dados', 'error')
                return render_template('login.html')
            
            cursor = conn.cursor()
            
            # Buscar usuário
            logger.info(f"Executando query: SELECT * FROM colaboradores WHERE usuario='{usuario}' AND senha='{senha}' AND ativo=1")
            cursor.execute("""
                SELECT id_colaborador, nome, email, cargo, nivel_acesso, ativo
                FROM colaboradores 
                WHERE usuario = ? AND senha = ? AND ativo = 1
            """, (usuario, senha))
            
            user = cursor.fetchone()
            conn.close()
            
            logger.info(f"Resultado da query: {dict(user) if user else 'Nenhum usuário encontrado'}")
            
            if user:
                # Login bem-sucedido
                session['user_id'] = user['id_colaborador']
                session['username'] = usuario
                session['nome'] = user['nome']
                session['email'] = user['email']
                session['cargo'] = user['cargo']
                session['nivel_acesso'] = user['nivel_acesso']
                
                logger.info(f'✅ Login bem-sucedido para: {usuario} ({user["nome"]})')
                flash(f'Bem-vindo, {user["nome"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f'❌ Login falhado - usuário/senha incorretos: {usuario}')
                flash('Usuário ou senha incorretos', 'error')
                
        except Exception as e:
            logger.error(f'❌ Erro no processo de login: {str(e)}')
            import traceback
            logger.error(f'Traceback: {traceback.format_exc()}')
            flash('Erro interno no sistema', 'error')
    
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
    """Dashboard principal com tratamento de erro"""
    try:
        conn = get_db_connection()
        if not conn:
            flash('Erro de conexão com o banco de dados', 'error')
            return render_template('dashboard.html', metrics={}, atividades=[])
        
        cursor = conn.cursor()
        metrics = {}
        
        # Métricas básicas
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE ativo = 1")
        metrics['total_clientes'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM apolices WHERE status_apolice = 'ATIVA'")
        metrics['total_apolices_ativas'] = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT COUNT(*) FROM apolices 
            WHERE status_apolice = 'ATIVA' 
            AND date(data_fim_vigencia) BETWEEN date('now') AND date('now', '+30 days')
        """)
        metrics['apolices_vencimento'] = cursor.fetchone()[0] or 0
        
        # Tarefas pendentes
        if session.get('nivel_acesso') == 'ADMINISTRADOR':
            cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'PENDENTE'")
        else:
            cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'PENDENTE' AND id_colaborador = ?", 
                         (session['user_id'],))
        metrics['tarefas_pendentes'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM sinistros WHERE status_sinistro IN ('ABERTO', 'EM_ANALISE')")
        metrics['sinistros_abertos'] = cursor.fetchone()[0] or 0
        
        # Receita do mês
        cursor.execute("""
            SELECT COALESCE(SUM(valor_premio), 0) 
            FROM apolices 
            WHERE strftime('%Y-%m', data_inicio_vigencia) = strftime('%Y-%m', 'now')
            AND status_apolice = 'ATIVA'
        """)
        metrics['receita_mes'] = cursor.fetchone()[0] or 0
        
        # Comissões do mês
        cursor.execute("""
            SELECT COALESCE(SUM(valor_comissao), 0) 
            FROM apolices 
            WHERE strftime('%Y-%m', data_inicio_vigencia) = strftime('%Y-%m', 'now')
            AND status_apolice = 'ATIVA'
        """)
        metrics['comissoes_mes'] = cursor.fetchone()[0] or 0
        
        # Atividades recentes
        if session.get('nivel_acesso') == 'ADMINISTRADOR':
            cursor.execute("""
                SELECT t.titulo, t.data_vencimento, t.prioridade, 
                       c.nome_completo as cliente, col.nome as responsavel
                FROM tarefas t
                LEFT JOIN clientes c ON t.id_cliente = c.id_cliente
                LEFT JOIN colaboradores col ON t.id_colaborador = col.id_colaborador
                WHERE t.status = 'PENDENTE'
                ORDER BY t.data_vencimento ASC
                LIMIT 5
            """)
        else:
            cursor.execute("""
                SELECT t.titulo, t.data_vencimento, t.prioridade, c.nome_completo as cliente
                FROM tarefas t
                LEFT JOIN clientes c ON t.id_cliente = c.id_cliente
                WHERE t.status = 'PENDENTE' AND t.id_colaborador = ?
                ORDER BY t.data_vencimento ASC
                LIMIT 5
            """, (session['user_id'],))
        
        atividades_recentes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return render_template('dashboard.html', metrics=metrics, atividades=atividades_recentes)
        
    except Exception as e:
        logger.error(f'Erro no dashboard: {str(e)}')
        flash('Erro ao carregar dashboard', 'error')
        return render_template('dashboard.html', metrics={}, atividades=[])

# Rotas simplificadas para evitar erros
@app.route('/clientes')
@login_required
def clientes():
    """Lista de clientes"""
    try:
        conn = get_db_connection()
        if not conn:
            return render_template('clientes.html', clientes=[])
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY nome_completo LIMIT 50")
        clientes_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return render_template('clientes.html', clientes=clientes_list, search='')
    except Exception as e:
        logger.error(f'Erro na lista de clientes: {str(e)}')
        flash('Erro ao carregar clientes', 'error')
        return render_template('clientes.html', clientes=[])

@app.route('/apolices')
@login_required
def apolices():
    """Lista de apólices"""
    try:
        conn = get_db_connection()
        if not conn:
            return render_template('apolices.html', apolices=[])
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM apolices ORDER BY data_inicio_vigencia DESC LIMIT 50")
        apolices_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return render_template('apolices.html', apolices=apolices_list)
    except Exception as e:
        logger.error(f'Erro na lista de apólices: {str(e)}')
        flash('Erro ao carregar apólices', 'error')
        return render_template('apolices.html', apolices=[])

@app.route('/tarefas')
@login_required
def tarefas():
    """Lista de tarefas"""
    try:
        conn = get_db_connection()
        if not conn:
            return render_template('tarefas.html', tarefas=[])
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tarefas ORDER BY data_vencimento ASC LIMIT 50")
        tarefas_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return render_template('tarefas.html', tarefas=tarefas_list)
    except Exception as e:
        logger.error(f'Erro na lista de tarefas: {str(e)}')
        flash('Erro ao carregar tarefas', 'error')
        return render_template('tarefas.html', tarefas=[])

@app.route('/sinistros')
@login_required
def sinistros():
    """Lista de sinistros"""
    try:
        conn = get_db_connection()
        if not conn:
            return render_template('sinistros.html', sinistros=[])
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sinistros ORDER BY data_ocorrencia DESC LIMIT 50")
        sinistros_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return render_template('sinistros.html', sinistros=sinistros_list)
    except Exception as e:
        logger.error(f'Erro na lista de sinistros: {str(e)}')
        flash('Erro ao carregar sinistros', 'error')
        return render_template('sinistros.html', sinistros=[])

@app.route('/seguradoras')
@login_required
def seguradoras():
    """Lista de seguradoras"""
    try:
        conn = get_db_connection()
        if not conn:
            return render_template('seguradoras.html', seguradoras=[])
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM seguradoras ORDER BY nome")
        seguradoras_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return render_template('seguradoras.html', seguradoras=seguradoras_list)
    except Exception as e:
        logger.error(f'Erro na lista de seguradoras: {str(e)}')
        return render_template('seguradoras.html', seguradoras=[])

@app.route('/relatorios')
@login_required
def relatorios():
    """Página de relatórios"""
    return render_template('relatorios.html')

@app.route('/teste')
def teste():
    """Rota de teste"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM colaboradores")
            total = cursor.fetchone()[0]
            conn.close()
            return jsonify({'status': 'OK', 'colaboradores': total, 'timestamp': datetime.now().isoformat()})
        return jsonify({'status': 'ERROR', 'message': 'Sem conexão com banco'})
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': str(e)})

# ============================================
# TRATAMENTO DE ERROS
# ============================================

@app.errorhandler(404)
def not_found_error(error):
    """Página não encontrada"""
    flash('Página não encontrada', 'warning')
    return redirect(url_for('dashboard'))

@app.errorhandler(500)
def internal_error(error):
    """Erro interno do servidor"""
    logger.error(f'Erro 500: {str(error)}')
    flash('Erro interno do servidor', 'error')
    return redirect(url_for('dashboard'))

@app.errorhandler(Exception)
def handle_exception(e):
    """Tratamento geral de exceções"""
    tb = traceback.format_exc()
    logger.error(f'Erro não tratado: {str(e)}\n{tb}')
    
    if app.debug:
        return f"<h1>Erro de Debug:</h1><pre>{tb}</pre>", 500
    
    flash('Ocorreu um erro inesperado. Tente novamente.', 'error')
    return redirect(url_for('login'))

# ============================================
# FILTROS TEMPLATE
# ============================================

def format_currency(value):
    """Formatar como moeda"""
    if value is None:
        return "R$ 0,00"
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def format_date(date_value):
    """Formatar data"""
    if not date_value:
        return ''
    try:
        if isinstance(date_value, str):
            date_value = datetime.strptime(date_value, '%Y-%m-%d')
        return date_value.strftime('%d/%m/%Y')
    except:
        return str(date_value)

app.jinja_env.filters['currency'] = format_currency
app.jinja_env.filters['date'] = format_date

# ============================================
# INICIALIZAÇÃO
# ============================================

if __name__ == '__main__':
    if init_database():
        print("🚀 Iniciando Sistema CLIVER Seguros...")
        print("📊 Dashboard: http://127.0.0.1:5000/dashboard")
        print("🔑 Login: http://127.0.0.1:5000/login")
        print("🧪 Teste: http://127.0.0.1:5000/teste")
        print("")
        print("👥 Usuários disponíveis:")
        print("   admin/admin (Administrador)")
        print("   joao/joao123 (Gerente)")
        print("   maria/maria123 (Corretora Senior)")
        print("   pedro/pedro123 (Corretor Junior)")
        print("")
        
        try:
            app.run(debug=True, host='0.0.0.0', port=5000)
        except Exception as e:
            logger.error(f'Erro ao iniciar servidor: {e}')
            print(f"❌ Erro ao iniciar servidor: {e}")
    else:
        print("❌ Erro ao inicializar o banco de dados!")