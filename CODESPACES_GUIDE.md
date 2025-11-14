# 🚀 Guia de Uso do GitHub Codespaces

## 📋 Informações do Codespace

**Nome:** `humble-xylophone-9qpgjvwqq9x3pppv`  
**Estado:** Provisioning (aguardando inicialização)  
**Branch:** `codespaces`  
**Repositório:** `rafaelst97/prototype-melhoria`  
**Configuração:** 2 cores, 8 GB RAM, 32 GB storage  
**Timeout de Inatividade:** 30 minutos  
**Período de Retenção:** 30 dias

---

## 🌐 Acessando o Codespace

### Opção 1: Via Navegador Web
```bash
gh codespace code --web --codespace humble-xylophone-9qpgjvwqq9x3pppv
```

### Opção 2: Via VS Code Desktop
```bash
gh codespace code --codespace humble-xylophone-9qpgjvwqq9x3pppv
```

### Opção 3: Via Portal GitHub
1. Acesse: https://github.com/codespaces
2. Clique no codespace `humble-xylophone-9qpgjvwqq9x3pppv`
3. Escolha "Open in VS Code" ou "Open in Browser"

---

## ⚙️ Configuração Automática

O Codespace já está configurado com:

### 🐳 Containers Docker Compose
- **Backend (FastAPI):** Porta 8000
- **Frontend (Nginx):** Porta 80
- **PostgreSQL:** Porta 5432
- **pgAdmin:** Porta 5050

### 🔧 Ferramentas Instaladas
- Docker-in-Docker
- GitHub CLI
- Python 3.11
- Node.js
- Git

### 📦 Extensões VS Code
- Python
- Docker
- GitLens
- Thunder Client
- PostgreSQL
- Live Server
- Pylance
- Database Client

---

## 🚀 Iniciando o Sistema

### 1. Aguarde o Setup Automático
O script `.devcontainer/setup.sh` instalará automaticamente:
- Dependências Python do backend
- Dependências de testes

### 2. Inicie os Containers Docker
```bash
docker-compose up -d
```

### 3. Verifique os Containers
```bash
docker-compose ps
```

### 4. Acesse o Sistema
- **Frontend:** Clique na porta 80 (será aberta automaticamente)
- **Backend API:** Porta 8000
- **Docs API:** http://localhost:8000/docs
- **pgAdmin:** http://localhost:5050

---

## 👥 Usuários de Teste

| Tipo | Email | Senha |
|------|-------|-------|
| **Admin** | admin@clinica.com | admin123 |
| **Médico** | joao1@clinica.com | medico123 |
| **Paciente** | maria@email.com | paciente123 |

---

## 🛠️ Comandos Úteis

### Gerenciar Codespace

```bash
# Listar todos os Codespaces
gh codespace list

# Ver detalhes do Codespace
gh codespace view --codespace humble-xylophone-9qpgjvwqq9x3pppv

# Parar o Codespace (economizar créditos)
gh codespace stop --codespace humble-xylophone-9qpgjvwqq9x3pppv

# Excluir o Codespace
gh codespace delete --codespace humble-xylophone-9qpgjvwqq9x3pppv

# Acessar via SSH
gh codespace ssh --codespace humble-xylophone-9qpgjvwqq9x3pppv
```

### Gerenciar Docker

```bash
# Iniciar containers
docker-compose up -d

# Parar containers
docker-compose down

# Ver logs
docker-compose logs -f backend

# Reconstruir containers
docker-compose up -d --build
```

### Executar Testes

```bash
# Testes unitários
cd backend
pytest

# Testes com cobertura
pytest --cov=app --cov-report=html

# Testes E2E
python test_sistema_completo.py
```

---

## 🔌 Portas Disponíveis

| Porta | Serviço | Visibilidade |
|-------|---------|--------------|
| **80** | Frontend (Nginx) | Pública |
| **8000** | Backend API (FastAPI) | Pública |
| **5432** | PostgreSQL | Privada |
| **5050** | pgAdmin | Privada |

---

## 📊 Gerenciando Recursos

### ⏱️ Timeout Automático
- O Codespace para automaticamente após **30 minutos** de inatividade
- Isso economiza seus créditos gratuitos

### 💾 Armazenamento
- **32 GB** de armazenamento disponível
- Arquivos persistem por **30 dias** após exclusão

### 🔄 Cotas GitHub Codespaces

**Plano Free:**
- 120 horas/mês de uso
- 15 GB de armazenamento

**Plano Pro:**
- 180 horas/mês de uso
- 20 GB de armazenamento

---

## 🐛 Troubleshooting

### Codespace não inicia?
```bash
# Verificar status
gh codespace view --codespace humble-xylophone-9qpgjvwqq9x3pppv

# Recriar Codespace
gh codespace delete --codespace humble-xylophone-9qpgjvwqq9x3pppv
gh codespace create -R rafaelst97/prototype-melhoria -b codespaces
```

### Docker não funciona?
```bash
# Reiniciar Docker
sudo service docker restart

# Verificar status
docker ps
```

### Banco de dados não conecta?
```bash
# Verificar PostgreSQL
docker-compose logs postgres

# Recriar banco
docker-compose down -v
docker-compose up -d
```

---

## 📚 Recursos Adicionais

- **Repositório:** https://github.com/rafaelst97/prototype-melhoria
- **Issues:** https://github.com/rafaelst97/prototype-melhoria/issues
- **Releases:** https://github.com/rafaelst97/prototype-melhoria/releases
- **GitHub Pages:** https://rafaelst97.github.io/prototype-melhoria/
- **Documentação:** [README.md](README.md)

---

## 👥 Equipe

- **Caio César Sabino Soares**
- **Júlia Cansian Rocha**
- **Rafael dos Santos**

**Universidade do Vale do Itajaí (UNIVALI)**  
**Melhoria de Processo de Software - 2025**

---

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Última atualização:** 09/11/2025  
**Versão do Sistema:** v2.0.0  
**Branch:** codespaces
