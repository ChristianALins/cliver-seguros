# 🏢 CLIVER Seguros - Sistema de Gestão Integrada<<<<<<< HEAD

# 🏢 Sistema de Gestão para Corretora de Seguros

![Versão](https://img.shields.io/badge/versão-2.1.0-brightgreen)

![Status](https://img.shields.io/badge/status-funcional-success)![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)

![Python](https://img.shields.io/badge/python-3.8+-blue)![Flask](https://img.shields.io/badge/flask-v3.1.2-green.svg)

![Flask](https://img.shields.io/badge/flask-2.0+-blue)![SQL Server](https://img.shields.io/badge/sqlserver-2019+-red.svg)

![SQL Server](https://img.shields.io/badge/sql%20server-2019+-blue)![License](https://img.shields.io/badge/license-MIT-blue.svg)



## 📋 Sobre o ProjetoUm sistema completo de gestão desenvolvido especialmente para corretoras de seguros, oferecendo controle total sobre clientes, apólices, comissões, sinistros e muito mais.



O **CLIVER Seguros** é um sistema completo de gestão para corretoras de seguros, desenvolvido em Python com Flask e SQL Server. O sistema oferece funcionalidades robustas para gerenciamento de clientes, apólices, sinistros e relatórios.## 🎯 **Funcionalidades Principais**



## ✨ Funcionalidades Principais### 💼 **Gestão Comercial**

- ✅ **Clientes**: Cadastro completo (PF/PJ) com histórico

### 🔐 **Autenticação e Segurança**- ✅ **Apólices**: Controle de vendas com cálculo automático de comissões

- ✅ Login seguro com validação aprimorada- ✅ **Seguradoras**: Gestão de parceiros comerciais

- ✅ Controle de sessão e permissões- ✅ **Tipos de Seguro**: Modalidades personalizáveis

- ✅ Níveis de acesso hierárquicos (Administrador, Gerente, Corretor)

- ✅ Proteção contra XSS e validação de entrada### 💰 **Controle Financeiro**

- ✅ **Comissões**: Cálculo automático para corretora e colaboradores

### 👥 **Gestão de Clientes**- ✅ **Relatórios**: Performance, vendas por período, comissões

- ✅ Cadastro completo PF/PJ- ✅ **Dashboard**: Indicadores em tempo real

- ✅ CRUD completo e seguro

- ✅ Sistema de busca em tempo real### 🛡️ **Pós-Venda**

- ✅ Exclusão protegida com verificação de dependências- ✅ **Sinistros**: Controle completo de ocorrências

- ✅ Interface responsiva e intuitiva- ✅ **Renovações**: Sistema proativo de renovação de apólices

- ✅ **Tarefas**: CRM integrado para acompanhamento

### 🏠 **Dashboard Inteligente**

- ✅ Estatísticas em tempo real### 👥 **Gestão de Pessoas**

- ✅ Visão geral do sistema- ✅ **Colaboradores**: Controle de vendedores e equipe

- ✅ Navegação intuitiva- ✅ **Permissões**: Sistema de roles (admin, corretor, usuário)

- ✅ Módulos organizados- ✅ **Performance**: Acompanhamento individual de vendas



### 🛡️ **Recursos Técnicos**## 🖥️ **Screenshots**

- ✅ Tratamento robusto de erros

- ✅ Logging estruturado### Dashboard Principal

- ✅ Operações de banco seguras![Dashboard](https://via.placeholder.com/800x400/0066cc/ffffff?text=Dashboard+Principal)

- ✅ Interface moderna e responsiva

- ✅ Validação completa de dados### Gestão de Apólices  

![Apolices](https://via.placeholder.com/800x400/28a745/ffffff?text=Gestão+de+Apólices)

## 🚀 Instalação e Configuração

### Relatórios Gerenciais

### 📋 Pré-requisitos![Relatorios](https://via.placeholder.com/800x400/dc3545/ffffff?text=Relatórios+Gerenciais)



- Python 3.8 ou superior## 🚀 **Tecnologias Utilizadas**

- SQL Server 2019 ou superior

- ODBC Driver 17/18 for SQL Server- **Backend**: Python 3.11+ com Flask

- **Banco de dados**: Microsoft SQL Server 2019+

### 🔧 Instalação- **Frontend**: HTML5, CSS3, Bootstrap

- **ORM**: PyODBC para conexão com SQL Server

1. **Clone o repositório:**- **Autenticação**: Sistema de sessões Flask

```bash

git clone https://github.com/ChristianALins/cliver-seguros.git## 📋 **Pré-requisitos**

cd cliver-seguros

```### Software Necessário

- Python 3.11 ou superior

2. **Instale as dependências:**- Microsoft SQL Server (2019+ recomendado) ou SQL Server Express

```bash- ODBC Driver 17 for SQL Server

pip install -r requirements_sqlserver.txt

```### Dependências Python

```bash

3. **Configure o banco de dados:**Flask==3.1.2

```bashpyodbc>=4.0.35

# Execute o script de criação do banco```

sqlcmd -S localhost -i criar_banco_sqlserver.sql

## ⚡ **Instalação Rápida**

# Execute o script de criação das tabelas

sqlcmd -S localhost -d CorretoraSegurosDB -i create_tables_completo.sql### 1. Clone o repositório

```bash

# Crie os usuários iniciaisgit clone https://github.com/seu-usuario/corretora-seguros.git

python criar_colaboradores.pycd corretora-seguros

``````



4. **Inicie o sistema:**### 2. Instale as dependências

```bash```bash

# Windowspip install -r requirements.txt

INICIAR_SISTEMA.bat```



# Manual### 3. Configure o banco de dados

python app_sistema_corrigido.pyExecute o script no SQL Server Management Studio:

``````sql

-- Execute INSTALACAO_COMPLETA.sql

## 🌐 Acesso ao Sistema```



- **URL:** `http://localhost:5006`### 4. Execute a aplicação

- **Usuário de teste:** `christian.lins@outlook.com.br````bash

- **Senha:** `123456`python app.py

```

## 📁 Estrutura do Projeto

### 5. Acesse o sistema

```- **URL**: http://localhost:5000

cliver-seguros/- **Login**: master / master123

├── app_sistema_corrigido.py     # Aplicação principal (Versão 2.1)

├── config.py                    # Configurações do sistema## 🔧 **Instalação Detalhada**

├── requirements_sqlserver.txt   # Dependências Python

├── criar_banco_sqlserver.sql    # Script criação banco### Passo 1: Preparação do Ambiente

├── create_tables_completo.sql   # Script criação tabelas

├── database_completo_melhorado.sql # Schema completo1. **Instale o Python 3.11+**

├── criar_colaboradores.py       # Script usuários iniciais   - Download: https://python.org/downloads

├── verificar_banco.py          # Utilitário verificação DB   - Marque "Add to PATH" durante instalação

├── verificar_colaboradores.py  # Utilitário verificação users

├── INICIAR_SISTEMA.bat         # Script inicialização Windows2. **Instale o SQL Server**

├── INICIAR_CLIVER_SQLSERVER.bat # Script inicialização SQL Server   - SQL Server Developer Edition (gratuito)

├── README.md                   # Este arquivo   - Ou SQL Server Express para uso básico

├── LICENSE                     # Licença do projeto

├── VERSION                     # Controle de versão3. **Instale o ODBC Driver**

├── PROJECT_SUMMARY.md          # Resumo técnico   - Download: Microsoft ODBC Driver 17 for SQL Server

├── IMPLEMENTACAO_COMPLETA.md   # Documentação implementação

└── SISTEMA_FUNCIONANDO.md      # Status funcionalidades### Passo 2: Configuração do Banco

```

1. **Execute o script de instalação completa**

## 🎯 Módulos do Sistema   ```sql

   -- Abra o SQL Server Management Studio

### ✅ **Implementados**   -- Execute o arquivo: INSTALACAO_COMPLETA.sql

- **👥 Clientes:** CRUD completo com busca e validação   ```

- **🏠 Dashboard:** Interface principal com estatísticas

- **🔐 Autenticação:** Sistema de login e permissões2. **Verifique as tabelas criadas**

- **👤 Perfil:** Gerenciamento de perfil do usuário   - Seguradoras, Tipos_Seguro, Clientes

   - Colaboradores, Apolices, Sinistros

### 🚧 **Em Desenvolvimento**   - Renovacao_Apolices, Tarefas, Users

- **📋 Apólices:** Gestão de apólices e comissões

- **🛡️ Sinistros:** Controle de sinistros### Passo 3: Configuração da Aplicação

- **📝 Tarefas:** Sistema de atividades

- **⚠️ Vencimentos:** Controle de renovações1. **Ajuste as configurações** (se necessário)

- **👨‍💼 Colaboradores:** Gestão de equipe (Admin)   ```python

- **🏦 Seguradoras:** Gestão de parceiros (Admin)   # config.py

- **📊 Relatórios:** Business Intelligence   SQL_SERVER = 'localhost'  # Seu servidor SQL

   SQL_DATABASE = 'CorretoraSegurosDB'

## 💡 Recursos Técnicos   USE_WINDOWS_AUTH = True   # Ou False para SQL Auth

   ```

### 🛡️ **Segurança**

- Validação rigorosa de entrada de dados2. **Instale as dependências**

- Proteção contra SQL Injection   ```bash

- Escape de HTML contra XSS   pip install -r requirements.txt

- Controle de sessão seguro   ```

- Verificação de permissões por nível

### Passo 4: Execução

### ⚡ **Performance**

- Conexões de banco otimizadas1. **Inicie a aplicação**

- Operações seguras com rollback   ```bash

- Tratamento robusto de erros   python app.py

- Logging estruturado   ```

- Interface responsiva

2. **Acesse via navegador**

### 🔧 **Manutenção**   - URL: http://localhost:5000

- Código bem documentado

- Estrutura modular## 🔐 **Credenciais Padrão**

- Tratamento de exceções

- Scripts de utilitários| Usuário | Senha | Nível de Acesso |

- Versionamento controlado|---------|-------|-----------------|

| master | master123 | Administrador completo |

## 📞 Suporte| admin | admin123 | Administrador |

| user | user123 | Usuário comum |

Para suporte técnico ou dúvidas sobre o sistema:

⚠️ **IMPORTANTE**: Altere essas senhas antes de usar em produção!

- **Email:** christian.lins@outlook.com.br

- **GitHub:** [ChristianALins/cliver-seguros](https://github.com/ChristianALins/cliver-seguros)## 📊 **Estrutura do Banco de Dados**



## 📜 Licença### Tabelas Principais



Este projeto está licenciado sob a [MIT License](LICENSE).```sql

-- Gestão Comercial

## 🏆 Status do ProjetoSeguradoras (parceiros comerciais)

Tipos_Seguro (modalidades de seguros)

```Clientes (base de clientes PF/PJ)

🎯 Status: TOTALMENTE FUNCIONAL ✅Colaboradores (equipe de vendas)

📊 Cobertura: Módulos principais implementados

🔒 Segurança: Validações e proteções implementadas-- Operações

📱 Interface: Responsiva e modernaApolices (vendas realizadas - tabela central)

🚀 Performance: Otimizada e estávelSinistros (ocorrências e processos)

```Renovacao_Apolices (controle de renovações)

Tarefas (CRM e follow-up)

---

-- Sistema

**Desenvolvido com ❤️ por Christian Lins**Users (autenticação e permissões)

```

*Sistema de Gestão para Corretoras de Seguros - Versão 2.1.0*
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
=======
# cliver-seguros
Sistema de Gestão para Corretora de Seguros - Cliver Seguros v1.2
>>>>>>> eb06adb4c9518d0f4fa88fba38d0801bf203e043
