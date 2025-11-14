# Mapa de Navegação - Sistema Clínica Saúde+

## 🗺️ Fluxo de Navegação do Sistema

### Página Inicial (index.html)
```
┌─────────────────────────────────────┐
│     CLÍNICA SAÚDE+                  │
│  Sistema de Agendamento             │
├─────────────────────────────────────┤
│                                     │
│  [👤 Paciente]                      │
│  [👨‍⚕️ Médico]                        │
│  [⚙️ Administração]                  │
│                                     │
└─────────────────────────────────────┘
```

---

## 👤 MÓDULO PACIENTE

### 1. Login (paciente/login.html)
- ✅ Login com e-mail e senha
- 🔗 Link para cadastro
- 🔗 Link voltar à página inicial

### 2. Cadastro (paciente/cadastro.html)
- ✅ Formulário completo de cadastro
- 📋 Campos: CPF, nome, telefone, e-mail, senha, convênio
- 🔗 Retorna para login após cadastro

### 3. Dashboard (paciente/dashboard.html)
```
┌─────────────────────────────────────────────────┐
│  Navegação: [Início] [Nova Consulta]           │
│            [Minhas Consultas] [Perfil]          │
├─────────────────────────────────────────────────┤
│                                                 │
│  📅 PRÓXIMAS CONSULTAS                          │
│  ├─ Consulta 1: Data, Médico, Especialidade    │
│  └─ Consulta 2: Data, Médico, Especialidade    │
│                                                 │
│  🏥 AÇÕES RÁPIDAS                               │
│  ├─ [Agendar Nova Consulta]                    │
│  ├─ [Ver Histórico]                             │
│  └─ [Editar Perfil]                             │
│                                                 │
│  📊 RESUMO DA CONTA                             │
│  ├─ Total de consultas: 12                     │
│  ├─ Consultas agendadas: 2                     │
│  └─ Status: Ativo                               │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 4. Agendar Consulta (paciente/agendar.html)
**Fluxo de Agendamento:**
```
1. Selecionar Especialidade
   ↓
2. Selecionar Médico (filtrado por especialidade)
   ↓
3. Selecionar Data (mínimo: amanhã)
   ↓
4. Selecionar Horário (disponíveis do médico)
   ↓
5. Adicionar Observações (opcional)
   ↓
6. Confirmar Agendamento
   ↓
7. Redirecionar para Minhas Consultas
```

### 5. Minhas Consultas (paciente/consultas.html)
- 📅 **Consultas Futuras**: Com opções de remarcar/cancelar
- 📜 **Histórico**: Consultas realizadas e canceladas
- ⚠️ **Regra**: Cancelamento até 24h antes

### 6. Perfil (paciente/perfil.html)
- ✏️ Editar informações pessoais
- 🔒 Alterar senha
- ℹ️ CPF não pode ser alterado

---

## 👨‍⚕️ MÓDULO MÉDICO

### 1. Login (medico/login.html)
- ✅ Login com CRM e senha
- 🔗 Voltar à página inicial

### 2. Dashboard (medico/dashboard.html)
```
┌─────────────────────────────────────────────────┐
│  Navegação: [Início] [Agenda] [Consultas]      │
│            [Horários]                            │
├─────────────────────────────────────────────────┤
│                                                 │
│  📅 CONSULTAS DE HOJE                           │
│  ├─ 09:00 - Paciente 1                         │
│  ├─ 10:30 - Paciente 2                         │
│  ├─ 14:00 - Paciente 3                         │
│  └─ 15:30 - Paciente 4                         │
│                                                 │
│  📊 ESTATÍSTICAS                                │
│  ├─ Consultas hoje: 4                          │
│  ├─ Consultas esta semana: 18                  │
│  └─ Horários bloqueados: 2                     │
│                                                 │
│  🏥 AÇÕES RÁPIDAS                               │
│  ├─ [Ver Agenda Completa]                      │
│  ├─ [Gerenciar Horários]                       │
│  └─ [Bloquear Horário]                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 3. Agenda (medico/agenda.html)
- 📅 Visualização de todas as consultas agendadas
- 🔍 Filtro por data
- ⛔ Visualização de horários bloqueados
- 🔓 Opção de desbloquear horários

### 4. Consultas (medico/consultas.html)
- 👤 Informações do paciente
- 📝 Observações do paciente
- ✍️ Registro de diagnóstico
- 💊 Prescrições e recomendações
- 💾 Salvar observações (visível apenas para médico e admin)

### 5. Gerenciar Horários (medico/horarios.html)
**Configuração Semanal:**
- Segunda a Sexta: Definir horários disponíveis
- ⏰ Horários manhã e tarde
- ⛔ Bloquear horários específicos
- 📝 Adicionar motivo do bloqueio

---

## ⚙️ MÓDULO ADMINISTRAÇÃO

### 1. Login (admin/login.html)
- ✅ Login com usuário e senha
- 🔗 Voltar à página inicial

### 2. Dashboard (admin/dashboard.html)
```
┌─────────────────────────────────────────────────┐
│  Navegação: [Início] [Médicos] [Pacientes]     │
│            [Relatórios] [Convênios]             │
├─────────────────────────────────────────────────┤
│                                                 │
│  📊 ESTATÍSTICAS GERAIS                         │
│  ├─ Pacientes: 245                             │
│  ├─ Médicos: 15                                │
│  ├─ Consultas (mês): 128                       │
│  └─ Cancelamentos: 8                           │
│                                                 │
│  🎯 AÇÕES RÁPIDAS                               │
│  ├─ [Cadastrar Médico]                         │
│  ├─ [Gerar Relatório]                          │
│  ├─ [Gerenciar Convênios]                      │
│  └─ [Ver Pacientes]                            │
│                                                 │
│  📅 CONSULTAS RECENTES                          │
│  └─ Listagem das últimas consultas             │
│                                                 │
│  ⚠️ ALERTAS                                     │
│  ├─ Pacientes com risco de bloqueio            │
│  └─ Médicos sem horários configurados          │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 3. Gerenciar Médicos (admin/medicos.html)
- 📋 Lista de todos os médicos
- ➕ Cadastrar novo médico
  - Nome, CRM, Especialidade
  - Telefone, E-mail
  - Convênios aceitos
- ✏️ Editar informações
- 🔴 Ativar/Desativar médico

### 4. Gerenciar Pacientes (admin/pacientes.html)
- 📋 Lista de todos os pacientes
- 🔍 Busca por nome ou CPF
- 👁️ Ver detalhes do paciente
- ⚠️ **Alertas de faltas**:
  - Amarelo: 2 faltas consecutivas
  - Vermelho: Bloqueado (3 faltas)
- 🔓 Desbloquear paciente

### 5. Relatórios (admin/relatorios.html)
**Tipos de Relatórios em PDF:**

1. **📊 Consultas por Médico**
   - Filtro: Médico específico ou todos
   - Período: Data inicial e final
   
2. **🏥 Consultas por Especialidade**
   - Filtro: Especialidade específica ou todas
   - Período: Data inicial e final
   
3. **❌ Taxa de Cancelamentos**
   - Período: Data inicial e final
   - Filtro: Motivo do cancelamento
   
4. **👥 Pacientes Mais Frequentes**
   - Período: Data inicial e final
   - Quantidade: Top 10, 20 ou 50

### 6. Gerenciar Convênios (admin/convenios.html)
- 📋 Lista de convênios aceitos
- ➕ Cadastrar novo convênio
- ✏️ Editar convênio
- 🔴 Ativar/Desativar convênio
- 📊 Estatísticas por convênio

---

## 🔄 Fluxos Principais

### Fluxo 1: Paciente Agendando Consulta
```
Login → Dashboard → Agendar Consulta → Selecionar Especialidade 
→ Selecionar Médico → Selecionar Data → Selecionar Horário 
→ Confirmar → Minhas Consultas
```

### Fluxo 2: Médico Registrando Consulta
```
Login → Dashboard → Agenda → Ver Detalhes da Consulta 
→ Registrar Observações → Salvar → Voltar à Agenda
```

### Fluxo 3: Admin Gerando Relatório
```
Login → Dashboard → Relatórios → Selecionar Tipo de Relatório 
→ Definir Filtros → Gerar PDF
```

### Fluxo 4: Médico Configurando Horários
```
Login → Dashboard → Gerenciar Horários → Definir Horários Semanais 
→ Bloquear Horários Específicos → Salvar
```

---

## 🎨 Padrões de Interface

### Cores do Sistema
- **Primária (Azul)**: `#3498db` - Botões e ações principais
- **Secundária (Verde)**: `#27ae60` - Confirmações e sucesso
- **Terciária (Vermelho)**: `#e74c3c` - Cancelamentos e alertas
- **Fundo**: `#ecf0f1` - Áreas de conteúdo
- **Texto**: `#2c3e50` - Texto principal

### Componentes Principais
- 📋 **Cards**: Agrupamento de informações
- 📊 **Tabelas**: Listagem de dados
- 🔘 **Botões**: Ações do usuário
- 📝 **Formulários**: Entrada de dados
- ⚠️ **Alertas**: Notificações e avisos

---

## 📱 Responsividade

O sistema é totalmente responsivo e se adapta a:
- 💻 **Desktop**: Layout completo com grid de 2 colunas
- 📱 **Tablet**: Layout adaptado
- 📱 **Mobile**: Layout em coluna única

---

**Versão**: 1.0  
**Data**: Outubro 2025  
**Status**: Protótipo de Navegação
