# 🐘 GUIA DE MIGRAÇÃO PARA POSTGRESQL

## ⚠️ SITUAÇÃO ATUAL

O PostgreSQL **não está instalado** ou **não está no PATH** do sistema.

---

## 📋 OPÇÕES

### OPÇÃO 1: Instalar PostgreSQL (Recomendado para Produção)

#### 1️⃣ **Instalar PostgreSQL**

**Via Instalador Oficial:**
- Download: https://www.postgresql.org/download/windows/
- Execute o instalador
- Durante a instalação:
  - Defina senha para usuário `postgres`
  - Porta: 5432 (padrão)
  - Locale: Português do Brasil

**Via Chocolatey (se tiver instalado):**
```powershell
choco install postgresql
```

#### 2️⃣ **Adicionar ao PATH**

Adicione ao PATH do Windows:
```
C:\Program Files\PostgreSQL\<versão>\bin
```

Reinicie o terminal após adicionar ao PATH.

#### 3️⃣ **Criar Banco e Usuário**

Execute no terminal (com PostgreSQL no PATH):
```powershell
# Conectar como postgres
psql -U postgres

# No prompt do psql, execute:
CREATE USER clinica_user WITH PASSWORD 'clinica_pass';
CREATE DATABASE clinica_saude OWNER clinica_user;
GRANT ALL PRIVILEGES ON DATABASE clinica_saude TO clinica_user;
\q
```

Ou execute o arquivo SQL:
```powershell
psql -U postgres -f backend\setup_postgres.sql
```

#### 4️⃣ **Criar Tabelas e Popular**

```powershell
cd backend
python migrate_postgres.py
```

#### 5️⃣ **Iniciar Servidor**

```powershell
uvicorn app.main:app --reload
```

---

### OPÇÃO 2: Usar Docker (Mais Rápido para Testar)

#### 1️⃣ **Verificar Docker**

```powershell
docker --version
```

#### 2️⃣ **Iniciar PostgreSQL via Docker**

```powershell
docker run --name clinica-postgres `
  -e POSTGRES_USER=clinica_user `
  -e POSTGRES_PASSWORD=clinica_pass `
  -e POSTGRES_DB=clinica_saude `
  -p 5432:5432 `
  -d postgres:15
```

#### 3️⃣ **Criar Tabelas e Popular**

```powershell
cd backend
python migrate_postgres.py
```

#### 4️⃣ **Iniciar Servidor**

```powershell
uvicorn app.main:app --reload
```

---

### OPÇÃO 3: Voltar para SQLite (Desenvolvimento)

Se quiser apenas testar rapidamente:

#### 1️⃣ **Editar backend/.env**

```env
APP_ENV=test
# DATABASE_URL=sqlite:///./clinica.db  (comentado, usa padrão)
```

#### 2️⃣ **Recriar banco SQLite**

```powershell
cd backend
python setup_quick.py
```

#### 3️⃣ **Iniciar servidor**

```powershell
uvicorn app.main:app --reload
```

---

## 🎯 RECOMENDAÇÃO

Para **desenvolvimento rápido**: Use **OPÇÃO 3** (SQLite)

Para **produção/teste real**: Use **OPÇÃO 2** (Docker) ou **OPÇÃO 1** (PostgreSQL instalado)

---

## 📝 PRÓXIMOS PASSOS

Escolha uma opção acima e me avise para eu continuar! 👍

### Perguntas:

1. **Você tem Docker instalado?**
2. **Prefere instalar PostgreSQL ou usar SQLite por enquanto?**
3. **É para produção ou apenas desenvolvimento/testes?**
