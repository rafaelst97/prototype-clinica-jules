# 📜 Scripts do Projeto

Esta pasta contém scripts utilitários para desenvolvimento e deploy.

## 📁 Arquivos

### 🪟 Windows

- **`abrir-site.bat`** - Abre o site no navegador (http://localhost:8081)
- **`publicar-github.bat`** - Script para publicar no GitHub
- **`setup-github.ps1`** - Configuração inicial do repositório GitHub
- **`start.ps1`** - Inicia o projeto completo (Docker Compose)

### 🐧 Linux/Mac

- **`start.sh`** - Inicia o projeto completo (Docker Compose)

## 🚀 Uso

### Iniciar o Projeto

**Windows:**
```powershell
.\scripts\start.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

### Abrir no Navegador

**Windows:**
```cmd
.\scripts\abrir-site.bat
```

### Publicar no GitHub

**Windows:**
```cmd
.\scripts\publicar-github.bat
```

## ⚙️ O que cada script faz

### start.ps1 / start.sh
1. Verifica se Docker está rodando
2. Executa `docker-compose up -d`
3. Aguarda serviços ficarem prontos
4. Exibe URLs de acesso

### abrir-site.bat
1. Abre http://localhost:8081/index.html no navegador padrão

### publicar-github.bat
1. Faz git add de todos os arquivos
2. Solicita mensagem de commit
3. Faz commit e push para origin

### setup-github.ps1
1. Inicializa repositório git
2. Configura remote origin
3. Faz commit inicial
4. Faz push para GitHub

## 🔧 Requisitos

- Docker + Docker Compose
- Git
- PowerShell (Windows) ou Bash (Linux/Mac)

## 📝 Notas

- Scripts devem ser executados da raiz do projeto
- Docker deve estar rodando antes de executar start.ps1/start.sh
- Para desenvolvimento, use `docker-compose up` (sem -d) para ver logs
