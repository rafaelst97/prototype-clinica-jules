# Script para criar repositório no GitHub
# Execute este script após criar manualmente o repositório no GitHub

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  GitHub Pages Setup - Clínica Saúde+" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Instruções
Write-Host "PASSO 1: Criar repositório no GitHub" -ForegroundColor Yellow
Write-Host "1. Acesse: https://github.com/new" -ForegroundColor White
Write-Host "2. Nome do repositório: prototype-melhoria" -ForegroundColor White
Write-Host "3. Deixe como público (Public)" -ForegroundColor White
Write-Host "4. NÃO adicione README, .gitignore ou licença" -ForegroundColor White
Write-Host "5. Clique em 'Create repository'" -ForegroundColor White
Write-Host ""

Write-Host "Pressione ENTER depois de criar o repositório no GitHub..." -ForegroundColor Green
Read-Host

Write-Host ""
Write-Host "PASSO 2: Enviando código para o GitHub..." -ForegroundColor Yellow

# Verificar se já tem remote
$remotes = git remote
if ($remotes -contains "origin") {
    Write-Host "Remote 'origin' já existe, removendo..." -ForegroundColor Gray
    git remote remove origin
}

# Pedir URL do repositório
Write-Host ""
Write-Host "Cole a URL do seu repositório GitHub (exemplo: https://github.com/seu-usuario/prototype-melhoria.git):" -ForegroundColor Cyan
$repoUrl = Read-Host

# Adicionar remote e fazer push
Write-Host ""
Write-Host "Adicionando remote e enviando código..." -ForegroundColor Yellow
git remote add origin $repoUrl
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "PASSO 3: Configurando GitHub Pages..." -ForegroundColor Yellow
Write-Host "1. Vá para: Settings > Pages" -ForegroundColor White
Write-Host "2. Em 'Source', selecione: 'Deploy from a branch'" -ForegroundColor White
Write-Host "3. Em 'Branch', selecione: 'main' e pasta '/ (root)'" -ForegroundColor White
Write-Host "4. Clique em 'Save'" -ForegroundColor White
Write-Host ""
Write-Host "Seu site estará disponível em:" -ForegroundColor Green
Write-Host "https://seu-usuario.github.io/prototype-melhoria/" -ForegroundColor Cyan
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Setup concluído! Aguarde alguns minutos para o deploy." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
