# GUIA DE PRÓXIMOS PASSOS - CLÍNICA SAÚDE+

## 🎯 Status Atual
- ✅ Sistema operacional com 63.6% de testes aprovados
- ✅ Todas as funcionalidades principais implementadas
- ✅ Banco de dados populado e funcional
- ✅ Backend e frontend rodando estáveis

## 🔧 CORREÇÕES PRIORITÁRIAS

### 1. Corrigir API de Consultas do Paciente (CRÍTICO)
**Arquivo**: `backend/app/routers/consultas.py` ou similar  
**Problema**: Retorna erro ao tentar listar consultas do paciente  
**Como testar**:
```bash
# Fazer login como paciente
# Navegar para http://localhost/paciente/consultas.html
# Verificar se as consultas são carregadas
```

**Possíveis causas**:
- Query SQL incorreta
- Problema com filtro por userId
- Falta de JOIN com médico/especialidade

### 2. Adicionar IDs na Página de Consultas do Médico
**Arquivo**: `medico/consultas.html`  
**Adicionar**:
```html
<h1 id="tituloConsultas">Consultas Agendadas</h1>
<div id="listaConsultas">
  <!-- conteúdo das consultas -->
</div>
```

### 3. Adicionar IDs na Página de Horários do Médico
**Arquivo**: `medico/horarios.html`  
**Adicionar**:
```html
<div id="listaHorarios">
  <!-- conteúdo dos horários -->
</div>
```

## 📋 FUNCIONALIDADES A IMPLEMENTAR

### 1. Cancelamento de Consulta
**Requisitos**:
- Permitir cancelamento até 24h antes
- Atualizar status da consulta para "CANCELADA"
- Registrar motivo do cancelamento
- Liberar horário para novos agendamentos

**Endpoint sugerido**:
```python
PUT /api/consultas/{id}/cancelar
Body: { "motivo": "string" }
```

### 2. Reagendamento de Consulta
**Requisitos**:
- Permitir reagendamento até 24h antes
- Verificar disponibilidade do novo horário
- Manter histórico de alterações

**Endpoint sugerido**:
```python
PUT /api/consultas/{id}/reagendar
Body: { "nova_data": "date", "novo_horario": "time" }
```

### 3. Validação de Regras de Negócio

#### Regra 1: Máximo 2 Consultas Futuras
**Arquivo**: `backend/app/routers/consultas.py` - função `agendar_consulta`
```python
# Verificar consultas futuras do paciente
consultas_futuras = db.query(Consulta).filter(
    Consulta.paciente_id == paciente_id,
    Consulta.status.in_(['agendada', 'confirmada']),
    Consulta.data >= datetime.now().date()
).count()

if consultas_futuras >= 2:
    raise HTTPException(
        status_code=400,
        detail="Você já possui 2 consultas agendadas. Cancele uma para agendar nova consulta."
    )
```

#### Regra 2: Cancelamento com 24h de Antecedência
```python
from datetime import datetime, timedelta

consulta = db.query(Consulta).get(consulta_id)
data_hora_consulta = datetime.combine(consulta.data, consulta.hora)
limite_cancelamento = data_hora_consulta - timedelta(hours=24)

if datetime.now() > limite_cancelamento:
    raise HTTPException(
        status_code=400,
        detail="Cancelamento deve ser feito com pelo menos 24h de antecedência"
    )
```

#### Regra 3: Bloqueio por 3 Faltas Consecutivas
**Arquivo**: `backend/app/models/models.py` - Paciente
```python
# Campo já existe: faltas_consecutivas

# Ao marcar falta:
paciente.faltas_consecutivas += 1
if paciente.faltas_consecutivas >= 3:
    usuario.bloqueado = True
```

**Desbloqueio pelo admin**:
```python
PUT /api/admin/pacientes/{id}/desbloquear
```

## 📊 RELATÓRIOS EM PDF

### Biblioteca Recomendada
```bash
pip install reportlab
```

### Exemplo de Implementação
**Arquivo**: `backend/app/utils/pdf_generator.py`
```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def gerar_relatorio_consultas(data_inicio, data_fim):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Relatório de Consultas")
    
    # Conteúdo
    consultas = db.query(Consulta).filter(...).all()
    y = 750
    for consulta in consultas:
        p.drawString(100, y, f"{consulta.data} - {consulta.paciente.nome}")
        y -= 20
    
    p.save()
    buffer.seek(0)
    return buffer
```

## 🧪 COMO EXECUTAR OS TESTES

### Testes Automatizados Selenium
```bash
cd "tests"
python teste_completo_automatizado_v2.py
```

### Testes Manuais
1. **Admin**: http://localhost/admin/login.html
   - Usuário: admin
   - Senha: admin123

2. **Médico**: http://localhost/medico/login.html
   - CRM: 12345-SC
   - Senha: medico123

3. **Paciente**: http://localhost/paciente/login.html
   - Email: paciente1@teste.com
   - Senha: paciente123

## 🔄 COMANDOS ÚTEIS

### Reiniciar Serviços
```powershell
cd "C:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto"
docker-compose restart backend
```

### Recriar Banco de Dados
```powershell
docker exec clinica_backend python create_tables.py
docker exec clinica_backend python seed_data.py
```

### Ver Logs
```powershell
docker logs clinica_backend --tail 50
docker logs clinica_frontend --tail 50
docker logs clinica_db --tail 50
```

### Acessar Banco de Dados
```powershell
# Via PgAdmin: http://localhost:5050
# Email: admin@clinica.com
# Senha: admin123

# Via psql (dentro do container)
docker exec -it clinica_db psql -U clinica_user -d clinica_saude
```

## 📚 DOCUMENTAÇÃO

### API (Swagger)
http://localhost:8000/docs

### Estrutura do Projeto
```
projeto/
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── routers/     # Endpoints
│   │   ├── models/      # Modelos SQLAlchemy
│   │   ├── schemas/     # Schemas Pydantic
│   │   └── utils/       # Utilitários
│   ├── seed_data.py     # Popular BD
│   └── create_tables.py # Criar tabelas
├── admin/           # Frontend Admin
├── medico/          # Frontend Médico
├── paciente/        # Frontend Paciente
├── js/              # JavaScript
├── css/             # Estilos
├── tests/           # Testes E2E
└── docs/            # Documentação
```

## ✅ CHECKLIST DE VALIDAÇÃO

Antes de considerar o projeto 100% completo:

### Funcionalidades
- [x] Cadastro de paciente
- [x] Login (admin, médico, paciente)
- [x] Listar médicos
- [x] Cadastrar médico
- [x] Listar convênios
- [x] Agendar consulta
- [ ] Visualizar consultas (corrigir)
- [ ] Cancelar consulta
- [ ] Reagendar consulta
- [ ] Registrar observação médica
- [ ] Gerar relatórios PDF
- [ ] Bloquear/desbloquear pacientes

### Regras de Negócio
- [ ] Máximo 2 consultas futuras
- [ ] Cancelamento com 24h
- [ ] Bloqueio por 3 faltas
- [ ] Evitar conflitos de horários

### Testes
- [x] Testes E2E Selenium (7/11)
- [ ] Testes de API (0%)
- [ ] Testes de unidade (0%)
- [ ] Testes de integração (0%)

## 🎓 RECOMENDAÇÕES FINAIS

1. **Priorize** corrigir a API de consultas do paciente
2. **Implemente** as regras de negócio pendentes
3. **Adicione** testes de integração para as APIs
4. **Documente** o código com comentários
5. **Revise** segurança antes do deploy em produção
6. **Faça** backup do banco de dados regularmente

## 📞 SUPORTE

### Em caso de dúvidas:
1. Consulte a documentação em `/docs`
2. Verifique os logs dos containers
3. Acesse o Swagger em http://localhost:8000/docs
4. Revise este guia de próximos passos

---

**Última Atualização**: 02/11/2025 04:33
**Versão**: 1.0.0
