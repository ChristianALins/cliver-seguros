# 🏢 Sistema de Gestão para Corretora de Seguros

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.1.2-green.svg)
![SQL Server](https://img.shields.io/badge/sqlserver-2019+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Um sistema completo de gestão desenvolvido especialmente para corretoras de seguros, oferecendo controle total sobre clientes, apólices, comissões, sinistros e muito mais.

## 🎯 **Funcionalidades Principais**

### 💼 **Gestão Comercial**
- ✅ **Clientes**: Cadastro completo (PF/PJ) com histórico
- ✅ **Apólices**: Controle de vendas com cálculo automático de comissões
- ✅ **Seguradoras**: Gestão de parceiros comerciais
- ✅ **Tipos de Seguro**: Modalidades personalizáveis

### 💰 **Controle Financeiro**
- ✅ **Comissões**: Cálculo automático para corretora e colaboradores
- ✅ **Relatórios**: Performance, vendas por período, comissões
- ✅ **Dashboard**: Indicadores em tempo real

### 🛡️ **Pós-Venda**
- ✅ **Sinistros**: Controle completo de ocorrências
- ✅ **Renovações**: Sistema proativo de renovação de apólices
- ✅ **Tarefas**: CRM integrado para acompanhamento

### 👥 **Gestão de Pessoas**
- ✅ **Colaboradores**: Controle de vendedores e equipe
- ✅ **Permissões**: Sistema de roles (admin, corretor, usuário)
- ✅ **Performance**: Acompanhamento individual de vendas

## 🖥️ **Screenshots**

### Dashboard Principal
![Dashboard](https://via.placeholder.com/800x400/0066cc/ffffff?text=Dashboard+Principal)

### Gestão de Apólices  
![Apolices](https://via.placeholder.com/800x400/28a745/ffffff?text=Gestão+de+Apólices)

### Relatórios Gerenciais
![Relatorios](https://via.placeholder.com/800x400/dc3545/ffffff?text=Relatórios+Gerenciais)

## 🚀 **Tecnologias Utilizadas**

- **Backend**: Python 3.11+ com Flask
- **Banco de dados**: Microsoft SQL Server 2019+
- **Frontend**: HTML5, CSS3, Bootstrap
- **ORM**: PyODBC para conexão com SQL Server
- **Autenticação**: Sistema de sessões Flask

## 📋 **Pré-requisitos**

### Software Necessário
- Python 3.11 ou superior
- Microsoft SQL Server (2019+ recomendado) ou SQL Server Express
- ODBC Driver 17 for SQL Server

### Dependências Python
```bash
Flask==3.1.2
pyodbc>=4.0.35
```

## ⚡ **Instalação Rápida**

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/corretora-seguros.git
cd corretora-seguros
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o banco de dados
Execute o script no SQL Server Management Studio:
```sql
-- Execute INSTALACAO_COMPLETA.sql
```

### 4. Execute a aplicação
```bash
python app.py
```

### 5. Acesse o sistema
- **URL**: http://localhost:5000
- **Login**: master / master123

## 🔧 **Instalação Detalhada**

### Passo 1: Preparação do Ambiente

1. **Instale o Python 3.11+**
   - Download: https://python.org/downloads
   - Marque "Add to PATH" durante instalação

2. **Instale o SQL Server**
   - SQL Server Developer Edition (gratuito)
   - Ou SQL Server Express para uso básico

3. **Instale o ODBC Driver**
   - Download: Microsoft ODBC Driver 17 for SQL Server

### Passo 2: Configuração do Banco

1. **Execute o script de instalação completa**
   ```sql
   -- Abra o SQL Server Management Studio
   -- Execute o arquivo: INSTALACAO_COMPLETA.sql
   ```

2. **Verifique as tabelas criadas**
   - Seguradoras, Tipos_Seguro, Clientes
   - Colaboradores, Apolices, Sinistros
   - Renovacao_Apolices, Tarefas, Users

### Passo 3: Configuração da Aplicação

1. **Ajuste as configurações** (se necessário)
   ```python
   # config.py
   SQL_SERVER = 'localhost'  # Seu servidor SQL
   SQL_DATABASE = 'CorretoraSegurosDB'
   USE_WINDOWS_AUTH = True   # Ou False para SQL Auth
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

### Passo 4: Execução

1. **Inicie a aplicação**
   ```bash
   python app.py
   ```

2. **Acesse via navegador**
   - URL: http://localhost:5000

## 🔐 **Credenciais Padrão**

| Usuário | Senha | Nível de Acesso |
|---------|-------|-----------------|
| master | master123 | Administrador completo |
| admin | admin123 | Administrador |
| user | user123 | Usuário comum |

⚠️ **IMPORTANTE**: Altere essas senhas antes de usar em produção!

## 📊 **Estrutura do Banco de Dados**

### Tabelas Principais

```sql
-- Gestão Comercial
Seguradoras (parceiros comerciais)
Tipos_Seguro (modalidades de seguros)
Clientes (base de clientes PF/PJ)
Colaboradores (equipe de vendas)

-- Operações
Apolices (vendas realizadas - tabela central)
Sinistros (ocorrências e processos)
Renovacao_Apolices (controle de renovações)
Tarefas (CRM e follow-up)

-- Sistema
Users (autenticação e permissões)
```

### Relacionamentos
- **Apolices** é a tabela central que conecta todas as outras
- **Comissões** calculadas automaticamente via campos persistidos
- **Foreign Keys** garantem integridade referencial

## 🎨 **Interface do Usuário**

### Características da Interface
- ✅ **Responsiva**: Funciona em desktop e mobile
- ✅ **Intuitiva**: Navegação clara e organizada
- ✅ **Moderna**: Design clean com Bootstrap
- ✅ **Funcional**: Foco na produtividade

### Módulos Disponíveis
- **Dashboard**: Visão geral com gráficos e indicadores
- **Clientes**: CRUD completo com histórico
- **Apólices**: Gestão de vendas com filtros avançados
- **Sinistros**: Controle de processos e indenizações
- **Relatórios**: Analytics detalhados de performance
- **Configurações**: Gestão de seguradoras, tipos, etc.

## 📈 **Funcionalidades Avançadas**

### Cálculos Automáticos
- **Comissão da Corretora**: `valor_premio × percentual_seguradora ÷ 100`
- **Comissão do Colaborador**: `comissao_corretora × percentual_colaborador ÷ 100`
- **Indicadores**: Totais automáticos no dashboard

### Controles de Negócio
- **Renovações Proativas**: Alertas 30 dias antes do vencimento
- **Status de Apólices**: Ativa, Vencida, Cancelada, Renovada
- **Workflow de Sinistros**: Aberto → Análise → Pago/Negado → Encerrado

### Relatórios Gerenciais
- **Performance por Colaborador**: Vendas, comissões, metas
- **Análise de Produtos**: Seguros mais vendidos
- **Indicadores Financeiros**: Faturamento, comissões a pagar
- **Dashboards Visuais**: Gráficos interativos

## 🛠️ **Desenvolvimento**

### Estrutura do Projeto
```
corretora-seguros/
├── app.py                 # Aplicação Flask principal
├── config.py              # Configurações
├── requirements.txt       # Dependências
├── static/                # Arquivos estáticos
│   ├── css/
│   └── images/
├── templates/             # Templates HTML
├── database/              # Scripts SQL
└── docs/                  # Documentação
```

### Padrões Utilizados
- **MVC**: Separação clara de responsabilidades
- **RESTful**: Rotas organizadas por recurso
- **SQL Seguro**: Uso de parâmetros prepared statements
- **Session Management**: Controle de autenticação via Flask sessions

## 🧪 **Testes**

Execute os testes inclusos:

```bash
# Teste de conexão com banco
python test_connection.py

# Teste de funcionalidades
python test_sistema.py

# Verificação de usuários
python check_users.py
```

## 📝 **Roadmap**

### Versão Atual (v1.0)
- ✅ Sistema base funcional
- ✅ CRUD de todas entidades
- ✅ Cálculos de comissão
- ✅ Relatórios básicos

### Próximas Versões
- 📋 **v1.1**: API REST para integração
- 📋 **v1.2**: Módulo financeiro avançado
- 📋 **v1.3**: Dashboard com gráficos interativos
- 📋 **v2.0**: Versão multi-tenant (múltiplas corretoras)

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 **Suporte**

- 📧 **Email**: seu-email@exemplo.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/corretora-seguros/issues)
- 📚 **Wiki**: [Documentação Completa](https://github.com/seu-usuario/corretora-seguros/wiki)

## ⭐ **Agradecimentos**

- Flask framework pela excelente base web
- Microsoft SQL Server pela robustez
- Bootstrap pela interface responsiva
- Comunidade open source

---

**Desenvolvido com ❤️ para modernizar a gestão de corretoras de seguros**

![Footer](https://via.placeholder.com/800x100/f8f9fa/6c757d?text=Sistema+de+Gestão+para+Corretoras+de+Seguros)