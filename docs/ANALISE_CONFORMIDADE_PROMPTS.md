# 📋 Análise de Conformidade com Casos de Uso (Pasta Prompts)

**Data:** 02/11/2025  
**Status:** 🔍 **EM ANÁLISE**

---

## 🎯 Casos de Uso Documentados (CasosDeUso.txt)

### ✅ **PACIENTE** (6 casos de uso)

| # | Caso de Uso | Implementado? | Backend | Frontend | Testado E2E? |
|---|-------------|---------------|---------|----------|--------------|
| 1 | Cadastrar Paciente | ✅ SIM | `/pacientes/cadastro` | `paciente/cadastro.html` | ✅ SIM (12 testes) |
| 2 | Login do Paciente | ✅ SIM | `/auth/login` | `paciente/login.html` | ✅ SIM (3 testes) |
| 3 | Agendar Consulta | ✅ SIM | `/pacientes/consultas` | `paciente/agendar.html` | ⚠️ PARCIAL |
| 4 | Visualizar Consultas | ✅ SIM | `/pacientes/consultas` | `paciente/consultas.html` | ❌ NÃO |
| 5 | Cancelar Consulta | ✅ SIM | `/pacientes/consultas/{id}/cancelar` | `paciente/consultas.html` | ⚠️ PARCIAL (1 teste) |
| 6 | **Reagendar Consulta** | ❌ **NÃO** | ❌ Falta endpoint | ❌ Falta UI | ❌ NÃO |

---

### ⚠️ **MÉDICO** (5 casos de uso)

| # | Caso de Uso | Implementado? | Backend | Frontend | Testado E2E? |
|---|-------------|---------------|---------|----------|--------------|
| 1 | Gerenciar Horários de Trabalho | ✅ SIM | `/medicos/horarios` | `medico/horarios.html` | ❌ NÃO |
| 2 | Visualizar Consultas Agendadas | ✅ SIM | `/medicos/consultas` | `medico/consultas.html` | ❌ NÃO |
| 3 | Registrar Observações da Consulta | ✅ SIM | `/medicos/observacoes` | `medico/consultas.html` | ❌ NÃO |
| 4 | **Bloquear Horários** | ⚠️ **PARCIAL** | ❌ Falta endpoint dedicado | ❌ Falta UI | ❌ NÃO |
| 5 | Visualizar Observações da Consulta | ✅ SIM | `/medicos/consultas/{id}` | `medico/consultas.html` | ❌ NÃO |

---

### ⚠️ **ADMINISTRADOR** (5 casos de uso)

| # | Caso de Uso | Implementado? | Backend | Frontend | Testado E2E? |
|---|-------------|---------------|---------|----------|--------------|
| 1 | Gerar Relatórios em PDF | ✅ SIM | `/admin/relatorios/pdf` | `admin/relatorios.html` | ⚠️ PARCIAL (1 teste) |
| 2 | Gerenciar Cadastro de Médicos | ✅ SIM | `/admin/medicos` | `admin/medicos.html` | ⚠️ PARCIAL (1 teste) |
| 3 | Gerenciar Planos de Saúde | ✅ SIM | `/admin/convenios` | `admin/convenios.html` | ❌ NÃO |
| 4 | **Desbloquear Contas de Pacientes** | ⚠️ **PARCIAL** | ⚠️ Existe lógica, falta endpoint | ❌ Falta UI | ❌ NÃO |
| 5 | Visualizar Observações da Consulta | ✅ SIM | `/admin/observacoes/{id}` | N/A | ❌ NÃO |

---

## 🚨 **FUNCIONALIDADES CRÍTICAS FALTANDO**

### 1. ❌ **Reagendar Consulta (PACIENTE)** - CRÍTICO
**Status:** NÃO IMPLEMENTADO  
**Impacto:** Alto - Caso de Uso explícito no documento  
**O que falta:**
- Backend: Endpoint `PUT /pacientes/consultas/{id}/reagendar`
- Frontend: Botão "Reagendar" e modal de seleção de nova data
- Validação: Mesmas regras de agendamento (24h antecedência, horários disponíveis)

---

### 2. ❌ **Bloquear Horários (MÉDICO)** - CRÍTICO
**Status:** PARCIALMENTE IMPLEMENTADO  
**Implementado:**
- ✅ Lógica de bloqueio por data no código (`validar_bloqueio_horario`)
- ✅ Endpoint para marcar consulta `bloqueada`

**O que falta:**
- ❌ Endpoint dedicado `POST /medicos/horarios/bloquear` para bloquear períodos sem consulta
- ❌ Frontend: Interface para médico bloquear horários (férias, compromissos, etc)
- ❌ UI: Visualização de horários bloqueados em vermelho na agenda

---

### 3. ❌ **Desbloquear Contas de Pacientes (ADMIN)** - IMPORTANTE
**Status:** PARCIALMENTE IMPLEMENTADO  
**Implementado:**
- ✅ Campo `esta_bloqueado` na tabela Paciente
- ✅ Validação de bloqueio no agendamento
- ✅ Lógica de bloqueio automático após 3 faltas

**O que falta:**
- ❌ Endpoint `PUT /admin/pacientes/{id}/desbloquear`
- ❌ Frontend: Botão de desbloqueio na interface de admin
- ❌ UI: Indicador visual de pacientes bloqueados
- ❌ Notificação ao paciente sobre desbloqueio

---

## 📊 **Resumo Estatístico**

### Implementação de Casos de Uso
- **Total de Casos de Uso:** 16
- **Totalmente Implementados:** 11 (69%)
- **Parcialmente Implementados:** 2 (13%)
- **Não Implementados:** 3 (19%)

### Cobertura de Testes E2E
- **Casos de Uso Testados:** 6 (38%)
- **Casos de Uso NÃO Testados:** 10 (62%)
- **Testes E2E Atuais:** 25 testes
- **Testes E2E Necessários:** ~50-60 testes (estimativa)

---

## 🎯 **Regras de Negócio (EstudoDeCaso.txt)**

| # | Regra de Negócio | Implementado? | Testado E2E? |
|---|-----------------|---------------|--------------|
| 1 | Cancelamento/remarcação até 24h antes | ✅ SIM | ⚠️ PARCIAL |
| 2 | Máximo 2 consultas futuras por paciente | ✅ SIM | ⚠️ PARCIAL |
| 3 | Médico define horários semanais | ✅ SIM | ❌ NÃO |
| 4 | Sistema evita conflito de agendamento | ✅ SIM | ❌ NÃO |
| 5 | Bloqueio após 3 faltas consecutivas | ✅ SIM | ❌ NÃO |
| 6 | Liberação pela administração | ⚠️ PARCIAL | ❌ NÃO |

---

## 📝 **Modelo de Dados (MER_Estrutura.txt)**

### Entidades Implementadas
✅ ESPECIALIDADE  
✅ PLANO_SAUDE (Convenio)  
✅ ADMINISTRADOR  
✅ MEDICO  
✅ PACIENTE  
✅ RELATORIO  
✅ HORARIO_TRABALHO  
✅ CONSULTA  
✅ OBSERVACAO  

**Conformidade:** 100% - Todas as 9 entidades documentadas estão implementadas

---

## 🏗️ **Arquitetura (ArquiteturaSistema.txt)**

### Camadas Implementadas
✅ **Frontend:** HTML + CSS + JavaScript (Vanilla)  
✅ **Backend:** Python + FastAPI  
✅ **Banco de Dados:** PostgreSQL  
✅ **Comunicação:** HTTP/JSON REST API  

**Conformidade:** 100% - Arquitetura conforme especificação

---

## 🚀 **PLANO DE AÇÃO PARA 100% DE CONFORMIDADE**

### Fase 1: Implementação de Funcionalidades Faltantes (8-12 horas)

#### 1.1 Reagendar Consulta (Paciente)
- [ ] Backend: Criar endpoint `PUT /pacientes/consultas/{id}/reagendar`
- [ ] Validações: 24h antecedência, horário disponível, limite 2 consultas
- [ ] Frontend: Adicionar modal de reagendamento em `consultas.html`
- [ ] JavaScript: Implementar lógica em `paciente-consultas.js`

#### 1.2 Bloquear Horários (Médico)
- [ ] Backend: Criar endpoint `POST /medicos/horarios/bloquear`
- [ ] Suportar: Data início/fim, motivo do bloqueio
- [ ] Frontend: Adicionar interface de bloqueio em `horarios.html`
- [ ] Visualização: Mostrar bloqueios em vermelho na agenda

#### 1.3 Desbloquear Contas (Admin)
- [ ] Backend: Criar endpoint `PUT /admin/pacientes/{id}/desbloquear`
- [ ] Registrar: Histórico de bloqueios/desbloqueios
- [ ] Frontend: Adicionar botão de desbloqueio em `pacientes.html`
- [ ] UI: Indicador visual de status bloqueado

---

### Fase 2: Testes E2E Completos (16-20 horas)

#### 2.1 Testes por Caso de Uso (1 arquivo por ator)

**test_e2e_paciente_completo.py** (~15-20 testes)
- [ ] UC1: Cadastrar Paciente (já existem 12 testes ✅)
- [ ] UC2: Login do Paciente (já existem 3 testes ✅)
- [ ] UC3: Agendar Consulta (5 cenários completos)
- [ ] UC4: Visualizar Consultas (futura, passada, filtros)
- [ ] UC5: Cancelar Consulta (cenários de sucesso e erro)
- [ ] UC6: Reagendar Consulta (novo - 3-4 cenários)

**test_e2e_medico_completo.py** (~12-15 testes)
- [ ] Login de Médico
- [ ] UC1: Gerenciar Horários (criar, editar, excluir)
- [ ] UC2: Visualizar Consultas Agendadas (hoje, semana, filtros)
- [ ] UC3: Registrar Observações (criar, editar)
- [ ] UC4: Bloquear Horários (novo - período, único dia)
- [ ] UC5: Visualizar Observações (listagem)

**test_e2e_admin_completo.py** (~15-18 testes)
- [ ] Login de Administrador
- [ ] UC1: Gerar Relatórios PDF (por médico, especialidade, período)
- [ ] UC2: Gerenciar Médicos (criar, editar, excluir, buscar)
- [ ] UC3: Gerenciar Convênios (CRUD completo)
- [ ] UC4: Desbloquear Contas (novo - casos de bloqueio)
- [ ] UC5: Visualizar Observações

**test_e2e_regras_negocio.py** (~8-10 testes)
- [ ] RN1: Cancelamento 24h (sucesso e erro)
- [ ] RN2: Limite 2 consultas (bloqueio no 3º agendamento)
- [ ] RN3: Horários médico semanais (validação)
- [ ] RN4: Conflito de agendamento (mesmo horário)
- [ ] RN5: Bloqueio 3 faltas (automático)
- [ ] RN6: Desbloqueio admin (manual)

---

### Fase 3: Documentação e Validação (2-4 horas)

- [ ] Atualizar este documento com status 100%
- [ ] Criar matriz de rastreabilidade (Caso de Uso ↔ Teste)
- [ ] Gerar relatório final de conformidade
- [ ] Evidências de testes (screenshots)

---

## 📊 **Estimativa de Trabalho**

| Fase | Atividade | Tempo Estimado |
|------|-----------|----------------|
| 1 | Implementar funcionalidades faltantes | 8-12 horas |
| 2 | Criar testes E2E completos | 16-20 horas |
| 3 | Documentação final | 2-4 horas |
| **TOTAL** | **Conformidade 100%** | **26-36 horas** |

---

## ✅ **Critérios de Aceitação**

Para considerar o projeto **100% conforme** aos Prompts:

1. ✅ Todas as 16 funcionalidades (Casos de Uso) implementadas
2. ✅ Todas as 6 Regras de Negócio validadas
3. ✅ Todas as 9 entidades do MER funcionais
4. ✅ 50-60 testes E2E cobrindo todos os casos de uso
5. ✅ Matriz de rastreabilidade documentada
6. ✅ 100% dos testes passando

---

**Próximo Passo:** Iniciar Fase 1 - Implementação de funcionalidades faltantes
