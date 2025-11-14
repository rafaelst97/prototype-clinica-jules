# Script de Orquestração de Testes Completos
# Prepara ambiente, popula banco de dados e executa testes automatizados

param(
    [switch]$SkipSeed = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ORQUESTRADOR DE TESTES - CLÍNICA SAÚDE+" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$startTime = Get-Date

# Função para verificar se o Docker está rodando
function Test-DockerRunning {
    try {
        $null = docker ps 2>&1
        return $?
    } catch {
        return $false
    }
}

# Função para verificar se container está rodando
function Test-ContainerRunning {
    param([string]$containerName)
    
    $container = docker ps --filter "name=$containerName" --format "{{.Names}}" 2>$null
    return ($null -ne $container -and $container -ne "")
}

# Função para esperar serviço estar pronto com timeout
function Wait-ServiceReady {
    param(
        [string]$url,
        [int]$maxAttempts = 30,
        [int]$delaySeconds = 2
    )
    
    Write-Host "Aguardando serviço estar pronto: $url" -ForegroundColor Yellow
    
    for ($i = 1; $i -le $maxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Serviço está pronto!" -ForegroundColor Green
                return $true
            }
        } catch {
            # Ignorar erro e tentar novamente
        }
        
        Write-Host "  Tentativa $i de $maxAttempts..." -ForegroundColor Gray
        Start-Sleep -Seconds $delaySeconds
    }
    
    Write-Host "❌ Timeout: Serviço não ficou pronto" -ForegroundColor Red
    return $false
}

# 1. Verificar Docker
Write-Host "1️⃣  Verificando Docker..." -ForegroundColor Cyan
if (-not (Test-DockerRunning)) {
    Write-Host "❌ Docker não está rodando. Inicie o Docker Desktop e tente novamente." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker está rodando" -ForegroundColor Green
Write-Host ""

# 2. Verificar se os containers estão rodando
Write-Host "2️⃣  Verificando containers..." -ForegroundColor Cyan

$containers = @("clinica_backend", "clinica_frontend", "clinica_db")
$allRunning = $true

foreach ($container in $containers) {
    if (Test-ContainerRunning $container) {
        Write-Host "✅ Container $container está rodando" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Container $container não está rodando" -ForegroundColor Yellow
        $allRunning = $false
    }
}

# 3. Iniciar containers se necessário
if (-not $allRunning) {
    Write-Host "`n3️⃣  Iniciando containers com Docker Compose..." -ForegroundColor Cyan
    
    $projectRoot = Split-Path -Parent $PSScriptRoot
    Set-Location $projectRoot
    
    Write-Host "Executando: docker-compose up -d" -ForegroundColor Gray
    docker-compose up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao iniciar containers" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Containers iniciados" -ForegroundColor Green
    Write-Host ""
    
    # Aguardar serviços ficarem prontos
    Write-Host "4️⃣  Aguardando serviços ficarem prontos..." -ForegroundColor Cyan
    
    if (-not (Wait-ServiceReady "http://localhost:8000/docs" 60 3)) {
        Write-Host "❌ Backend não ficou pronto a tempo" -ForegroundColor Red
        exit 1
    }
    
    if (-not (Wait-ServiceReady "http://localhost" 30 2)) {
        Write-Host "❌ Frontend não ficou pronto a tempo" -ForegroundColor Red
        exit 1
    }
    
} else {
    Write-Host "✅ Todos os containers já estão rodando" -ForegroundColor Green
    Write-Host ""
}

# 5. Popular banco de dados (se não for para pular)
if (-not $SkipSeed) {
    Write-Host "5️⃣  Populando banco de dados com dados de teste..." -ForegroundColor Cyan
    
    Write-Host "Executando seed_data.py no container..." -ForegroundColor Gray
    
    # Executar seed com timeout
    $seedJob = Start-Job -ScriptBlock {
        docker exec clinica_backend python seed_data.py 2>&1
    }
    
    $seedTimeout = 30
    $seedComplete = Wait-Job -Job $seedJob -Timeout $seedTimeout
    
    if ($seedComplete) {
        $seedOutput = Receive-Job -Job $seedJob
        Write-Host $seedOutput
        
        if ($seedJob.State -eq "Completed") {
            Write-Host "✅ Banco de dados populado com sucesso" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Seed pode ter falhado, mas continuando..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  Seed timeout, mas continuando..." -ForegroundColor Yellow
        Stop-Job -Job $seedJob
    }
    
    Remove-Job -Job $seedJob -Force
    Write-Host ""
} else {
    Write-Host "5️⃣  Pulando população do banco (--SkipSeed)" -ForegroundColor Yellow
    Write-Host ""
}

# 6. Executar testes automatizados
Write-Host "6️⃣  Executando testes automatizados..." -ForegroundColor Cyan
Write-Host ""

$testsPath = Join-Path $PSScriptRoot "..\tests\selenium\teste_completo_automatizado.py"

if (Test-Path $testsPath) {
    Write-Host "Executando: python $testsPath" -ForegroundColor Gray
    Write-Host ""
    
    # Executar testes sem timeout (deixar rodar até completar)
    python $testsPath
    $testExitCode = $LASTEXITCODE
    
    Write-Host ""
    
    if ($testExitCode -eq 0) {
        Write-Host "✅ TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  ALGUNS TESTES FALHARAM" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Arquivo de testes não encontrado: $testsPath" -ForegroundColor Red
    $testExitCode = 1
}

Write-Host ""

# 7. Relatório final
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ORQUESTRAÇÃO CONCLUÍDA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏱️  Tempo total: $([math]::Round($duration, 2)) segundos" -ForegroundColor White
Write-Host ""

if ($testExitCode -eq 0) {
    Write-Host "🎉 SISTEMA 100% FUNCIONAL E TESTADO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Acesse o sistema em: http://localhost" -ForegroundColor White
    Write-Host "📚 Documentação da API: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "⚠️  Verifique os erros acima e corrija os problemas." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
