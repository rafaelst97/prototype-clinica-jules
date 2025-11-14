# 🔌 Como Conectar ao Banco de Dados no pgAdmin

## 📍 Passo 1: Acesse o pgAdmin

Abra seu navegador em: **http://localhost:5050**

**Credenciais de Login do pgAdmin:**
- **Email:** `admin@clinica.com`
- **Senha:** `admin123`

---

## 📍 Passo 2: Adicionar Novo Servidor

Após fazer login, você verá o painel do pgAdmin vazio (sem servidores).

### Opção A: Menu Superior
1. Clique em **Object** (menu superior)
2. Selecione **Register** → **Server...**

### Opção B: Botão de Atalho
1. Procure o ícone **"Add New Server"** (servidor com símbolo +)
2. Clique nele

### Opção C: Clique com Botão Direito
1. No painel esquerdo, clique com **botão direito** em **"Servers"**
2. Selecione **Register** → **Server...**

---

## 📍 Passo 3: Configurar Conexão

Uma janela **"Register - Server"** vai abrir com várias abas.

### 🏷️ **ABA "General"**

| Campo | Valor |
|-------|-------|
| **Name** | `Clinica Saude` |

### 🔌 **ABA "Connection"**

| Campo | Valor | ⚠️ Importante |
|-------|-------|---------------|
| **Host name/address** | `postgres` | ⚠️ NÃO use "localhost"! |
| **Port** | `5432` | |
| **Maintenance database** | `clinica_saude` | |
| **Username** | `clinica_user` | |
| **Password** | `clinica_pass` | |
| **Save password?** | ✅ Marcar (recomendado) | |

### ⚠️ **ATENÇÃO ESPECIAL**

**Host name/address** deve ser **`postgres`** (nome do container), NÃO `localhost`!

Isso porque:
- O pgAdmin está rodando dentro de um container Docker
- Ele precisa acessar o container do PostgreSQL pela rede interna do Docker
- `postgres` é o nome do serviço definido no `docker-compose.yml`

---

## 📍 Passo 4: Salvar e Conectar

1. Após preencher todos os campos, clique em **"Save"**
2. O pgAdmin vai tentar conectar ao banco
3. Se tudo estiver correto, você verá:

```
Servers/
└── Clinica Saude
    └── Databases (1)
        └── clinica_saude
            └── Schemas
                └── public
                    └── Tables (9) ← Aqui estão suas tabelas!
```

---

## 📊 Passo 5: Ver as Tabelas

1. No painel esquerdo, expanda:
   - **Servers**
   - **Clinica Saude**
   - **Databases**
   - **clinica_saude**
   - **Schemas**
   - **public**
   - **Tables**

2. Você verá as **9 tabelas** criadas:
   - `admin`
   - `bloqueios_horario`
   - `consultas`
   - `convenios`
   - `especialidades`
   - `horarios_disponiveis`
   - `medicos`
   - `pacientes`
   - `usuarios`

3. Para ver os dados de uma tabela:
   - **Botão direito** na tabela
   - **View/Edit Data** → **All Rows**

---

## ⚠️ Resolução de Problemas

### ❌ "could not connect to server"

**Causa:** Container do PostgreSQL não está rodando

**Solução:**
```powershell
docker-compose ps postgres
```

Se não aparecer como "Up" e "healthy", reinicie:
```powershell
docker-compose restart postgres
```

---

### ❌ "authentication failed for user"

**Causa:** Credenciais incorretas

**Solução:** Verifique se digitou exatamente:
- Username: `clinica_user` (sem espaços)
- Password: `clinica_pass` (sem espaços)

---

### ❌ "Connection timeout" ou "Name resolution error"

**Causa:** Usou `localhost` em vez de `postgres`

**Solução:** Use `postgres` no campo "Host name/address"

---

## 📋 Referência Rápida de Credenciais

```
╔════════════════════════════════════════════╗
║           PGADMIN LOGIN                    ║
╠════════════════════════════════════════════╣
║ URL:      http://localhost:5050            ║
║ Email:    admin@clinica.com                ║
║ Password: admin123                         ║
╚════════════════════════════════════════════╝

╔════════════════════════════════════════════╗
║        POSTGRESQL CONNECTION               ║
╠════════════════════════════════════════════╣
║ Host:     postgres                         ║
║ Port:     5432                             ║
║ Database: clinica_saude                    ║
║ Username: clinica_user                     ║
║ Password: clinica_pass                     ║
╚════════════════════════════════════════════╝
```

---

## 🎯 Próximos Passos

Depois de conectar ao banco, você pode:

1. **Popular o banco com dados iniciais:**
   ```powershell
   docker exec -it clinica_backend python seed_data.py
   ```

2. **Testar a API:**
   - Acesse: http://localhost:8000/docs
   - Teste os endpoints de login, cadastro, etc.

3. **Usar o sistema:**
   - Frontend: http://localhost
   - Login como paciente/médico/admin

---

**✅ Pronto! Agora você pode visualizar e gerenciar todas as tabelas do banco de dados!**
