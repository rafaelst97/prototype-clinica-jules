# 🚀 Deploy Rápido - Passo a Passo

## ⚡ Opção 1: Render.com (MAIS FÁCIL - 5 minutos)

### 1️⃣ Acesse e faça login:
```
https://render.com/
```
👉 Login com GitHub

### 2️⃣ Crie o PostgreSQL:
1. **New** > **PostgreSQL**
2. Nome: `clinica-saude-db`
3. Region: **Oregon**
4. Plan: **Free**
5. **Create Database**

📋 Copie a **Internal Database URL** que aparecerá

### 3️⃣ Crie o Backend:
1. **New** > **Web Service**
2. Connect repository: `rafaelst97/prototype-melhoria`
3. Preencha:
   - Name: `clinica-saude-backend`
   - Region: **Oregon**
   - Branch: **main**
   - Root Directory: `backend`
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables** (Add):
   ```
   DATABASE_URL = [cole aqui a URL do passo 2]
   SECRET_KEY = sua_chave_secreta_aqui_123
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ```

5. Plan: **Free**
6. **Create Web Service**

### 4️⃣ Crie o Frontend:
1. **New** > **Static Site**
2. Repository: `rafaelst97/prototype-melhoria`
3. Preencha:
   - Name: `clinica-saude-frontend`
   - Branch: **main**
   - Build Command: (deixar vazio)
   - Publish Directory: `.`

4. Plan: **Free**
5. **Create Static Site**

### 5️⃣ Aguarde o Deploy:
- Backend: ~5 minutos
- Frontend: ~2 minutos
- Database: pronto instantaneamente

### ✅ URLs finais:
- **Frontend:** `https://clinica-saude-frontend.onrender.com`
- **Backend:** `https://clinica-saude-backend.onrender.com`
- **API Docs:** `https://clinica-saude-backend.onrender.com/docs`

---

## ⚡ Opção 2: Railway.app (MAIS RÁPIDO - 3 minutos)

### 1️⃣ Instale Railway CLI:
```powershell
npm install -g @railway/cli
```

### 2️⃣ Login e Deploy:
```bash
# Login
railway login

# Criar projeto
railway init

# Deploy tudo
railway up

# Adicionar PostgreSQL
railway add --database postgresql

# Abrir dashboard
railway open
```

### 3️⃣ Configure Environment:
No dashboard Railway:
1. Backend > Variables:
   ```
   SECRET_KEY = sua_chave_secreta
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ```

### ✅ Pronto! Railway configura tudo automaticamente.

**Custo:** $5/mês de crédito grátis (suficiente para teste)

---

## ⚡ Opção 3: Fly.io (MAIS RECURSOS - 10 minutos)

### 1️⃣ Instale Fly CLI:
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### 2️⃣ Login:
```bash
fly auth login
```

### 3️⃣ Deploy Backend:
```bash
cd backend
fly launch --name clinica-saude-backend --region gru
fly deploy
```

### 4️⃣ Adicione PostgreSQL:
```bash
fly postgres create --name clinica-saude-db --region gru
fly postgres attach clinica-saude-db
```

### 5️⃣ Configure Secrets:
```bash
fly secrets set SECRET_KEY=sua_chave_secreta
fly secrets set ALGORITHM=HS256
fly secrets set ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### ✅ URLs:
```bash
fly status
fly open
```

**Custo:** Completamente GRÁTIS (3 VMs de 256MB + PostgreSQL 3GB)

---

## 📊 Qual Escolher?

| Critério | Render | Railway | Fly.io |
|----------|--------|---------|--------|
| **Facilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Velocidade Deploy** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Custo** | GRÁTIS | $5/mês | GRÁTIS |
| **PostgreSQL** | 500 MB | Ilimitado* | 3 GB |
| **Uptime** | 99% | 99.9% | 99.9% |
| **Região Brasil** | ❌ | ✅ | ✅ |

**Recomendação:**
- 🥇 **Iniciante?** → Render.com
- 🥈 **Profissional?** → Railway.app
- 🥉 **Recursos?** → Fly.io

---

## 🐛 Problemas Comuns

### Backend não inicia?
```bash
# Verificar logs
render logs -f clinica-saude-backend

# Ou no dashboard: Services > Backend > Logs
```

### Database error?
- Verificar se `DATABASE_URL` está correta
- Testar conexão: `psql $DATABASE_URL`

### Frontend não carrega API?
- Atualizar `js/config.js` com URL do backend
- Verificar CORS em `backend/app/main.py`

---

## 📞 Suporte

**Render:** https://render.com/docs  
**Railway:** https://docs.railway.app  
**Fly.io:** https://fly.io/docs

---

## 👥 Equipe

- **Caio César Sabino Soares**
- **Júlia Cansian Rocha**
- **Rafael dos Santos**

**UNIVALI - 2025**
