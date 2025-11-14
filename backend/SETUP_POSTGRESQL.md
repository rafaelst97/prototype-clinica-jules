# 🗄️ Guia de Instalação e Configuração do PostgreSQL

## 📋 Pré-requisitos

- PostgreSQL 14+ instalado
- Python 3.10+
- Dependências do projeto instaladas

---

## 🔧 Passo 1: Instalar PostgreSQL

### Windows
1. Baixar PostgreSQL: https://www.postgresql.org/download/windows/
2. Executar o instalador
3. Durante a instalação:
   - Senha do usuário `postgres`: `postgres` (ou escolha outra)
   - Porta padrão: `5432`
   - Locale: `Portuguese, Brazil`

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS
```bash
brew install postgresql@14
brew services start postgresql@14
```

---

## 🎯 Passo 2: Criar Banco de Dados e Usuário

### Conectar ao PostgreSQL
```bash
# Windows (PowerShell como Admin)
psql -U postgres

# Linux/macOS
sudo -u postgres psql
```

### Executar comandos SQL
```sql
-- Criar usuário
CREATE USER clinica_user WITH PASSWORD 'clinica_pass123';

-- Criar banco de dados
CREATE DATABASE clinica_saude OWNER clinica_user;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE clinica_saude TO clinica_user;

-- Conectar ao banco criado
\c clinica_saude

-- Conceder privilégios no schema public
GRANT ALL ON SCHEMA public TO clinica_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO clinica_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO clinica_user;

-- Sair
\q
```

---

## ⚙️ Passo 3: Configurar Variáveis de Ambiente

O arquivo `backend/.env` já está configurado:

```env
POSTGRES_USER=clinica_user
POSTGRES_PASSWORD=clinica_pass123
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=clinica_saude
```

**⚠️ IMPORTANTE:** Se você usou senha diferente, atualize o `.env`

---

## 🚀 Passo 4: Executar Setup do Banco de Dados

### Instalar dependências (se ainda não instalou)
```bash
cd backend
pip install -r requirements.txt
```

### Executar script de setup
```bash
python setup_database.py
```

Este script irá:
1. ✅ Criar todas as 9 tabelas (conforme MER)
2. ✅ Popular com dados de teste
3. ✅ Criar credenciais de acesso

---

## 🔑 Credenciais Padrão

### Administrador
- **Email:** admin@clinica.com
- **Senha:** admin123

### Médicos
- **Email:** joao.silva@clinica.com (ou outros médicos)
- **Senha:** medico123

### Pacientes
- **Email:** carlos@email.com (ou outros pacientes)
- **Senha:** paciente123

---

## ✅ Passo 5: Verificar Instalação

### Testar conexão
```bash
python -c "from app.database import engine; print('✅ Conexão OK!' if engine else '❌ Erro')"
```

### Iniciar servidor
```bash
uvicorn app.main:app --reload
```

### Acessar documentação da API
Abra no navegador: http://localhost:8000/docs

---

## 🧪 Passo 6: Executar Testes

```bash
# Testes de estrutura do banco
pytest tests/test_database_structure.py -v

# Testes de regras de negócio
pytest tests/test_regras_negocio.py -v

# Todos os testes
pytest tests/ -v
```

---

## 🔍 Comandos Úteis PostgreSQL

### Ver todas as tabelas
```sql
\c clinica_saude
\dt
```

### Ver dados de uma tabela
```sql
SELECT * FROM especialidade;
SELECT * FROM paciente;
SELECT * FROM medico;
```

### Resetar banco (CUIDADO!)
```bash
python setup_database.py  # Recria tudo do zero
```

---

## 🐛 Troubleshooting

### Erro: "password authentication failed"
- Verifique o `.env` com as credenciais corretas
- Execute: `ALTER USER clinica_user WITH PASSWORD 'clinica_pass123';`

### Erro: "database does not exist"
- Execute o Passo 2 novamente para criar o banco

### Erro: "permission denied for schema public"
- Execute os comandos de GRANT do Passo 2

### Porta 5432 em uso
- Verifique se já existe outra instância do PostgreSQL rodando
- Mude a porta no `.env` e no PostgreSQL

---

## 📚 Estrutura do Banco de Dados

### 9 Tabelas (100% conforme MER)
1. **ESPECIALIDADE** - Especialidades médicas
2. **PLANOSAUDE** - Planos de saúde (ex-Convênio)
3. **ADMINISTRADOR** - Usuários administradores
4. **MEDICO** - Médicos cadastrados
5. **PACIENTE** - Pacientes cadastrados
6. **HORARIOTRABALHO** - Horários de atendimento dos médicos
7. **CONSULTA** - Consultas agendadas/realizadas
8. **OBSERVACAO** - Observações médicas das consultas
9. **RELATORIO** - Relatórios gerados (uso futuro)

### Relacionamentos
- MEDICO → ESPECIALIDADE (N:1)
- PACIENTE → PLANOSAUDE (N:1)
- CONSULTA → PACIENTE (N:1)
- CONSULTA → MEDICO (N:1)
- HORARIOTRABALHO → MEDICO (N:1)
- OBSERVACAO → CONSULTA (N:1)

---

## 🎉 Pronto!

O banco de dados está configurado e populado. Agora você pode:
1. ✅ Testar a API no Swagger: http://localhost:8000/docs
2. ✅ Fazer login nos 3 portais (admin, medico, paciente)
3. ✅ Executar os testes automatizados
4. ✅ Validar as 4 regras de negócio (RN1-RN4)
