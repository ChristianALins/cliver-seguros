-- Criação do banco de dados
CREATE DATABASE CorretoraDB;
GO
USE CorretoraDB;
GO
-- Criação da tabela de usuários
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL -- 'master' ou 'user'
);
GO
-- Inserção dos usuários master e user para teste
INSERT INTO users (username, password, role) VALUES ('master', 'master123', 'master');
INSERT INTO users (username, password, role) VALUES ('user', 'user123', 'user');
GO
