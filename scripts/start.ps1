# Script de Inicializacao - Clinica Saude+

Write-Host "`n" -NoNewline
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "         Sistema Clinica Saude+ - Full Stack                     " -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "`n"

Write-Host "Parando containers existentes..." -ForegroundColor Yellow
docker-compose down

Write-Host "`nConstruindo imagens Docker..." -ForegroundColor Yellow
docker-compose build

Write-Host "`nIniciando containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`nAguardando servicos iniciarem (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "`nStatus dos containers:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`nServicos disponiveis:" -ForegroundColor Green
Write-Host "   Frontend:    http://localhost" -ForegroundColor White
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "   PostgreSQL:  localhost:5432" -ForegroundColor White

Write-Host "`nCredenciais de Teste:" -ForegroundColor Magenta
Write-Host "   Admin: admin@clinica.com / admin123" -ForegroundColor Gray

Write-Host "`nComandos uteis:" -ForegroundColor Yellow
Write-Host "   Ver logs:       docker-compose logs -f" -ForegroundColor Gray
Write-Host "   Parar:          docker-compose down" -ForegroundColor Gray
Write-Host "   Reiniciar:      docker-compose restart" -ForegroundColor Gray
Write-Host "   Resetar dados:  docker-compose down -v; docker-compose up -d" -ForegroundColor Gray

Write-Host "`nSistema pronto para uso!" -ForegroundColor Green
Write-Host ""
