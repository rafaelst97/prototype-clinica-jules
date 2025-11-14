# Guia Rápido - Novas Funcionalidades

## Como Usar as Novas Funcionalidades do Sistema

---

## 1. Instalação e Configuração

### Passo 1: Instalar Dependências
```bash
cd backend
pip install -r requirements.txt
```

### Passo 2: Aplicar Migrações do Banco de Dados
```bash
alembic upgrade head
```

### Passo 3: Iniciar o Servidor
```bash
uvicorn app.main:app --reload
```

---

## 2. Observações Médicas

### Como Médico Registra Observação

**Endpoint**: `POST /medicos/observacoes`

**Exemplo de Request**:
```json
{
  "consulta_id": 1,
  "descricao": "Paciente apresentou melhora significativa. Recomendado continuar tratamento por mais 30 dias."
}
```

**Resposta**:
```json
{
  "id": 1,
  "consulta_id": 1,
  "descricao": "Paciente apresentou melhora significativa...",
  "data_criacao": "2025-10-26T10:30:00"
}
```

### Como Visualizar Observação

**Endpoint**: `GET /medicos/observacoes/{consulta_id}`

### Como Atualizar Observação

**Endpoint**: `PUT /medicos/observacoes/{consulta_id}`

**Exemplo**:
```json
{
  "descricao": "Observação atualizada com novos dados..."
}
```

---

## 3. Relatórios em PDF

### 3.1 Relatório de Consultas por Médico

**Endpoint**: `GET /admin/relatorios/consultas-por-medico?data_inicio=2025-10-01&data_fim=2025-10-31&formato=pdf`

**Parâmetros**:
- `data_inicio` (opcional): Data inicial do período
- `data_fim` (opcional): Data final do período
- `formato`: "json" ou "pdf"

**Como Gerar**:

**Em JSON** (para visualizar no navegador):
```
GET /admin/relatorios/consultas-por-medico?data_inicio=2025-10-01&data_fim=2025-10-31&formato=json
```

**Em PDF** (para download):
```
GET /admin/relatorios/consultas-por-medico?data_inicio=2025-10-01&data_fim=2025-10-31&formato=pdf
```

### 3.2 Relatório de Consultas por Especialidade

**Endpoint**: `GET /admin/relatorios/consultas-por-especialidade?formato=pdf`

### 3.3 Relatório de Cancelamentos

**Endpoint**: `GET /admin/relatorios/cancelamentos?formato=pdf`

**Dados Retornados**:
- Total de consultas no período
- Total de cancelamentos
- Total de remarcações
- Taxa de cancelamento em %

### 3.4 Relatório de Pacientes Frequentes

**Endpoint**: `GET /admin/relatorios/pacientes-frequentes?limite=20&formato=pdf`

**Parâmetros**:
- `limite`: Número de pacientes a retornar (padrão: 20)

### 3.5 Ver Histórico de Relatórios Gerados

**Endpoint**: `GET /admin/relatorios/historico`

---

## 4. Sistema de Bloqueio de Pacientes

### 4.1 Como Funciona o Bloqueio Automático

O sistema bloqueia automaticamente pacientes que:
- Faltarem a 3 consultas consecutivas sem aviso

**Status do Paciente**:
- `faltas_consecutivas`: Contador de faltas
- `usuario.bloqueado`: Status de bloqueio (true/false)

### 4.2 Como Administrador Desbloqueia Paciente

**Endpoint**: `PUT /admin/pacientes/{paciente_id}/desbloquear`

**Exemplo**:
```
PUT /admin/pacientes/123/desbloquear
```

**O que acontece**:
1. Define `usuario.bloqueado = false`
2. Zera `faltas_consecutivas = 0`
3. Paciente pode agendar novamente

### 4.3 Como Administrador Bloqueia Paciente Manualmente

**Endpoint**: `PUT /admin/pacientes/{paciente_id}/bloquear`

---

## 5. Agendamento de Consultas (Com Validações)

### 5.1 Limite de 2 Consultas Futuras

Ao tentar agendar uma terceira consulta, o sistema retorna:

**Erro**:
```json
{
  "detail": "Você já possui 2 consultas agendadas. Cancele uma para agendar outra."
}
```

**Solução**: Cancelar uma das consultas futuras primeiro.

### 5.2 Paciente Bloqueado

Ao tentar agendar estando bloqueado:

**Erro**:
```json
{
  "detail": "Sua conta está bloqueada. Entre em contato com a administração."
}
```

**Solução**: Contatar administração para desbloqueio.

---

## 6. Cancelamento de Consultas

### 6.1 Regra de 24h

**Endpoint**: `DELETE /pacientes/consultas/{consulta_id}`

**Exemplo de Request**:
```json
{
  "motivo_cancelamento": "Imprevisto de última hora"
}
```

**Se cancelar com menos de 24h**:
```json
{
  "detail": "Cancelamento deve ser feito com pelo menos 24h de antecedência"
}
```

---

## 7. Exemplos de Uso Completo

### 7.1 Fluxo do Paciente

1. **Cadastrar**:
```bash
POST /pacientes/cadastro
```

2. **Login**:
```bash
POST /auth/login
```

3. **Agendar Consulta** (máximo 2):
```bash
POST /pacientes/consultas
```

4. **Ver Consultas**:
```bash
GET /pacientes/consultas
```

5. **Cancelar** (até 24h antes):
```bash
DELETE /pacientes/consultas/{id}
```

### 7.2 Fluxo do Médico

1. **Login**:
```bash
POST /auth/login
```

2. **Ver Consultas do Dia**:
```bash
GET /medicos/consultas/hoje
```

3. **Registrar Observação**:
```bash
POST /medicos/observacoes
```

4. **Bloquear Horário**:
```bash
POST /medicos/bloqueios
```

### 7.3 Fluxo do Administrador

1. **Login**:
```bash
POST /auth/login
```

2. **Ver Dashboard**:
```bash
GET /admin/dashboard
```

3. **Gerar Relatório PDF**:
```bash
GET /admin/relatorios/consultas-por-medico?formato=pdf
```

4. **Desbloquear Paciente**:
```bash
PUT /admin/pacientes/{id}/desbloquear
```

5. **Ver Histórico de Relatórios**:
```bash
GET /admin/relatorios/historico
```

---

## 8. Testando com cURL

### 8.1 Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@clinica.com", "senha": "senha123"}'
```

### 8.2 Gerar Relatório PDF
```bash
curl -X GET "http://localhost:8000/admin/relatorios/consultas-por-medico?formato=pdf" \
  -H "Authorization: Bearer {seu_token}" \
  --output relatorio.pdf
```

### 8.3 Criar Observação
```bash
curl -X POST "http://localhost:8000/medicos/observacoes" \
  -H "Authorization: Bearer {seu_token}" \
  -H "Content-Type: application/json" \
  -d '{"consulta_id": 1, "descricao": "Paciente evoluindo bem"}'
```

---

## 9. Testando pelo Frontend

### 9.1 Para Administradores

No arquivo `js/admin-relatorios.js`, adicione botões para gerar relatórios:

```javascript
// Gerar Relatório de Consultas por Médico
async function gerarRelatorioMedicos() {
    const dataInicio = document.getElementById('dataInicio').value;
    const dataFim = document.getElementById('dataFim').value;
    
    window.open(
        `http://localhost:8000/admin/relatorios/consultas-por-medico?data_inicio=${dataInicio}&data_fim=${dataFim}&formato=pdf`,
        '_blank'
    );
}
```

### 9.2 Para Médicos

No arquivo `js/medico-consultas.js`, adicione função para observações:

```javascript
async function registrarObservacao(consultaId) {
    const descricao = document.getElementById('observacao').value;
    
    const response = await fetch('http://localhost:8000/medicos/observacoes', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            consulta_id: consultaId,
            descricao: descricao
        })
    });
    
    if (response.ok) {
        alert('Observação registrada com sucesso!');
    }
}
```

---

## 10. Dicas e Boas Práticas

### 10.1 Para Pacientes
- ⚠️ Não falte a consultas sem avisar
- ⚠️ Cancele com pelo menos 24h de antecedência
- ✅ Mantenha no máximo 2 consultas agendadas

### 10.2 Para Médicos
- ✅ Sempre registre observações após consultas
- ✅ Bloqueie horários com antecedência
- ✅ Mantenha a agenda sempre atualizada

### 10.3 Para Administradores
- ✅ Gere relatórios mensalmente
- ✅ Monitore taxa de cancelamentos
- ✅ Desbloqueie pacientes quando apropriado
- ✅ Acompanhe especialidades mais procuradas

---

## 11. Troubleshooting

### Erro: "Sua conta está bloqueada"
**Solução**: Contate a administração ou verifique suas faltas consecutivas.

### Erro: "Você já possui 2 consultas agendadas"
**Solução**: Cancele uma consulta antes de agendar outra.

### Erro: "Cancelamento deve ser feito com pelo menos 24h de antecedência"
**Solução**: Entre em contato com a clínica por telefone.

### Erro ao gerar PDF: "reportlab not found"
**Solução**: Execute `pip install reportlab==4.0.7`

---

## 12. Suporte

Para dúvidas ou problemas:
- Consulte a documentação em `/docs`
- Verifique logs do servidor
- Consulte o arquivo `IMPLEMENTACOES_26_10_2025.md`

---

**Última atualização**: 26 de Outubro de 2025
