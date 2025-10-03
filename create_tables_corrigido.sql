USE CorretoraSegurosDB;
GO

-- ============================================================================
-- ESTRUTURA CORRIGIDA CONFORME REQUISITOS ESPECIFICADOS
-- Sistema de Corretora de Seguros - Versão Normalizada
-- ============================================================================

BEGIN TRANSACTION;

-- Drop das tabelas em ordem reversa (respeitando FKs)
IF OBJECT_ID('Pagamentos', 'U') IS NOT NULL DROP TABLE Pagamentos;
IF OBJECT_ID('Sinistros', 'U') IS NOT NULL DROP TABLE Sinistros;
IF OBJECT_ID('Apolice_Produtos', 'U') IS NOT NULL DROP TABLE Apolice_Produtos;
IF OBJECT_ID('Proposta_Produtos', 'U') IS NOT NULL DROP TABLE Proposta_Produtos;
IF OBJECT_ID('Apolices', 'U') IS NOT NULL DROP TABLE Apolices;
IF OBJECT_ID('Propostas', 'U') IS NOT NULL DROP TABLE Propostas;
IF OBJECT_ID('Produtos', 'U') IS NOT NULL DROP TABLE Produtos;
IF OBJECT_ID('Tarefas', 'U') IS NOT NULL DROP TABLE Tarefas;
IF OBJECT_ID('Renovacao_Apolices', 'U') IS NOT NULL DROP TABLE Renovacao_Apolices;
IF OBJECT_ID('Colaboradores', 'U') IS NOT NULL DROP TABLE Colaboradores;
IF OBJECT_ID('Clientes', 'U') IS NOT NULL DROP TABLE Clientes;
IF OBJECT_ID('Seguradoras', 'U') IS NOT NULL DROP TABLE Seguradoras;
GO

-- ============================================================================
-- 1. TABELA SEGURADORAS (Expandida conforme requisitos)
-- ============================================================================
CREATE TABLE Seguradoras (
    id_seguradora INT IDENTITY(1,1) PRIMARY KEY,
    nome_seguradora VARCHAR(255) NOT NULL,
    cnpj_seguradora VARCHAR(18) UNIQUE,
    contato_principal VARCHAR(100),
    telefone_seguradora VARCHAR(20),
    email_seguradora VARCHAR(255),
    endereco_seguradora VARCHAR(500),
    especialidades NVARCHAR(MAX), -- vida, auto, residencial, empresarial, etc.
    condicoes_pagamento NVARCHAR(500), -- 30/60/90 dias, À vista, etc.
    status_seguradora VARCHAR(10) DEFAULT 'Ativa' CHECK (status_seguradora IN ('Ativa', 'Inativa')),
    data_cadastro DATETIME DEFAULT GETDATE(),
    observacoes NVARCHAR(MAX)
);
GO

-- ============================================================================
-- 2. TABELA CLIENTES (Expandida com histórico de seguros via relacionamentos)
-- ============================================================================
CREATE TABLE Clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo_pessoa VARCHAR(10) NOT NULL CHECK (tipo_pessoa IN ('Fisica', 'Juridica')),
    cpf_cnpj VARCHAR(18) UNIQUE NOT NULL, -- Renomeado para ficar mais claro
    data_nascimento DATE,
    email VARCHAR(255),
    telefone VARCHAR(20),
    celular VARCHAR(20),
    endereco VARCHAR(255),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(9),
    profissao VARCHAR(100), -- Para pessoa física
    renda_mensal DECIMAL(10,2), -- Para análise de risco
    data_cadastro DATETIME DEFAULT GETDATE(),
    status_cliente VARCHAR(10) DEFAULT 'Ativo' CHECK (status_cliente IN ('Ativo', 'Inativo', 'Suspenso')),
    observacoes NVARCHAR(MAX)
);
GO

-- ============================================================================
-- 3. TABELA PRODUTOS (Nova - Requisito essencial)
-- ============================================================================
CREATE TABLE Produtos (
    id_produto INT IDENTITY(1,1) PRIMARY KEY,
    id_seguradora INT NOT NULL,
    nome_produto VARCHAR(255) NOT NULL,
    tipo_seguro VARCHAR(50) NOT NULL CHECK (tipo_seguro IN ('Vida', 'Auto', 'Residencial', 'Empresarial', 'Saude', 'Viagem', 'Outros')),
    cobertura NVARCHAR(MAX) NOT NULL, -- Detalhes da cobertura
    valor_minimo DECIMAL(12,2),
    valor_maximo DECIMAL(12,2),
    franquia DECIMAL(10,2), -- Valor da franquia
    percentual_comissao DECIMAL(5,2) DEFAULT 0,
    idade_minima INT,
    idade_maxima INT,
    status_produto VARCHAR(10) DEFAULT 'Ativo' CHECK (status_produto IN ('Ativo', 'Inativo', 'Descontinuado')),
    data_lancamento DATE DEFAULT GETDATE(),
    observacoes NVARCHAR(MAX),
    
    -- FK para Seguradora
    CONSTRAINT FK_Produtos_Seguradoras 
        FOREIGN KEY (id_seguradora) REFERENCES Seguradoras (id_seguradora) 
        ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

-- ============================================================================
-- 4. TABELA COLABORADORES
-- ============================================================================
CREATE TABLE Colaboradores (
    id_colaborador INT IDENTITY(1,1) PRIMARY KEY,
    nome_colaborador VARCHAR(255) NOT NULL,
    email_colaborador VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    telefone VARCHAR(20),
    percentual_comissao DECIMAL(5,2) DEFAULT 0,
    data_contratacao DATE,
    status VARCHAR(10) DEFAULT 'Ativo' CHECK (status IN ('Ativo', 'Inativo', 'Licenca')),
    observacoes NVARCHAR(MAX)
);
GO

-- ============================================================================
-- 5. TABELA PROPOSTAS (Nova - Requisito essencial)
-- ============================================================================
CREATE TABLE Propostas (
    id_proposta INT IDENTITY(1,1) PRIMARY KEY,
    numero_proposta VARCHAR(50) UNIQUE NOT NULL,
    id_cliente INT NOT NULL,
    id_colaborador INT NOT NULL,
    id_seguradora INT NOT NULL,
    data_proposta DATE NOT NULL DEFAULT GETDATE(),
    valor_total DECIMAL(12,2) NOT NULL,
    status_proposta VARCHAR(20) NOT NULL DEFAULT 'Pendente' 
        CHECK (status_proposta IN ('Pendente', 'Em Analise', 'Aprovada', 'Rejeitada', 'Cancelada')),
    data_resposta DATE,
    motivo_rejeicao NVARCHAR(500),
    validade_proposta DATE, -- Data até quando a proposta é válida
    observacoes NVARCHAR(MAX),
    
    -- Foreign Keys
    CONSTRAINT FK_Propostas_Clientes 
        FOREIGN KEY (id_cliente) REFERENCES Clientes (id_cliente) 
        ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Propostas_Colaboradores 
        FOREIGN KEY (id_colaborador) REFERENCES Colaboradores (id_colaborador) 
        ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Propostas_Seguradoras 
        FOREIGN KEY (id_seguradora) REFERENCES Seguradoras (id_seguradora) 
        ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

-- ============================================================================
-- 6. TABELA PROPOSTA_PRODUTOS (Relacionamento M:N - Requisito)
-- ============================================================================
CREATE TABLE Proposta_Produtos (
    id_proposta_produto INT IDENTITY(1,1) PRIMARY KEY,
    id_proposta INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT DEFAULT 1,
    valor_unitario DECIMAL(12,2) NOT NULL,
    valor_total DECIMAL(12,2) NOT NULL,
    observacoes NVARCHAR(500),
    
    -- Foreign Keys
    CONSTRAINT FK_PropostaProdutos_Propostas 
        FOREIGN KEY (id_proposta) REFERENCES Propostas (id_proposta) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_PropostaProdutos_Produtos 
        FOREIGN KEY (id_produto) REFERENCES Produtos (id_produto) 
        ON DELETE NO ACTION ON UPDATE CASCADE,
        
    -- Índice único para evitar duplicatas
    CONSTRAINT UK_Proposta_Produto UNIQUE (id_proposta, id_produto)
);
GO

-- ============================================================================
-- 7. TABELA APOLICES (Ajustada conforme requisitos)
-- ============================================================================
CREATE TABLE Apolices (
    id_apolice INT IDENTITY(1,1) PRIMARY KEY,
    numero_apolice VARCHAR(50) UNIQUE NOT NULL,
    id_proposta INT, -- Relacionamento com proposta (opcional para apólices antigas)
    id_cliente INT NOT NULL,
    id_seguradora INT NOT NULL,
    id_colaborador INT NOT NULL,
    data_emissao DATE NOT NULL DEFAULT GETDATE(),
    data_inicio_vigencia DATE NOT NULL,
    data_fim_vigencia DATE NOT NULL,
    valor_total DECIMAL(12,2) NOT NULL,
    percentual_comissao_seguradora DECIMAL(5,2),
    valor_comissao_corretora AS (valor_total * percentual_comissao_seguradora / 100) PERSISTED,
    percentual_comissao_colaborador DECIMAL(5,2),
    valor_comissao_colaborador AS ((valor_total * percentual_comissao_seguradora / 100) * percentual_comissao_colaborador / 100) PERSISTED,
    status_apolice VARCHAR(20) NOT NULL DEFAULT 'Ativa' 
        CHECK (status_apolice IN ('Ativa', 'Vencida', 'Cancelada', 'Renovada', 'Suspensa')),
    data_pagamento_comissao_corretora DATE,
    data_pagamento_comissao_colaborador DATE,
    observacoes NVARCHAR(MAX),
    
    -- Foreign Keys
    CONSTRAINT FK_Apolices_Propostas 
        FOREIGN KEY (id_proposta) REFERENCES Propostas (id_proposta) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT FK_Apolices_Clientes 
        FOREIGN KEY (id_cliente) REFERENCES Clientes (id_cliente) 
        ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Apolices_Seguradoras 
        FOREIGN KEY (id_seguradora) REFERENCES Seguradoras (id_seguradora) 
        ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Apolices_Colaboradores 
        FOREIGN KEY (id_colaborador) REFERENCES Colaboradores (id_colaborador) 
        ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

-- ============================================================================
-- 8. TABELA APOLICE_PRODUTOS (Relacionamento M:N - Requisito)
-- ============================================================================
CREATE TABLE Apolice_Produtos (
    id_apolice_produto INT IDENTITY(1,1) PRIMARY KEY,
    id_apolice INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT DEFAULT 1,
    valor_unitario DECIMAL(12,2) NOT NULL,
    valor_total DECIMAL(12,2) NOT NULL,
    franquia_aplicada DECIMAL(10,2),
    cobertura_especifica NVARCHAR(MAX), -- Coberturas específicas desta apólice/produto
    observacoes NVARCHAR(500),
    
    -- Foreign Keys
    CONSTRAINT FK_ApolicesProdutos_Apolices 
        FOREIGN KEY (id_apolice) REFERENCES Apolices (id_apolice) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_ApolicesProdutos_Produtos 
        FOREIGN KEY (id_produto) REFERENCES Produtos (id_produto) 
        ON DELETE NO ACTION ON UPDATE CASCADE,
        
    -- Índice único para evitar duplicatas
    CONSTRAINT UK_Apolice_Produto UNIQUE (id_apolice, id_produto)
);
GO

-- ============================================================================
-- 9. TABELA PAGAMENTOS (Nova - Requisito essencial)
-- ============================================================================
CREATE TABLE Pagamentos (
    id_pagamento INT IDENTITY(1,1) PRIMARY KEY,
    id_apolice INT NOT NULL,
    numero_parcela INT NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    valor_parcela DECIMAL(10,2) NOT NULL,
    valor_pago DECIMAL(10,2),
    forma_pagamento VARCHAR(50) CHECK (forma_pagamento IN ('Boleto', 'Cartao Credito', 'Cartao Debito', 'PIX', 'Transferencia', 'Dinheiro')),
    status_pagamento VARCHAR(20) DEFAULT 'Pendente' 
        CHECK (status_pagamento IN ('Pendente', 'Pago', 'Vencido', 'Cancelado', 'Estornado')),
    juros_aplicados DECIMAL(8,2) DEFAULT 0,
    desconto_aplicado DECIMAL(8,2) DEFAULT 0,
    observacoes NVARCHAR(500),
    data_criacao DATETIME DEFAULT GETDATE(),
    
    -- Foreign Key
    CONSTRAINT FK_Pagamentos_Apolices 
        FOREIGN KEY (id_apolice) REFERENCES Apolices (id_apolice) 
        ON DELETE CASCADE ON UPDATE CASCADE
);
GO

-- ============================================================================
-- 10. TABELA SINISTROS (Ajustada conforme requisitos)
-- ============================================================================
CREATE TABLE Sinistros (
    id_sinistro INT IDENTITY(1,1) PRIMARY KEY,
    numero_sinistro VARCHAR(50) UNIQUE NOT NULL, -- Requisito: número do sinistro
    id_apolice INT NOT NULL,
    data_ocorrido DATE NOT NULL,
    data_comunicacao DATETIME DEFAULT GETDATE(),
    descricao_sinistro NVARCHAR(MAX) NOT NULL,
    valor_sinistro DECIMAL(12,2),
    valor_franquia DECIMAL(10,2),
    valor_indenizacao DECIMAL(12,2),
    status_sinistro VARCHAR(20) NOT NULL DEFAULT 'Em Analise' 
        CHECK (status_sinistro IN ('Aberto', 'Em Analise', 'Aprovado', 'Pago', 'Negado', 'Encerrado')),
    numero_processo_seguradora VARCHAR(50),
    data_fechamento DATE,
    motivo_negativa NVARCHAR(500),
    observacoes NVARCHAR(MAX),
    
    -- Foreign Key
    CONSTRAINT FK_Sinistros_Apolices 
        FOREIGN KEY (id_apolice) REFERENCES Apolices (id_apolice) 
        ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

-- ============================================================================
-- 11. TABELA TAREFAS (Mantida com ajustes)
-- ============================================================================
CREATE TABLE Tarefas (
    id_tarefa INT IDENTITY(1,1) PRIMARY KEY,
    id_colaborador INT NOT NULL,
    id_apolice INT,
    id_cliente INT,
    id_proposta INT, -- Nova relação com propostas
    titulo_tarefa VARCHAR(255) NOT NULL,
    descricao_tarefa NVARCHAR(MAX),
    data_criacao DATETIME DEFAULT GETDATE(),
    data_vencimento DATETIME,
    prioridade VARCHAR(10) NOT NULL DEFAULT 'Media' 
        CHECK (prioridade IN ('Baixa', 'Media', 'Alta', 'Urgente')),
    status_tarefa VARCHAR(20) NOT NULL DEFAULT 'Pendente' 
        CHECK (status_tarefa IN ('Pendente', 'Em Andamento', 'Concluida', 'Cancelada')),
    data_conclusao DATETIME,
    
    -- Foreign Keys
    CONSTRAINT FK_Tarefas_Colaboradores 
        FOREIGN KEY (id_colaborador) REFERENCES Colaboradores (id_colaborador) 
        ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Tarefas_Apolices 
        FOREIGN KEY (id_apolice) REFERENCES Apolices (id_apolice) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT FK_Tarefas_Clientes 
        FOREIGN KEY (id_cliente) REFERENCES Clientes (id_cliente) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT FK_Tarefas_Propostas 
        FOREIGN KEY (id_proposta) REFERENCES Propostas (id_proposta) 
        ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- ============================================================================
-- 12. TABELA RENOVACAO_APOLICES (Mantida com ajustes)
-- ============================================================================
CREATE TABLE Renovacao_Apolices (
    id_renovacao INT IDENTITY(1,1) PRIMARY KEY,
    id_apolice_antiga INT NOT NULL,
    data_prevista_renovacao DATE NOT NULL,
    status_renovacao VARCHAR(20) NOT NULL DEFAULT 'Pendente' 
        CHECK (status_renovacao IN ('Pendente', 'Renovada', 'Nao Renovada', 'Em Negociacao')),
    id_apolice_nova INT UNIQUE,
    valor_nova_apolice DECIMAL(12,2),
    observacoes NVARCHAR(MAX),
    
    -- Foreign Keys
    CONSTRAINT FK_RenovacaoApolices_ApolicesAntiga 
        FOREIGN KEY (id_apolice_antiga) REFERENCES Apolices (id_apolice) 
        ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_RenovacaoApolices_ApolicesNova 
        FOREIGN KEY (id_apolice_nova) REFERENCES Apolices (id_apolice) 
        ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- ============================================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================================

-- Índices para consultas frequentes
CREATE INDEX IX_Clientes_CPF_CNPJ ON Clientes(cpf_cnpj);
CREATE INDEX IX_Clientes_Nome ON Clientes(nome);
CREATE INDEX IX_Apolices_Cliente ON Apolices(id_cliente);
CREATE INDEX IX_Apolices_Seguradora ON Apolices(id_seguradora);
CREATE INDEX IX_Apolices_DataVigencia ON Apolices(data_inicio_vigencia, data_fim_vigencia);
CREATE INDEX IX_Propostas_Cliente ON Propostas(id_cliente);
CREATE INDEX IX_Propostas_Status ON Propostas(status_proposta);
CREATE INDEX IX_Pagamentos_Vencimento ON Pagamentos(data_vencimento);
CREATE INDEX IX_Pagamentos_Status ON Pagamentos(status_pagamento);
CREATE INDEX IX_Sinistros_Apolice ON Sinistros(id_apolice);
CREATE INDEX IX_Sinistros_Status ON Sinistros(status_sinistro);

COMMIT TRANSACTION;
GO

-- ============================================================================
-- INSERÇÃO DE DADOS DE EXEMPLO (OPCIONAL)
-- ============================================================================

-- Inserir algumas seguradoras de exemplo
INSERT INTO Seguradoras (nome_seguradora, cnpj_seguradora, contato_principal, telefone_seguradora, email_seguradora, especialidades, condicoes_pagamento) VALUES
('Seguradora Alpha', '11.222.333/0001-44', 'João Silva', '(11) 1234-5678', 'contato@alpha.com.br', 'Vida, Auto, Residencial', '30/60/90 dias'),
('Beta Seguros', '22.333.444/0001-55', 'Maria Santos', '(21) 2345-6789', 'vendas@beta.com.br', 'Empresarial, Saúde', 'À vista, 30 dias'),
('Gamma Proteção', '33.444.555/0001-66', 'Carlos Lima', '(31) 3456-7890', 'comercial@gamma.com.br', 'Auto, Viagem', 'Cartão, À vista');

-- Inserir alguns produtos de exemplo
INSERT INTO Produtos (id_seguradora, nome_produto, tipo_seguro, cobertura, valor_minimo, valor_maximo, franquia, percentual_comissao) VALUES
(1, 'Vida Individual', 'Vida', 'Morte natural e acidental, Invalidez permanente', 50000.00, 1000000.00, 0.00, 15.00),
(1, 'Auto Premium', 'Auto', 'Casco, Terceiros, Roubo e Furto, Assistência 24h', 20000.00, 200000.00, 2000.00, 20.00),
(2, 'Residencial Completo', 'Residencial', 'Incêndio, Roubo, Danos Elétricos, Responsabilidade Civil', 100000.00, 2000000.00, 1000.00, 18.00);

-- Inserir colaborador de exemplo
INSERT INTO Colaboradores (nome_colaborador, email_colaborador, senha, cargo, telefone, percentual_comissao) VALUES
('Admin Sistema', 'admin@cliver.com.br', 'admin123', 'Administrador', '(11) 9999-9999', 0.00),
('Corretor Demo', 'demo@cliver.com.br', 'demo123', 'Corretor Senior', '(11) 8888-8888', 50.00);

PRINT 'Estrutura de banco de dados criada com sucesso!';
PRINT 'Requisitos implementados:';
PRINT '✓ Entidades: Clientes, Seguradoras, Produtos, Propostas, Apólices, Pagamentos, Sinistros';
PRINT '✓ Relacionamentos M:N: Proposta_Produtos, Apolice_Produtos';
PRINT '✓ Chaves primárias e estrangeiras com integridade referencial';
PRINT '✓ Normalização adequada e índices para performance';

GO