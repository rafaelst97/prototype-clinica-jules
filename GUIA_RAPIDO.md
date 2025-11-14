# 🚀 Guia Rápido - Sistema Clínica Saúde+

## 📊 Acessar Interfaces

### 1. Frontend (Sistema Web)
**URL:** http://localhost  
Sistema principal para pacientes, médicos e administradores

### 2. API Docs (Swagger)
**URL:** http://localhost:8000/docs  
Documentação interativa da API REST com testes

### 3. pgAdmin (Banco de Dados)
**URL:** http://localhost:5050  
Interface gráfica para visualizar e gerenciar o PostgreSQL

**Credenciais pgAdmin:**
- Email: `admin@clinica.com`
- Senha: `admin123`

**Após login no pgAdmin:**
1. Clique em "Add New Server"
2. Aba "General":
   - Name: `Clinica Saude`
3. Aba "Connection":
   - Host: `postgres`
   - Port: `5432`
   - Database: `clinica_saude`
   - Username: `clinica_user`
   - Password: `clinica_pass`
4. Clique em "Save"

Agora você pode navegar pelas tabelas em:
**Servers > Clinica Saude > Databases > clinica_saude > Schemas > public > Tables**

## 🔑 Credenciais de Teste

### Administrador
- **Email:** admin@clinica.com
- **Senha:** admin123
- **Acesso:** http://localhost/admin/login.html

### Médicos
- **Dr. João Silva (Cardiologia)**
  - Email: dr.silva@clinica.com
  - Senha: medico123
  
- **Dra. Maria Santos (Dermatologia)**
  - Email: dra.santos@clinica.com
  - Senha: medico123
  
- **Dr. Pedro Oliveira (Pediatria)**
  - Email: dr.oliveira@clinica.com
  - Senha: medico123

### Paciente
- Você pode criar seu próprio cadastro em: http://localhost/paciente/cadastro.html

## 🎯 Fluxo de Uso

### 1. Popular Banco de Dados (Primeira vez)
```bash
docker exec -it clinica_backend python seed_data.py
```

### 2. Cadastrar Paciente
1. Acesse: http://localhost/paciente/cadastro.html
2. Preencha o formulário
3. Faça login

### 3. Agendar Consulta (Como Paciente)
1. Login no sistema
2. Ir em "Agendar Consulta"
3. Escolher especialidade
4. Escolher médico
5. Escolher data e horário
6. Confirmar

### 4. Gerenciar Horários (Como Médico)
1. Login como médico
2. Ir em "Horários Disponíveis"
3. Configurar grade de horários
4. Bloquear horários específicos se necessário

### 5. Administração
1. Login como admin
2. Dashboard com estatísticas
3. Gerenciar médicos, pacientes, convênios
4. Visualizar todas as consultas

## 🔧 Comandos Úteis

### Iniciar Sistema
```bash
docker-compose up -d
```

### Ver Logs
```bash
docker-compose logs -f
docker-compose logs -f backend  # Apenas backend
```

### Parar Sistema
```bash
docker-compose down
```

### Resetar Banco de Dados
```bash
docker-compose down -v
docker-compose up -d
docker exec -it clinica_backend python seed_data.py
```

### Acessar Container Backend
```bash
docker exec -it clinica_backend /bin/bash
```

### Acessar PostgreSQL via terminal
```bash
docker exec -it clinica_db psql -U clinica_user -d clinica_saude
```

## 📋 Tabelas do Banco

1. **usuarios** - Dados de autenticação (todos os tipos)
2. **pacientes** - Dados específicos de pacientes
3. **medicos** - Dados específicos de médicos
4. **admins** - Dados específicos de administradores
5. **especialidades** - Especialidades médicas
6. **convenios** - Convênios médicos
7. **consultas** - Agendamentos
8. **horarios_disponiveis** - Grade de horários dos médicos
9. **bloqueios_horarios** - Bloqueios temporários

## 🐛 Troubleshooting

### Backend não inicia
```bash
docker-compose logs backend
docker-compose restart backend
```

### Erro de conexão com banco
```bash
docker-compose restart postgres
```

### Limpar tudo e recomeçar
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d --build
docker exec -it clinica_backend python seed_data.py
```

## 📚 Recursos

- **Swagger UI:** http://localhost:8000/docs - Teste todas as APIs
- **ReDoc:** http://localhost:8000/redoc - Documentação alternativa
- **pgAdmin:** http://localhost:5050 - Interface do banco
- **Frontend:** http://localhost - Sistema web

## ✅ Checklist de Verificação

- [ ] Containers rodando: `docker-compose ps`
- [ ] Backend respondendo: http://localhost:8000
- [ ] Frontend acessível: http://localhost
- [ ] Banco populado: Verificar no pgAdmin
- [ ] Login funcionando: Testar com admin@clinica.com
