# Script para executar todos os testes e gerar relatório completo

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "EXECUÇÃO COMPLETA DE TESTES - Sistema Clínica Saúde+" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "backend")) {
    Write-Host "❌ Execute este script do diretório raiz do projeto" -ForegroundColor Red
    exit 1
}

# Navegar para o backend
cd backend

Write-Host "📦 Instalando dependências de teste..." -ForegroundColor Yellow
pip install -r requirements-test.txt

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "FASE 1: Testes de Validadores e Regras de Negócio" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

pytest tests/test_validators_completo.py -v --tb=short

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "FASE 2: Testes de Segurança" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

pytest tests/test_seguranca_completo.py -v --tb=short

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "FASE 3: Testes de Endpoints (Existentes)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

pytest tests/test_endpoints_pacientes.py -v --tb=short
pytest tests/test_endpoints_medicos.py -v --tb=short
pytest tests/test_admin_relatorios.py -v --tb=short

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "FASE 4: Validação de Banco de Dados" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker está rodando
docker ps | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Docker não está rodando. Pulando validação de BD." -ForegroundColor Yellow
} else {
    python tests/validate_database.py
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "FASE 5: Testes E2E com Selenium" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se aplicação está rodando
$response = $null
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -Method Head -TimeoutSec 2 -ErrorAction SilentlyContinue
} catch {}

if ($response -and $response.StatusCode -eq 200) {
    Write-Host "✅ Aplicação está rodando. Executando testes E2E..." -ForegroundColor Green
    pytest tests/test_e2e_selenium.py -v --tb=short
} else {
    Write-Host "⚠️  Aplicação não está rodando em http://localhost" -ForegroundColor Yellow
    Write-Host "   Inicie a aplicação com 'docker-compose up' para executar testes E2E" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "FASE 6: Cobertura de Código" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Gerando relatório de cobertura..." -ForegroundColor Yellow
pytest --cov=app --cov-report=html --cov-report=term-missing

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "RELATÓRIO FINAL GERADO" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 Relatórios disponíveis:" -ForegroundColor Green
Write-Host "   - Cobertura de código: backend/htmlcov/index.html" -ForegroundColor White
Write-Host "   - Screenshots de testes E2E: backend/tests/screenshots/" -ForegroundColor White

Write-Host ""
Write-Host "✅ Execução de testes concluída!" -ForegroundColor Green
Write-Host ""

# Voltar ao diretório raiz
cd ..
