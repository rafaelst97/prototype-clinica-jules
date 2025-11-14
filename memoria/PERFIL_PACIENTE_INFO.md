# 📋 Perfil do Paciente - Informações e Limitações

## ✅ Funcionalidades Implementadas

### 1. **Dados Carregados do PostgreSQL**
Todos os dados exibidos na tela de perfil vêm diretamente do banco de dados PostgreSQL:
- ✅ Nome completo
- ✅ CPF (com máscara: XXX.XXX.XXX-XX)
- ✅ Telefone (com máscara: (XX) XXXXX-XXXX)
- ✅ E-mail
- ✅ Convênio (carregado dinamicamente do banco)

### 2. **Campos Editáveis**
O paciente pode atualizar os seguintes campos:
- ✅ **Nome completo**
- ✅ **Telefone** (máscara aplicada automaticamente)
- ✅ **Convênio** (lista carregada do banco PostgreSQL)

### 3. **Campos Não Editáveis** (por decisão de negócio)
- ❌ **CPF**: Documento não pode ser alterado (apenas visualização)
- ❌ **E-mail**: Não pode ser alterado pelo paciente (campo desabilitado)
  - **Motivo**: E-mail é usado como identificador único para login
  - **Alternativa**: Se precisar alterar e-mail, deve ser feito por administrador

---

## 🔒 Regras de Negócio do Backend

### Endpoint PUT `/pacientes/perfil/{id}`
**Aceita apenas 3 campos:**
1. `nome` (string)
2. `telefone` (string, apenas números)
3. `id_plano_saude_fk` (integer ou null)

**NÃO aceita:**
- ❌ `email` - Identificador único não pode ser alterado
- ❌ `cpf` - Documento permanente
- ❌ `data_nascimento` - Dado cadastral fixo
- ❌ `endereco` - Não faz parte do modelo atual

---

## 🏥 Convênios Disponíveis

Lista carregada dinamicamente do PostgreSQL (`plano_saude`):
1. **Unimed** - Cobertura completa nacional
2. **SulAmérica** - Plano nacional com cobertura internacional
3. **Bradesco Saúde** - Cobertura nacional
4. **Amil** - Rede credenciada nacional
5. **NotreDame Intermédica** - Cobertura regional Sul
6. **Particular** - Atendimento particular sem convênio

---

## 🔄 Fluxo de Atualização

```javascript
1. Usuário edita nome, telefone ou convênio
2. Clica em "Salvar Alterações"
3. JavaScript remove máscara do telefone
4. Envia para API: { nome, telefone, id_plano_saude_fk }
5. Backend valida e atualiza PostgreSQL
6. Frontend recarrega dados atualizados
7. Exibe mensagem de sucesso
```

---

## 🐛 Debug e Logs

### Console do navegador mostra:
```
📊 Carregando perfil do paciente: {id}
✅ Perfil carregado do PostgreSQL: {dados}
🏥 Carregando convênios do PostgreSQL...
✅ {N} convênios carregados. Selecionado: {id}
📤 Enviando atualização para PostgreSQL: {dados}
✅ Perfil atualizado: {resultado}
```

---

## 📊 Validações Frontend

### Telefone:
- Aceita 10 ou 11 dígitos
- Máscara automática: `(XX) XXXX-XXXX` ou `(XX) XXXXX-XXXX`
- Remove máscara antes de enviar para API

### Nome:
- Campo obrigatório
- Sem validação específica (aceita qualquer texto)

### Convênio:
- Opcional (pode selecionar "Particular")
- Valida se plano existe no banco antes de salvar

---

## 🎯 Próximas Melhorias Possíveis

1. **Alterar senha** (formulário já existe, falta implementar backend)
2. **Validação de CPF** (apenas visual, não edita)
3. **Histórico de alterações** (auditoria)
4. **Upload de foto de perfil**
5. **Alterar e-mail** (via solicitação ao admin)

---

## 📝 Resumo das Correções Aplicadas

### Problema 1: Email não atualiza
**Causa**: Backend não aceita campo `email` no PUT  
**Solução**: Campo desabilitado no HTML com mensagem explicativa

### Problema 2: Convênio não atualiza
**Causa**: Select não estava conectado à API  
**Solução**: 
- Criado endpoint GET `/pacientes/planos-saude`
- JavaScript carrega planos do banco
- Form envia `id_plano_saude_fk` correto

### Problema 3: CPF sem máscara
**Causa**: Função de formatação não existia  
**Solução**: 
- Criada função `formatarCPF()`
- Aplicada ao carregar perfil

---

## ✅ Status Final

| Campo | Carrega? | Máscara? | Atualiza? | Observação |
|-------|----------|----------|-----------|------------|
| CPF | ✅ | ✅ | ❌ | Não editável (regra de negócio) |
| Nome | ✅ | - | ✅ | Editável |
| Telefone | ✅ | ✅ | ✅ | Editável com máscara |
| Email | ✅ | - | ❌ | Não editável (regra de negócio) |
| Convênio | ✅ | - | ✅ | Editável, lista do banco |

---

**Documentado em:** 03/11/2024  
**Backend:** FastAPI + PostgreSQL  
**Frontend:** Vanilla JavaScript  
