# 🏥 Sistema de Agendamento Clínica Saúde+ - Full Stack

Sistema completo de agendamento de consultas médicas com backend em Python (FastAPI), PostgreSQL e frontend responsivo.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)
- [Funcionalidades](#funcionalidades)
- [Credenciais de Teste](#credenciais-de-teste)

## 🎯 Visão Geral

Sistema desenvolvido para gerenciar o fluxo completo de agendamento de consultas médicas, incluindo:
- Cadastro e autenticação de pacientes, médicos e administradores
- Agendamento de consultas com validações de regras de negócio
- Gerenciamento de horários e bloqueios pelos médicos
- Painel administrativo completo
- Relatórios e estatísticas

## 🚀 Tecnologias

### Backend
- **Python 3.11**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **PostgreSQL** - Banco de dados relacional
- **JWT** - Autenticação segura
- **Bcrypt** - Hash de senhas
- **Pydantic** - Validação de dados

### Frontend
- **HTML5 / CSS3** - Interface responsiva
- **JavaScript (Vanilla)** - Interações do lado do cliente
- **Font Awesome** - Ícones profissionais

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração de containers
- **Nginx** - Servidor web para o frontend

## 📦 Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado
- [Git](https://git-scm.com/) instalado
- Porta 80 (frontend), 8000 (backend) e 5432 (postgres) disponíveis

## ⚡ Instalação e Execução

### 1. Clone o repositório

```bash
git clone https://github.com/rafaelst97/prototype-melhoria.git
cd prototype-melhoria
```

### 2. Inicie os containers

```bash
docker-compose up -d
```

Aguarde alguns segundos para os serviços iniciarem.

### 3. Acesse o sistema

- **Frontend**: http://localhost
- **API (Swagger Docs)**: http://localhost:8000/docs
- **API (ReDoc)**: http://localhost:8000/redoc

### 4. Credenciais de Teste

**Administrador:**
- Email: `admin@clinica.com`
- Senha: `admin123`

## 📁 Estrutura do Projeto

```
prototype-melhoria/
├── backend/
│   ├── app/
│   │   ├── models/         # Modelos do banco de dados (SQLAlchemy)
│   │   ├── routers/        # Endpoints da API (FastAPI)
│   │   ├── schemas/        # Schemas de validação (Pydantic)
│   │   ├── utils/          # Utilitários (auth, validators)
│   │   ├── config.py       # Configurações da aplicação
│   │   ├── database.py     # Conexão com o banco
│   │   └── main.py         # Aplicação principal
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── paciente/               # Frontend - Módulo Paciente
├── medico/                 # Frontend - Módulo Médico
├── admin/                  # Frontend - Módulo Administração
├── css/                    # Estilos globais
├── docker-compose.yml      # Orquestração de containers
├── nginx.conf              # Configuração do Nginx
├── init.sql                # Script de inicialização do banco
└── index.html              # Página inicial
```

## 🔌 API Endpoints

### Autenticação
- `POST /auth/login` - Login de usuário
- `GET /auth/me` - Dados do usuário logado

### Pacientes
- `POST /pacientes/cadastro` - Cadastro de paciente
- `GET /pacientes/perfil` - Perfil do paciente
- `PUT /pacientes/perfil` - Atualizar perfil
- `POST /pacientes/consultas` - Agendar consulta
- `GET /pacientes/consultas` - Listar consultas
- `DELETE /pacientes/consultas/{id}` - Cancelar consulta
- `GET /pacientes/medicos/{id}/horarios-disponiveis` - Horários disponíveis

### Médicos
- `GET /medicos/perfil` - Perfil do médico
- `GET /medicos/consultas` - Listar consultas
- `GET /medicos/consultas/hoje` - Consultas do dia
- `PUT /medicos/consultas/{id}` - Atualizar consulta
- `GET /medicos/horarios` - Listar horários configurados
- `POST /medicos/horarios` - Adicionar horário
- `DELETE /medicos/horarios/{id}` - Remover horário
- `GET /medicos/bloqueios` - Listar bloqueios
- `POST /medicos/bloqueios` - Criar bloqueio
- `DELETE /medicos/bloqueios/{id}` - Remover bloqueio

### Administração
- `GET /admin/dashboard` - Estatísticas gerais
- `GET /admin/medicos` - Listar médicos
- `POST /admin/medicos` - Cadastrar médico
- `PUT /admin/medicos/{id}` - Atualizar médico
- `DELETE /admin/medicos/{id}` - Desativar médico
- `GET /admin/pacientes` - Listar pacientes
- `PUT /admin/pacientes/{id}/bloquear` - Bloquear paciente
- `PUT /admin/pacientes/{id}/desbloquear` - Desbloquear paciente
- `GET /admin/convenios` - Listar convênios
- `POST /admin/convenios` - Cadastrar convênio
- `PUT /admin/convenios/{id}` - Atualizar convênio
- `GET /admin/especialidades` - Listar especialidades
- `POST /admin/especialidades` - Cadastrar especialidade
- `GET /admin/consultas` - Listar todas consultas

**Documentação completa:** http://localhost:8000/docs

## ✨ Funcionalidades

### Módulo Paciente
- ✅ Cadastro com validação de CPF único
- ✅ Agendamento de consultas
- ✅ Limite de 2 consultas simultâneas
- ✅ Cancelamento com regra de 24h
- ✅ Histórico de consultas
- ✅ Gerenciamento de perfil

### Módulo Médico
- ✅ Agenda diária e semanal
- ✅ Configuração de horários disponíveis
- ✅ Bloqueio de horários específicos
- ✅ Registro de observações sobre pacientes
- ✅ Visualização de consultas futuras

### Módulo Administração
- ✅ Dashboard com estatísticas
- ✅ CRUD completo de médicos
- ✅ CRUD de convênios e especialidades
- ✅ Bloqueio/desbloqueio de pacientes
- ✅ Listagem e filtros de consultas
- ✅ Gerenciamento de usuários

### Regras de Negócio Implementadas
- ✅ Paciente pode ter no máximo 2 consultas agendadas
- ✅ Cancelamento deve ser feito com 24h de antecedência
- ✅ Não é possível agendar em horários bloqueados
- ✅ Validação de conflitos de horários
- ✅ Apenas horários dentro da grade do médico
- ✅ Autenticação JWT com tokens seguros
- ✅ Senhas criptografadas com bcrypt

## 🗄️ Banco de Dados

O banco de dados PostgreSQL possui as seguintes tabelas:

- **usuarios** - Dados de autenticação
- **pacientes** - Dados específicos de pacientes
- **medicos** - Dados específicos de médicos
- **admins** - Dados específicos de administradores
- **especialidades** - Especialidades médicas
- **convenios** - Convênios médicos
- **consultas** - Agendamentos de consultas
- **horarios_disponiveis** - Grade de horários dos médicos
- **bloqueios_horarios** - Bloqueios de horários

## 🛠️ Comandos Úteis

### Parar os containers
```bash
docker-compose down
```

### Ver logs
```bash
docker-compose logs -f
```

### Ver logs apenas do backend
```bash
docker-compose logs -f backend
```

### Resetar banco de dados
```bash
docker-compose down -v
docker-compose up -d
```

### Acessar banco de dados diretamente
```bash
docker exec -it clinica_db psql -U clinica_user -d clinica_saude
```

### Executar migrações manualmente
```bash
docker exec -it clinica_backend python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## 🧪 Testando a API

### Exemplo: Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clinica.com",
    "senha": "admin123"
  }'
```

### Exemplo: Listar Especialidades (requer token)
```bash
curl -X GET http://localhost:8000/medicos/especialidades \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 🔐 Segurança

- ✅ Senhas criptografadas com bcrypt (12 rounds)
- ✅ Autenticação JWT com expiração
- ✅ Validação de dados com Pydantic
- ✅ Proteção contra SQL Injection (SQLAlchemy ORM)
- ✅ CORS configurado
- ✅ Middleware de autenticação em rotas protegidas

## 📝 Desenvolvimento

### Adicionar nova rota

1. Criar o endpoint em `backend/app/routers/`
2. Adicionar schema em `backend/app/schemas/schemas.py`
3. Incluir router em `backend/app/main.py`

### Modificar banco de dados

1. Alterar modelos em `backend/app/models/models.py`
2. Recriar containers: `docker-compose down -v && docker-compose up -d`

## 🐛 Troubleshooting

### Porta 80 em uso
Altere a porta do frontend em `docker-compose.yml`:
```yaml
frontend:
  ports:
    - "8080:80"  # Acessar em http://localhost:8080
```

### Erro ao conectar no banco
Verifique se o PostgreSQL iniciou:
```bash
docker-compose logs postgres
```

### Backend não inicia
Verifique os logs:
```bash
docker-compose logs backend
```

## 👥 Autor

**Rafael** - [@rafaelst97](https://github.com/rafaelst97)

## 📄 Licença

Este projeto foi desenvolvido como protótipo educacional para a disciplina de Melhoria de Processo de Software.

---

**Versão:** 2.0.0  
**Data:** Outubro 2025  
**Stack:** Python + FastAPI + PostgreSQL + Docker
