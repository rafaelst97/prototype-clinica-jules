@echo off
echo Configurando repositorio Git...
echo.

REM Verificar se ja existe um remote origin
git remote remove origin 2>nul

REM Adicionar o novo remote
echo Adicionando remote origin...
git remote add origin https://github.com/rafaelst97/prototype-clinica-jules.git

REM Verificar branch atual
echo.
echo Branch atual:
git branch --show-current

REM Renomear para main se necessario
git branch -M main

REM Adicionar todos os arquivos
echo.
echo Adicionando arquivos...
git add .

REM Fazer commit se houver mudancas
git diff-index --quiet HEAD || git commit -m "Initial commit - Jules clinic prototype"

REM Fazer push
echo.
echo Fazendo push para GitHub...
git push -u origin main

echo.
echo Concluido!
pause
