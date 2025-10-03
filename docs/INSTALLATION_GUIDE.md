# 🚀 Guia de Instalação Completa

## 📋 Pré-requisitos

### Software Obrigatório

#### 1. Python 3.11+
- **Download**: https://python.org/downloads/
- **Instalação**: 
  - ✅ Marque "Add Python to PATH"
  - ✅ Marque "Install for all users"
- **Verificação**: `python --version`

#### 2. Microsoft SQL Server
**Opção A - SQL Server Developer (Recomendado)**
- **Download**: https://www.microsoft.com/sql-server/sql-server-downloads
- **Tamanho**: ~1.5GB
- **Recursos**: Completo, ideal para desenvolvimento

**Opção B - SQL Server Express (Básico)**
- **Download**: https://www.microsoft.com/sql-server/sql-server-editions-express
- **Tamanho**: ~200MB  
- **Limitações**: 10GB por banco, 1GB RAM

#### 3. SQL Server Management Studio (SSMS)
- **Download**: https://docs.microsoft.com/sql/ssms/download-sql-server-management-studio-ssms
- **Tamanho**: ~600MB
- **Necessário**: Para executar scripts SQL

#### 4. ODBC Driver 17 for SQL Server
- **Download**: https://www.microsoft.com/download/details.aspx?id=56567
- **Necessário**: Para conexão Python → SQL Server

---

## 🔧 Instalação Passo a Passo

### Etapa 1: Configurar Python

```bash
# 1. Verificar instalação
python --version
pip --version

# 2. Atualizar pip (recomendado)
python -m pip install --upgrade pip

# 3. Verificar se está funcionando
python -c "import sys; print(sys.version)"
```

### Etapa 2: Configurar SQL Server

#### Instalação do SQL Server
1. **Execute o instalador** do SQL Server
2. **Escolha**: "Instalação personalizada"
3. **Recursos mínimos necessários**:
   - ✅ Serviços do Mecanismo de Banco de Dados
   - ✅ SQL Server Replication (opcional)
4. **Configuração da Instância**:
   - Nome da instância: `MSSQLSERVER` (padrão)
   - Ou nome personalizado (anotar para config)
5. **Configuração de Autenticação**:
   - ✅ **Modo Misto** (SQL Server e Windows)
   - Defina senha do usuário `sa`
   - ✅ Adicione usuário Windows atual como admin

#### Verificação
```cmd
# Testar conectividade
sqlcmd -S localhost -E
# Se conectar, digite: SELECT @@VERSION
# Digite: GO
# Pressione Enter
# Digite: EXIT
```

### Etapa 3: Instalar SSMS

1. **Download** e execute o instalador
2. **Instalação padrão** (pode demorar ~10 min)
3. **Teste**: Abrir SSMS e conectar em `localhost`

### Etapa 4: Instalar ODBC Driver

1. **Download** e execute o instalador
2. **Instalação padrão**
3. **Verificação**:
   ```cmd
   # Abrir: Painel de Controle → Ferramentas Administrativas → Fontes de Dados ODBC
   # Verificar se "ODBC Driver 17 for SQL Server" está listado
   ```

---

## 📥 Download e Setup do Projeto

### Método 1: Download ZIP (Mais Simples)

1. **Acesse** o repositório GitHub
2. **Clique** em "Code" → "Download ZIP"
3. **Extraia** para uma pasta de sua escolha
4. **Exemplo**: `C:\projetos\corretora-seguros\`

### Método 2: Git Clone (Se tiver Git)

```bash
# Clone do repositório
git clone https://github.com/seu-usuario/corretora-seguros.git
cd corretora-seguros
```

### Instalação das Dependências Python

```bash
# Navegue para a pasta do projeto
cd C:\caminho\para\projeto

# Instale as dependências
pip install -r requirements.txt

# Verificar se instalou corretamente
pip list | findstr Flask
pip list | findstr pyodbc
```

---

## 🗄️ Configuração do Banco de Dados

### Etapa 1: Conectar no SSMS

1. **Abrir** SQL Server Management Studio
2. **Conectar**:
   - Server: `localhost` ou `.\MSSQLSERVER`
   - Authentication: `Windows Authentication`
   - Clique em **Connect**

### Etapa 2: Executar Script de Instalação

1. **Abrir** arquivo `INSTALACAO_COMPLETA.sql` no SSMS
   - File → Open → File → Selecionar o arquivo
2. **Executar** o script completo
   - Pressione `F5` ou clique em "Execute"
3. **Aguardar** conclusão (~30 segundos)

### Etapa 3: Verificar Instalação

```sql
-- Execute no SSMS para verificar
USE CorretoraSegurosDB;
GO

-- Listar tabelas criadas
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Verificar usuários
SELECT * FROM users;
```

**Resultado esperado**: 9 tabelas + tabela users com 3 usuários

---

## ⚙️ Configuração da Aplicação

### Verificar config.py

```python
# Abrir: config.py
# Verificar configurações:

class Config:
    SECRET_KEY = 'supersecretkey'  # Mude em produção
    SQL_SERVER = 'localhost'       # Seu servidor SQL
    SQL_DATABASE = 'CorretoraSegurosDB'
    SQL_USERNAME = None            # Não usado com Windows Auth
    SQL_PASSWORD = None            # Não usado com Windows Auth
    SQL_DRIVER = 'ODBC Driver 17 for SQL Server'
    USE_WINDOWS_AUTH = True        # Use Windows Authentication
```

### Testar Conectividade

```bash
# Execute o teste de conexão
python test_connection.py
```

**Resultado esperado**:
```
Conexão bem-sucedida! SQL Server: Microsoft SQL Server 2019...
Banco atual: CorretoraSegurosDB
Tabelas encontradas: ['Apolices', 'Clientes', ...]
```

---

## 🚀 Primeira Execução

### Inicialização

**Opção A - Script Automático:**
```cmd
# Execute o arquivo .bat
INICIAR_SISTEMA.bat
```

**Opção B - Manual:**
```bash
# No terminal/cmd
cd C:\caminho\para\projeto
python app.py
```

### Verificar se funcionou

```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Acesso ao Sistema

1. **Abrir navegador**
2. **Acessar**: http://localhost:5000
3. **Login**: 
   - Usuário: `master`
   - Senha: `master123`
4. **Resultado**: Dashboard principal deve carregar

---

## ✅ Checklist de Verificação

### Python ✅
- [ ] Python 3.11+ instalado
- [ ] `pip` funcionando
- [ ] `python --version` mostra versão correta

### SQL Server ✅  
- [ ] SQL Server instalado e rodando
- [ ] SSMS conecta em `localhost`
- [ ] Banco `CorretoraSegurosDB` criado
- [ ] Tabelas visíveis no SSMS

### Aplicação ✅
- [ ] Dependências instaladas (`pip list`)
- [ ] `test_connection.py` executa sem erro
- [ ] `python app.py` inicia sem erro
- [ ] http://localhost:5000 abre no navegador
- [ ] Login funciona (master/master123)
- [ ] Dashboard carrega com dados

### Funcionalidades ✅
- [ ] Navegação entre módulos funciona
- [ ] Cadastro de cliente funciona
- [ ] Dashboard mostra estatísticas
- [ ] Logout funciona

---

## 🛠️ Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'flask'"
```bash
# Solução
pip install flask
# ou
pip install -r requirements.txt
```

### Erro: "pyodbc.Error: ('08001', '[08001] [Microsoft]...'"
**Problema**: SQL Server não está rodando ou não acessível
```cmd
# Verificar serviços
services.msc
# Procurar: SQL Server (MSSQLSERVER)
# Status deve ser: "Running"
```

### Erro: "Invalid object name 'CorretoraSegurosDB'"
**Problema**: Banco não foi criado
```sql
-- Execute no SSMS
CREATE DATABASE CorretoraSegurosDB;
-- Depois execute INSTALACAO_COMPLETA.sql
```

### Página não carrega (Erro 500)
**Problema**: Configuração incorreta
1. Verificar `config.py`
2. Executar `test_connection.py`
3. Verificar logs no terminal

### Login não funciona
```sql
-- Verificar usuários no SSMS
USE CorretoraSegurosDB;
SELECT * FROM users;
-- Se vazio, execute insert_users.py
```

---

## 🎯 Próximos Passos

### Após Instalação Bem-sucedida

1. **Alterar senhas padrão** (recomendado)
2. **Adicionar dados de teste** próprios
3. **Explorar funcionalidades** do sistema
4. **Fazer backup** do banco configurado
5. **Configurar para produção** (se necessário)

### Configuração para Produção

```python
# config.py para produção
SECRET_KEY = 'chave-super-secreta-complexa'
DEBUG = False
USE_WINDOWS_AUTH = False  # Se usar SQL Auth
SQL_USERNAME = 'usuario_app'
SQL_PASSWORD = 'senha_complexa'
```

---

## 📞 Suporte

### Se algo não funcionou:

1. **Verifique** cada etapa do checklist
2. **Execute** os testes de diagnóstico
3. **Consulte** os logs de erro
4. **Verifique** versões dos softwares
5. **Abra uma issue** no GitHub com detalhes do erro

### Informações Úteis para Suporte:
- Versão do Python: `python --version`
- Versão do SQL Server: Execute `SELECT @@VERSION` no SSMS
- Sistema Operacional: Windows 10/11
- Mensagens de erro completas

---

**✅ Instalação concluída com sucesso!**

Agora você tem um sistema completo de gestão para corretora de seguros rodando localmente. 🎉