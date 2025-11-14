# Script para configurar PostgreSQL para o projeto Clínica Saúde

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🐘 CONFIGURAÇÃO POSTGRESQL - CLÍNICA SAÚDE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Verificar se PostgreSQL está instalado
Write-Host "`n🔍 Verificando instalação do PostgreSQL..." -ForegroundColor Yellow
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue

if (-not $psqlPath) {
    Write-Host "❌ PostgreSQL não encontrado!" -ForegroundColor Red
    Write-Host "`n💡 Instale o PostgreSQL:" -ForegroundColor Yellow
    Write-Host "   1. Download: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "   2. Ou use Chocolatey: choco install postgresql" -ForegroundColor White
    exit 1
}

Write-Host "✅ PostgreSQL encontrado: $($psqlPath.Source)" -ForegroundColor Green

# Credenciais
$DB_NAME = "clinica_saude"
$DB_USER = "clinica_user"
$DB_PASS = "clinica_pass"

Write-Host "`n📝 Configurações:" -ForegroundColor Yellow
Write-Host "   Banco: $DB_NAME" -ForegroundColor White
Write-Host "   Usuário: $DB_USER" -ForegroundColor White
Write-Host "   Senha: $DB_PASS" -ForegroundColor White

# Solicitar senha do postgres
Write-Host "`n🔐 Digite a senha do usuário 'postgres':" -ForegroundColor Yellow
$env:PGPASSWORD = Read-Host -AsSecureString | ConvertFrom-SecureString -AsPlainText

# Criar usuário
Write-Host "`n👤 Criando usuário $DB_USER..." -ForegroundColor Yellow
$createUserSQL = "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
$checkUserSQL = "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER';"

$userExists = psql -U postgres -d postgres -t -c $checkUserSQL 2>$null

if ($userExists -match "1") {
    Write-Host "ℹ️  Usuário já existe" -ForegroundColor Cyan
} else {
    psql -U postgres -d postgres -c $createUserSQL
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Usuário criado!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao criar usuário" -ForegroundColor Red
        exit 1
    }
}

# Criar banco
Write-Host "`n🗄️  Criando banco $DB_NAME..." -ForegroundColor Yellow
$createDBSQL = "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
$checkDBSQL = "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';"

$dbExists = psql -U postgres -d postgres -t -c $checkDBSQL 2>$null

if ($dbExists -match "1") {
    Write-Host "ℹ️  Banco já existe" -ForegroundColor Cyan
} else {
    psql -U postgres -d postgres -c $createDBSQL
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Banco criado!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao criar banco" -ForegroundColor Red
        exit 1
    }
}

# Dar permissões
Write-Host "`n🔑 Concedendo permissões..." -ForegroundColor Yellow
$grantSQL = "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
psql -U postgres -d postgres -c $grantSQL
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Permissões concedidas!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Aviso: erro ao conceder permissões" -ForegroundColor Yellow
}

# Limpar variável de senha
Remove-Item Env:\PGPASSWORD

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "✅ POSTGRESQL CONFIGURADO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n💡 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. python migrate_postgres.py  (criar tabelas e popular)" -ForegroundColor White
Write-Host "   2. uvicorn app.main:app --reload  (iniciar servidor)" -ForegroundColor White
Write-Host ""
