@echo off
title GitHub Pages - Clinica Saude+
color 0A

echo.
echo ========================================
echo   PUBLICAR NO GITHUB PAGES
echo   Prototipo Clinica Saude+
echo ========================================
echo.
echo STATUS: Pronto para enviar ao GitHub
echo.
echo AGUARDE: Criando repositorio no GitHub...
echo.

start https://github.com/new

echo.
echo Apos criar o repositorio no GitHub:
echo   Nome: prototype-melhoria
echo   Publico: SIM
echo   README/gitignore/license: NAO
echo.
echo Pressione ENTER para continuar...
pause >nul

echo.
echo Enviando codigo para o GitHub...
echo.

git push -u origin main

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo   SUCESSO! Codigo enviado!
    echo ========================================
    echo.
    echo PROXIMO PASSO: Ativar GitHub Pages
    echo   1. Va para: Settings ^> Pages
    echo   2. Branch: main, pasta: / (root^)
    echo   3. Clique em Save
    echo.
    echo Seu site estara em:
    echo https://rafaelst97.github.io/prototype-melhoria/
    echo.
) else (
    echo.
    echo ========================================
    echo   ERRO ao enviar codigo
    echo ========================================
    echo.
    echo Verifique se criou o repositorio corretamente
    echo e tente novamente executando:
    echo   git push -u origin main
    echo.
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul
