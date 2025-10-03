import sqlite3

def criar_tabela_colaboradores():
    conn = sqlite3.connect('cliver_seguros.db')
    cursor = conn.cursor()
    
    # Criar tabela colaboradores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS colaboradores (
        id_colaborador INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_colaborador TEXT NOT NULL,
        email_colaborador TEXT UNIQUE NOT NULL,
        telefone TEXT,
        cargo TEXT NOT NULL,
        salario REAL,
        data_admissao DATE,
        cpf TEXT,
        endereco TEXT,
        status TEXT DEFAULT 'ativo',
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Inserir dados de exemplo
    colaboradores_exemplo = [
        ('João Silva', 'joao.silva@cliver.com', '(11) 99999-1111', 'Corretor Senior', 5500.00, '2023-01-15', '123.456.789-01', 'Rua A, 123', 'ativo'),
        ('Maria Santos', 'maria.santos@cliver.com', '(11) 99999-2222', 'Gerente de Vendas', 8000.00, '2022-08-20', '987.654.321-02', 'Rua B, 456', 'ativo'),
        ('Pedro Costa', 'pedro.costa@cliver.com', '(11) 99999-3333', 'Analista de Sinistros', 4200.00, '2023-06-10', '456.789.123-03', 'Rua C, 789', 'ativo'),
        ('Ana Oliveira', 'ana.oliveira@cliver.com', '(11) 99999-4444', 'Assistente Administrativo', 3200.00, '2024-01-12', '321.654.987-04', 'Rua D, 321', 'ativo')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO colaboradores 
    (nome_colaborador, email_colaborador, telefone, cargo, salario, data_admissao, cpf, endereco, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', colaboradores_exemplo)
    
    conn.commit()
    conn.close()
    
    print("✅ Tabela 'colaboradores' criada com sucesso!")
    print("✅ Dados de exemplo inseridos!")

if __name__ == "__main__":
    criar_tabela_colaboradores()