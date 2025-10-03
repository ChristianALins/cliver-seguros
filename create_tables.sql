-- Criação das tabelas do sistema CorretoraDB
USE CorretoraDB;
GO

CREATE TABLE Clientes (
    id_cliente INT PRIMARY KEY IDENTITY(1,1),
    nome NVARCHAR(100) NOT NULL,
    tipo_pessoa NVARCHAR(20) NOT NULL,
    documento NVARCHAR(30) NOT NULL UNIQUE,
    data_nascimento DATE,
    email NVARCHAR(100),
    telefone NVARCHAR(30),
    endereco NVARCHAR(200),
    cidade NVARCHAR(50),
    estado NVARCHAR(2),
    cep NVARCHAR(10),
    data_cadastro DATETIME DEFAULT GETDATE()
);

CREATE TABLE Seguradoras (
    id_seguradora INT PRIMARY KEY IDENTITY(1,1),
    nome_seguradora NVARCHAR(100) NOT NULL,
    cnpj_seguradora NVARCHAR(20) NOT NULL UNIQUE,
    contato_seguradora NVARCHAR(100),
    email_seguradora NVARCHAR(100)
);

CREATE TABLE Tipos_Seguro (
    id_tipo_seguro INT PRIMARY KEY IDENTITY(1,1),
    nome_tipo_seguro NVARCHAR(100) NOT NULL UNIQUE,
    descricao_tipo_seguro TEXT
);

CREATE TABLE Colaboradores (
    id_colaborador INT PRIMARY KEY IDENTITY(1,1),
    nome_colaborador NVARCHAR(100) NOT NULL,
    email_colaborador NVARCHAR(100) NOT NULL UNIQUE,
    senha NVARCHAR(255) NOT NULL,
    cargo NVARCHAR(50),
    data_contratacao DATE,
    status NVARCHAR(20)
);

CREATE TABLE Apolices (
    id_apolice INT PRIMARY KEY IDENTITY(1,1),
    id_cliente INT NOT NULL,
    id_seguradora INT NOT NULL,
    id_tipo_seguro INT NOT NULL,
    id_colaborador INT NOT NULL,
    numero_apolice NVARCHAR(50) NOT NULL UNIQUE,
    data_inicio_vigencia DATE,
    data_fim_vigencia DATE,
    valor_premio DECIMAL(18,2),
    percentual_comissao_seguradora DECIMAL(5,2),
    valor_comissao_corretora AS (valor_premio * percentual_comissao_seguradora / 100),
    percentual_comissao_colaborador DECIMAL(5,2),
    valor_comissao_colaborador AS (valor_premio * percentual_comissao_colaborador / 100),
    data_pagamento_comissao_corretora DATE,
    data_pagamento_comissao_colaborador DATE,
    status_apolice NVARCHAR(20),
    observacoes TEXT,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY (id_seguradora) REFERENCES Seguradoras(id_seguradora),
    FOREIGN KEY (id_tipo_seguro) REFERENCES Tipos_Seguro(id_tipo_seguro),
    FOREIGN KEY (id_colaborador) REFERENCES Colaboradores(id_colaborador)
);

CREATE TABLE Sinistros (
    id_sinistro INT PRIMARY KEY IDENTITY(1,1),
    id_apolice INT NOT NULL,
    data_ocorrido DATE,
    data_comunicacao DATETIME,
    descricao_sinistro TEXT,
    status_sinistro NVARCHAR(20),
    numero_processo_seguradora NVARCHAR(50),
    valor_indenizacao DECIMAL(18,2),
    observacoes TEXT,
    FOREIGN KEY (id_apolice) REFERENCES Apolices(id_apolice)
);

CREATE TABLE Renovacao_Apolices (
    id_renovacao INT PRIMARY KEY IDENTITY(1,1),
    id_apolice_antiga INT NOT NULL,
    data_prevista_renovacao DATE,
    status_renovacao NVARCHAR(20),
    id_apolice_nova INT UNIQUE,
    observacoes TEXT,
    FOREIGN KEY (id_apolice_antiga) REFERENCES Apolices(id_apolice),
    FOREIGN KEY (id_apolice_nova) REFERENCES Apolices(id_apolice)
);

CREATE TABLE Tarefas (
    id_tarefa INT PRIMARY KEY IDENTITY(1,1),
    id_colaborador INT NOT NULL,
    id_apolice INT,
    id_cliente INT,
    titulo_tarefa NVARCHAR(100) NOT NULL,
    descricao_tarefa TEXT,
    data_criacao DATETIME DEFAULT GETDATE(),
    data_vencimento DATETIME,
    prioridade NVARCHAR(20),
    status_tarefa NVARCHAR(20),
    data_conclusao DATETIME,
    FOREIGN KEY (id_colaborador) REFERENCES Colaboradores(id_colaborador),
    FOREIGN KEY (id_apolice) REFERENCES Apolices(id_apolice),
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
);
