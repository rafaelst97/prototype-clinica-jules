# 🚀 GUIA COMPLETO - DEPLOY NO RENDER

## ✅ Status Atual

### Backend
- ✅ **Serviço**: `clinica-saude-backend` (Web Service)
- ✅ **URL**: https://clinica-saude-backend.onrender.com
- ✅ **Status**: ONLINE e funcionando
- ✅ **Último commit**: `b8ee28d` - feat: Add database population endpoint

### Frontend
- ⏳ **Serviço**: `clinica-saude-frontend` (Static Site)
- ⏳ **URL**: https://clinica-saude-frontend.onrender.com
- ⏳ **Status**: Precisa de redeploy (commit `ae9caf6`)
- ⏳ **Pendência**: Deploy manual para atualizar com config.js

### Banco de Dados
- ✅ **Serviço**: `clinica-saude-db` (PostgreSQL 15)
- ✅ **Status**: ONLINE
- ⚠️ **Dados**: VAZIO - precisa popular

---

## 📋 PASSO A PASSO - FINALIZAR DEPLOY

### 1️⃣ Deploy do Frontend (URGENTE)

**O que fazer:**
1. Acesse https://dashboard.render.com
2. Clique no serviço `clinica-saude-frontend`
3. Clique no botão **"Manual Deploy"** (canto superior direito)
4. Selecione **"Deploy latest commit"**
5. Aguarde o deploy (~2-3 minutos)

**Resultado esperado:**
- Frontend vai carregar com `config.js`
- Todas as chamadas de API vão para `https://clinica-saude-backend.onrender.com`
- Não vai mais tentar conectar em `localhost:8000`

---

### 2️⃣ Aguardar Deploy do Backend (AUTOMÁTICO)

**O que acontece:**
- Render detecta o commit `b8ee28d` automaticamente
- Inicia build e deploy do backend
- Adiciona o endpoint `/admin/popular-dados`

**Como acompanhar:**
1. Acesse o serviço `clinica-saude-backend` no Render Dashboard
2. Aba **"Logs"** - veja o processo de build/deploy
3. Aguarde status **"Live"**

**Tempo estimado:** 5-10 minutos

---

### 3️⃣ Popular Banco de Dados (DEPOIS DO BACKEND ESTAR LIVE)

**Opção A: Executar script localmente (RECOMENDADO)**

```powershell
# No PowerShell do seu computador
cd "c:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto\backend"

python populate_render.py
```

**O que o script faz:**
- Conecta no backend do Render via HTTPS
- Chama o endpoint `/admin/popular-dados`
- Cria todos os dados de teste
- Mostra as credenciais criadas

**Opção B: Via navegador (SIMPLES)**

1. Abra o navegador
2. Acesse: https://clinica-saude-backend.onrender.com/docs
3. Procure o endpoint **POST /admin/popular-dados**
4. Clique em **"Try it out"**
5. Clique em **"Execute"**

**Opção C: Via curl**

```powershell
curl -X POST "https://clinica-saude-backend.onrender.com/admin/popular-dados"
```

---

## 🔑 Credenciais de Teste (após popular)

### Admin
- **Email**: admin@clinica.com
- **Senha**: admin123
- **URL**: https://clinica-saude-frontend.onrender.com/admin/login.html

### Médico
- **Email**: joao1@clinica.com
- **Senha**: medico123
- **URL**: https://clinica-saude-frontend.onrender.com/medico/login.html

### Paciente
- **Email**: maria@email.com
- **Senha**: paciente123
- **URL**: https://clinica-saude-frontend.onrender.com/paciente/login.html

---

## 🧪 Testar Sistema Completo

### 1. Testar Backend
```powershell
# Health check
curl https://clinica-saude-backend.onrender.com/health

# Resposta esperada:
# {"status":"healthy"}
```

### 2. Testar Login
1. Acesse: https://clinica-saude-frontend.onrender.com/admin/login.html
2. Use: admin@clinica.com / admin123
3. Deve redirecionar para dashboard

### 3. Verificar Console do Navegador
Abra DevTools (F12) e veja:
```
[Config] Ambiente detectado: Render
[Config] API URL configurada: https://clinica-saude-backend.onrender.com
```

---

## 🔧 Solução de Problemas

### ❌ Erro: "API URL is undefined"
**Solução:** Frontend não foi redeployado
- Faça Manual Deploy do frontend no Render

### ❌ Erro: "Failed to fetch"
**Solução:** Backend ainda não está Live
- Aguarde deploy do backend completar
- Verifique logs em Render Dashboard

### ❌ Erro: "Banco de dados já contém dados"
**Solução:** Dados já foram populados antes
- Pode ignorar ou limpar com `--limpar`:
```powershell
python populate_render.py --limpar
```

### ❌ Erro: "401 Unauthorized" ao popular
**Solução:** Endpoint é público, não precisa autenticação
- Verifique se o backend está Live
- Tente novamente em 1 minuto

---

## 📊 Dados Criados

Após popular o banco, terá:
- **Usuários**: 9 (1 admin, 3 médicos, 5 pacientes)
- **Médicos**: 3 com especialidades diferentes
- **Pacientes**: 5 cadastrados
- **Convênios**: 3 (Unimed, Amil, Bradesco)
- **Especialidades**: 5 (Cardiologia, Dermatologia, Pediatria, Ortopedia, Ginecologia)
- **Horários**: Médicos com agenda de segunda a sexta (8h-12h e 14h-18h)

---

## ⏱️ Cronograma de Execução

| Passo | Ação | Tempo | Status |
|-------|------|-------|--------|
| 1 | Deploy Frontend (Manual) | 2-3 min | ⏳ Pendente |
| 2 | Deploy Backend (Auto) | 5-10 min | ⏳ Em progresso |
| 3 | Popular Banco | 1 min | ⏳ Aguardando |
| 4 | Testar Sistema | 5 min | ⏳ Aguardando |

**TOTAL ESTIMADO:** 15-20 minutos

---

## 🎯 Próximos Passos (após tudo funcionando)

1. ✅ Sistema online e funcional
2. 📝 Criar documentação de uso
3. 🔐 Configurar domínio personalizado (opcional)
4. 📊 Monitorar uso e performance
5. 🚀 Fazer melhorias baseadas em feedback

---

## 📞 Suporte

Se algo não funcionar:
1. Verifique os logs no Render Dashboard
2. Teste o health endpoint do backend
3. Verifique console do navegador (F12)
4. Confirme que todos os deploys estão Live

---

**Última atualização:** 2025-01-12
**Versão:** v2.0.0
**Commits importantes:**
- `b8ee28d` - Endpoint de população de dados
- `ae9caf6` - config.js em todos os HTMLs
- `9937b22` - Criação do config.js
