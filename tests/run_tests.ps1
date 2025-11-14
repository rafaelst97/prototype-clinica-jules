# Script PowerShell para Executar Testes Automatizados
# tests/run_tests.ps1

Write-Host "🧪 Testes Automatizados - Clínica Saúde+" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Python está instalado
Write-Host "📦 Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python não encontrado. Por favor, instale Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green
Write-Host ""

# Verificar se dependências estão instaladas
Write-Host "📦 Verificando dependências..." -ForegroundColor Yellow
$pipList = pip list 2>&1
if ($pipList -notmatch "selenium") {
    Write-Host "⚠️  Selenium não encontrado. Instalando dependências..." -ForegroundColor Yellow
    pip install -r tests/requirements-tests.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao instalar dependências" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Dependências OK" -ForegroundColor Green
Write-Host ""

# Verificar se Docker está rodando
Write-Host "🐳 Verificando Docker..." -ForegroundColor Yellow
$dockerPs = docker-compose ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Docker não está rodando. Iniciando..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep -Seconds 10
}
Write-Host "✅ Docker OK" -ForegroundColor Green
Write-Host ""

# Verificar se frontend está acessível
Write-Host "🌐 Verificando Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:80" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Frontend acessível (porta 80)" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend não está respondendo em http://localhost:80" -ForegroundColor Red
    Write-Host "   Execute: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Verificar se backend está acessível
Write-Host "🔧 Verificando Backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Backend acessível (porta 8000)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend não está respondendo em http://localhost:8000" -ForegroundColor Red
    Write-Host "   Execute: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Menu de opções
Write-Host "Escolha uma opção:" -ForegroundColor Cyan
Write-Host "1. Executar TODOS os testes" -ForegroundColor White
Write-Host "2. Executar testes de CADASTRO" -ForegroundColor White
Write-Host "3. Executar testes de LOGIN" -ForegroundColor White
Write-Host "4. Executar testes de AGENDAMENTO" -ForegroundColor White
Write-Host "5. Executar testes de CANCELAMENTO" -ForegroundColor White
Write-Host "6. Executar testes de REAGENDAMENTO" -ForegroundColor White
Write-Host "7. Executar testes de VISUALIZAÇÃO" -ForegroundColor White
Write-Host "8. Executar teste específico (por número)" -ForegroundColor White
Write-Host "9. Gerar relatório HTML" -ForegroundColor White
Write-Host "0. Sair" -ForegroundColor White
Write-Host ""

$opcao = Read-Host "Digite a opção"

switch ($opcao) {
    "1" {
        Write-Host "`n🚀 Executando TODOS os testes..." -ForegroundColor Cyan
        pytest tests/test_interface_completo.py -v
    }
    "2" {
        Write-Host "`n🚀 Executando testes de CADASTRO..." -ForegroundColor Cyan
        pytest tests/test_interface_completo.py::TestCadastroPaciente -v
    }
    "3" {
        Write-Host "`n🚀 Executando testes de LOGIN..." -ForegroundColor Cyan
        pytest tests/test_interface_completo.py::TestLoginPaciente -v
    }
    "4" {
        Write-Host "`n🚀 Executando testes de AGENDAMENTO..." -ForegroundColor Cyan
        pytest tests/test_interface_completo.py::TestAgendamentoConsulta -v
    }
    "5" {
        Write-Host "`n🚀 Executando testes de CANCELAMENTO..." -ForegroundColor Cyan
        pytest tests/test_interface_completo.py::TestCancelamentoConsulta -v
    }
    "6" {
        Write-Host "`n🚀 Executando testes de REAGENDAMENTO..." -ForegroundColor Cyan
        pytest tests/test_interface_completo.py::TestReagendamentoConsulta -v
    }
    "7" {
        Write-Host "`n🚀 Executando testes de VISUALIZAÇÃO..." -ForegroundColor Cyan
        pytest tests/test_interface_completo.py::TestVisualizacaoConsultas -v
    }
    "8" {
        $numeroTeste = Read-Host "Digite o número do teste (ex: 010)"
        Write-Host "`n🚀 Executando teste $numeroTeste..." -ForegroundColor Cyan
        pytest tests/test_interface_completo.py -v -k "test_${numeroTeste}"
    }
    "9" {
        Write-Host "`n🚀 Gerando relatório HTML..." -ForegroundColor Cyan
        pytest tests/test_interface_completo.py -v --html=report.html --self-contained-html
        Write-Host "`n✅ Relatório gerado: report.html" -ForegroundColor Green
        Write-Host "   Abra o arquivo no navegador para visualizar" -ForegroundColor Yellow
    }
    "0" {
        Write-Host "`n👋 Até logo!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "`n❌ Opção inválida" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Execução concluída!" -ForegroundColor Green
Write-Host ""
