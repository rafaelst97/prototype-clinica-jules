# 🌐 Guia de Deploy em Produção

## 📋 Índice
1. [Render.com (Recomendado)](#rendercom-recomendado)
2. [Railway.app](#railwayapp)
3. [Fly.io](#flyio)
4. [Vercel + Supabase](#vercel--supabase)
5. [Comparação de Plataformas](#comparação-de-plataformas)

---

## 🎯 Render.com (Recomendado)

### ✅ Por que Render?
- **100% Gratuito** para começar
- **PostgreSQL incluído** (500 MB)
- **SSL/HTTPS automático**
- **Deploy via Git** (push = deploy)
- **Sem cartão de crédito** no plano free
- **Sem dormir** (ao contrário do Heroku)

### 🚀 Deploy em 3 Passos

#### 1️⃣ Criar Conta no Render
```
https://render.com/
```
- Faça login com sua conta GitHub
- Autorize acesso ao repositório `prototype-melhoria`

#### 2️⃣ Criar Serviços via Dashboard

**A) PostgreSQL Database:**
1. Dashboard > New > PostgreSQL
2. Nome: `clinica-saude-db`
3. Database: `clinica_db`
4. User: `clinica_user`
5. Region: Oregon (mais barato)
6. Plan: **Free**
7. Criar

**B) Backend (Web Service):**
1. Dashboard > New > Web Service
2. Conectar repositório: `rafaelst97/prototype-melhoria`
3. Branch: `main`
4. Nome: `clinica-saude-backend`
5. Region: Oregon
6. Build Command: `pip install -r backend/requirements.txt`
7. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
8. Plan: **Free**
9. Environment Variables:
   ```
   DATABASE_URL = [copiar do PostgreSQL acima]
   SECRET_KEY = [gerar aleatório]
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ```
10. Criar

**C) Frontend (Static Site):**
1. Dashboard > New > Static Site
2. Repositório: `rafaelst97/prototype-melhoria`
3. Branch: `main`
4. Nome: `clinica-saude-frontend`
5. Build Command: (deixar vazio)
6. Publish Directory: `.`
7. Plan: **Free**
8. Criar

#### 3️⃣ Configurar URLs

Após deploy, você terá:
- **Frontend:** `https://clinica-saude-frontend.onrender.com`
- **Backend:** `https://clinica-saude-backend.onrender.com`
- **API Docs:** `https://clinica-saude-backend.onrender.com/docs`

---

## 🚂 Railway.app

### ✅ Vantagens
- **$5/mês grátis** de crédito
- **Suporte nativo a Docker Compose**
- **Deploy super rápido**
- **Logs em tempo real**

### 🚀 Deploy

1. **Instalar Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login:**
```bash
railway login
```

3. **Inicializar Projeto:**
```bash
railway init
```

4. **Deploy:**
```bash
railway up
```

5. **Abrir Dashboard:**
```bash
railway open
```

### 💰 Custos Railway
- **Plano Free:** $5/mês de crédito
- **Backend:** ~$2-3/mês
- **PostgreSQL:** ~$1-2/mês
- **Frontend:** Grátis (static)

---

## ✈️ Fly.io

### ✅ Vantagens
- **3 VMs grátis** (256 MB RAM cada)
- **PostgreSQL incluído** (3 GB free)
- **Edge computing** (baixa latência)
- **Suporte Docker nativo**

### 🚀 Deploy

1. **Instalar Fly CLI:**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

2. **Login:**
```bash
fly auth login
```

3. **Criar App Backend:**
```bash
cd backend
fly launch --name clinica-saude-backend
```

4. **Criar PostgreSQL:**
```bash
fly postgres create --name clinica-saude-db
fly postgres attach clinica-saude-db
```

5. **Deploy:**
```bash
fly deploy
```

---

## 🎨 Vercel + Supabase

### ✅ Vantagens
- **Vercel:** Melhor para frontend (serverless)
- **Supabase:** PostgreSQL + Auth + Storage grátis
- **Super rápido** (CDN global)
- **Git integration** perfeita

### 🚀 Deploy

#### Frontend (Vercel):
1. https://vercel.com/new
2. Import `rafaelst97/prototype-melhoria`
3. Build Settings:
   - Framework: Other
   - Output: `.` (raiz)
4. Deploy

#### Backend (Vercel Serverless):
Converter FastAPI para Vercel Functions:
```bash
# Criar vercel.json
{
  "builds": [
    {
      "src": "backend/app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/app/main.py"
    }
  ]
}
```

#### Database (Supabase):
1. https://supabase.com
2. New Project > `clinica-saude`
3. Copiar `DATABASE_URL`
4. Adicionar em Vercel Environment Variables

---

## 📊 Comparação de Plataformas

| Plataforma | Custo Mensal | PostgreSQL | Deploy | SSL | Uptime |
|------------|--------------|------------|--------|-----|--------|
| **Render** | **Grátis** | 500 MB | Git Push | ✅ | 99% |
| **Railway** | $5 crédito | Incluído | CLI/Git | ✅ | 99.9% |
| **Fly.io** | **Grátis** | 3 GB | CLI | ✅ | 99.9% |
| **Vercel + Supabase** | **Grátis** | 500 MB | Git Push | ✅ | 99.99% |
| **Heroku** | $7/mês | $9/mês | Git Push | ✅ | 99% |

---

## 🎯 Recomendação por Caso

### 🆓 Quer 100% Grátis?
→ **Render.com** (mais fácil) ou **Fly.io** (mais recursos)

### ⚡ Quer Máxima Performance?
→ **Vercel + Supabase** (CDN global)

### 🐳 Precisa Docker Completo?
→ **Railway** ou **Fly.io**

### 💼 Produção Real?
→ **Railway** ($5/mês) ou **Fly.io**

---

## 🔧 Configurações Necessárias

### Backend Environment Variables:
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=seu_secret_key_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=https://seu-frontend.com
```

### Frontend (js/config.js):
```javascript
const API_URL = 'https://clinica-saude-backend.onrender.com';
```

---

## 🚀 Deploy Automático (CI/CD)

### GitHub Actions para Render:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Trigger Render Deploy
        run: |
          curl -X POST \
            https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }}?key=${{ secrets.RENDER_API_KEY }}
```

---

## 📱 Após o Deploy

### 1. Popular Banco de Dados:
```bash
# Via Render Dashboard > Shell
cd backend
python populate_test_data.py
```

### 2. Testar API:
```bash
curl https://clinica-saude-backend.onrender.com/health
```

### 3. Testar Frontend:
```
https://clinica-saude-frontend.onrender.com
```

### 4. Verificar Logs:
```bash
# Render Dashboard > Logs
# Ou via CLI:
render logs -f
```

---

## 🐛 Troubleshooting

### Backend não inicia?
- Verificar `DATABASE_URL` nas env vars
- Checar logs: `render logs`
- Verificar build command

### Erro de CORS?
- Adicionar frontend URL em `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://clinica-saude-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Database connection failed?
- Verificar se PostgreSQL está running
- Testar conexão manual
- Verificar credenciais

---

## 💡 Dicas Pro

1. **Usar CDN:** Render tem CDN automático
2. **Habilitar Caching:** Configurar headers HTTP
3. **Monitoramento:** Integrar com UptimeRobot (grátis)
4. **Backups:** Render faz backup automático do PostgreSQL
5. **Custom Domain:** Adicionar domínio próprio (grátis)

---

## 👥 Equipe

- **Caio César Sabino Soares**
- **Júlia Cansian Rocha**
- **Rafael dos Santos**

**UNIVALI - Melhoria de Processo de Software - 2025**

---

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE)

---

**Última atualização:** 09/11/2025  
**Versão:** v2.0.0
