# 🔐 TOKEN SECRETO - Configuração

## 📍 Localização do Token

O token está definido em:
```
backend/app/routers/populate.py
Linha ~23: SECRET_TOKEN = "meu-token-super-secreto-2025"
```

---

## 🔒 Como Gerar um Token Mais Seguro

### Opção 1: Python (Recomendado)
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Opção 2: PowerShell
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### Opção 3: Online
Use um gerador de senhas seguras como:
- https://www.random.org/strings/
- https://passwordsgenerator.net/

---

## ⚙️ Como Alterar o Token

1. Gere um novo token usando uma das opções acima
2. Abra o arquivo `backend/app/routers/populate.py`
3. Localize a linha com `SECRET_TOKEN = "..."`
4. Substitua pelo seu novo token
5. Faça commit e push:

```powershell
git add backend/app/routers/populate.py
git commit -m "security: Update secret token"
git push origin main
```

6. Aguarde o Render fazer deploy automático (~5 min)

---

## 🌐 Como Usar

Após configurar o token, acesse no navegador:

```
https://clinica-saude-backend.onrender.com/admin/popula-banco/SEU-TOKEN-AQUI
```

### Exemplo com token padrão (TROCAR!):
```
https://clinica-saude-backend.onrender.com/admin/popula-banco/meu-token-super-secreto-2025
```

### Exemplo com token seguro:
```
https://clinica-saude-backend.onrender.com/admin/popula-banco/xK9mP2vL8qN5tR4wE7yU3iO6aS1dF0gH
```

---

## ✨ Recursos da URL Secreta

✅ **Acesso direto pelo navegador** - Sem precisar de script Python  
✅ **Interface visual bonita** - HTML com design responsivo  
✅ **Proteção por token** - Apenas quem tem o token pode acessar  
✅ **Feedback visual** - Mostra estatísticas e credenciais criadas  
✅ **Prevenção de duplicação** - Avisa se banco já está populado  

---

## 🔐 Segurança

### ⚠️ IMPORTANTE:
1. **NUNCA** compartilhe o token publicamente
2. **SEMPRE** use um token único e complexo
3. **TROQUE** o token se suspeitar de vazamento
4. **NÃO** comite o token no Git (já está no código, mas poderia usar variável de ambiente)

### Melhor Prática:
Idealmente, o token deveria vir de uma variável de ambiente:

```python
import os
SECRET_TOKEN = os.getenv("POPULATE_SECRET_TOKEN", "fallback-token")
```

E definir no Render:
```
Dashboard > clinica-saude-backend > Environment > Add Environment Variable
Key: POPULATE_SECRET_TOKEN
Value: seu-token-super-secreto
```

---

## 🎯 Exemplo de Uso Completo

1. **Gere o token:**
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   # Resultado: xK9mP2vL8qN5tR4wE7yU3iO6aS1dF0gH
   ```

2. **Atualize o código:**
   - Edite `populate.py` → linha do `SECRET_TOKEN`
   - Faça commit e push

3. **Acesse no navegador:**
   ```
   https://clinica-saude-backend.onrender.com/admin/popula-banco/xK9mP2vL8qN5tR4wE7yU3iO6aS1dF0gH
   ```

4. **Veja a mágica acontecer!** ✨
   - Página bonita com estatísticas
   - Credenciais de teste exibidas
   - Banco populado automaticamente

---

## 🚫 O Que Acontece com Token Errado

Se tentar acessar com token inválido:
```
https://clinica-saude-backend.onrender.com/admin/popula-banco/token-errado
```

Resultado: Página de "🔒 Acesso Negado" com status HTTP 403

---

**Data:** 09/11/2025  
**Versão:** 2.0.0  
**Autor:** Sistema Clínica Saúde+
