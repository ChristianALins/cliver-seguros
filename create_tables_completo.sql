USE CorretoraSegurosDB;
GO

BEGIN TRANSACTION;

-- Drop Tables (em ordem inversa para lidar com FKs)
IF OBJECT_ID('Tarefas', 'U') IS NOT NULL DROP TABLE Tarefas;
IF OBJECT_ID('Renovacao_Apolices', 'U') IS NOT NULL DROP TABLE Renovacao_Apolices;
IF OBJECT_ID('Sinistros', 'U') IS NOT NULL DROP TABLE Sinistros;
IF OBJECT_ID('Apolices', 'U') IS NOT NULL DROP TABLE Apolices;
IF OBJECT_ID('Colaboradores', 'U') IS NOT NULL DROP TABLE Colaboradores;
IF OBJECT_ID('Clientes', 'U') IS NOT NULL DROP TABLE Clientes;
IF OBJECT_ID('Tipos_Seguro', 'U') IS NOT NULL DROP TABLE Tipos_Seguro;
IF OBJECT_ID('Seguradoras', 'U') IS NOT NULL DROP TABLE Seguradoras;
GO

CREATE TABLE Seguradoras (
    id_seguradora INT IDENTITY(1,1) PRIMARY KEY,
    nome_seguradora VARCHAR(255) NOT NULL,
    cnpj_seguradora VARCHAR(18) UNIQUE,
    contato_seguradora VARCHAR(20),
    email_seguradora VARCHAR(255)
);
GO

CREATE TABLE Tipos_Seguro (
    id_tipo_seguro INT IDENTITY(1,1) PRIMARY KEY,
    nome_tipo_seguro VARCHAR(100) NOT NULL UNIQUE,
    descricao_tipo_seguro NVARCHAR(MAX)
);
GO

CREATE TABLE Clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo_pessoa VARCHAR(10) NOT NULL CHECK (tipo_pessoa IN ('Fisica', 'Juridica')),
    documento VARCHAR(18) UNIQUE NOT NULL,
    data_nascimento DATE,
    email VARCHAR(255),
    telefone VARCHAR(20),
    endereco VARCHAR(255),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(9),
    data_cadastro DATETIME DEFAULT GETDATE()
);
GO

CREATE TABLE Colaboradores (
    id_colaborador INT IDENTITY(1,1) PRIMARY KEY,
    nome_colaborador VARCHAR(255) NOT NULL,
    email_colaborador VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    data_contratacao DATE,
    status VARCHAR(10) DEFAULT 'Ativo' CHECK (status IN ('Ativo', 'Inativo'))
);
GO

CREATE TABLE Apolices (
    id_apolice INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_seguradora INT NOT NULL,
    id_tipo_seguro INT NOT NULL,
    id_colaborador INT NOT NULL,
    numero_apolice VARCHAR(50) UNIQUE NOT NULL,
    data_inicio_vigencia DATE NOT NULL,
    data_fim_vigencia DATE NOT NULL,
    valor_premio DECIMAL(10, 2) NOT NULL,
    percentual_comissao_seguradora DECIMAL(5, 2),
    valor_comissao_corretora AS (valor_premio * percentual_comissao_seguradora / 100) PERSISTED,
    percentual_comissao_colaborador DECIMAL(5, 2),
    valor_comissao_colaborador AS ((valor_premio * percentual_comissao_seguradora / 100) * percentual_comissao_colaborador / 100) PERSISTED,
    data_pagamento_comissao_corretora DATE,
    data_pagamento_comissao_colaborador DATE,
    status_apolice VARCHAR(20) NOT NULL DEFAULT 'Ativa' CHECK (status_apolice IN ('Ativa', 'Vencida', 'Cancelada', 'Renovada', 'Aguardando Pagamento')),
    observacoes NVARCHAR(MAX),
    CONSTRAINT FK_Apolices_Clientes FOREIGN KEY (id_cliente) REFERENCES Clientes (id_cliente) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Apolices_Seguradoras FOREIGN KEY (id_seguradora) REFERENCES Seguradoras (id_seguradora) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Apolices_TiposSeguro FOREIGN KEY (id_tipo_seguro) REFERENCES Tipos_Seguro (id_tipo_seguro) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Apolices_Colaboradores FOREIGN KEY (id_colaborador) REFERENCES Colaboradores (id_colaborador) ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

CREATE TABLE Sinistros (
    id_sinistro INT IDENTITY(1,1) PRIMARY KEY,
    id_apolice INT NOT NULL,
    data_ocorrido DATE NOT NULL,
    data_comunicacao DATETIME DEFAULT GETDATE(),
    descricao_sinistro NVARCHAR(MAX),
    status_sinistro VARCHAR(20) NOT NULL DEFAULT 'Aberto' CHECK (status_sinistro IN ('Aberto', 'Em Analise', 'Pago', 'Negado', 'Encerrado')),
    numero_processo_seguradora VARCHAR(50),
    valor_indenizacao DECIMAL(10, 2),
    observacoes NVARCHAR(MAX),
    CONSTRAINT FK_Sinistros_Apolices FOREIGN KEY (id_apolice) REFERENCES Apolices (id_apolice) ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

CREATE TABLE Renovacao_Apolices (
    id_renovacao INT IDENTITY(1,1) PRIMARY KEY,
    id_apolice_antiga INT NOT NULL,
    data_prevista_renovacao DATE NOT NULL,
    status_renovacao VARCHAR(20) NOT NULL DEFAULT 'Pendente' CHECK (status_renovacao IN ('Pendente', 'Renovada', 'Nao Renovada', 'Em Negociacao')),
    id_apolice_nova INT UNIQUE,
    observacoes NVARCHAR(MAX),
    CONSTRAINT FK_RenovacaoApolices_ApolicesAntiga FOREIGN KEY (id_apolice_antiga) REFERENCES Apolices (id_apolice) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_RenovacaoApolices_ApolicesNova FOREIGN KEY (id_apolice_nova) REFERENCES Apolices (id_apolice) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

CREATE TABLE Tarefas (
    id_tarefa INT IDENTITY(1,1) PRIMARY KEY,
    id_colaborador INT NOT NULL,
    id_apolice INT,
    id_cliente INT,
    titulo_tarefa VARCHAR(255) NOT NULL,
    descricao_tarefa NVARCHAR(MAX),
    data_criacao DATETIME DEFAULT GETDATE(),
    data_vencimento DATETIME,
    prioridade VARCHAR(10) NOT NULL DEFAULT 'Media' CHECK (prioridade IN ('Baixa', 'Media', 'Alta', 'Urgente')),
    status_tarefa VARCHAR(20) NOT NULL DEFAULT 'Pendente' CHECK (status_tarefa IN ('Pendente', 'Em Andamento', 'Concluida', 'Cancelada')),
    data_conclusao DATETIME,
    CONSTRAINT FK_Tarefas_Colaboradores FOREIGN KEY (id_colaborador) REFERENCES Colaboradores (id_colaborador) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Tarefas_Apolices FOREIGN KEY (id_apolice) REFERENCES Apolices (id_apolice) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT FK_Tarefas_Clientes FOREIGN KEY (id_cliente) REFERENCES Clientes (id_cliente) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

COMMIT TRANSACTION;
GO
