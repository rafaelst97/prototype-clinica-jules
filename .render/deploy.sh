#!/bin/bash

# Script de Deploy Automático para Render.com
# Clínica Saúde+ v2.0.0

echo "=========================================="
echo "🚀 Deploy para Render.com"
echo "=========================================="

# Verificar se está logado no Render
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI não encontrado"
    echo "📥 Instalando Render CLI..."
    npm install -g render-cli
fi

# Fazer login no Render (se necessário)
echo "🔐 Verificando autenticação Render..."
render whoami || render login

# Criar Blueprint no Render
echo "📋 Criando serviços no Render..."
render blueprint create

echo ""
echo "=========================================="
echo "✅ Deploy iniciado com sucesso!"
echo "=========================================="
echo ""
echo "📊 Acompanhe o deploy em:"
echo "https://dashboard.render.com"
echo ""
echo "⏱️  O deploy pode levar 5-10 minutos"
echo ""
echo "🌐 URLs após deploy completo:"
echo "- Frontend: https://clinica-saude-frontend.onrender.com"
echo "- Backend: https://clinica-saude-backend.onrender.com"
echo "- API Docs: https://clinica-saude-backend.onrender.com/docs"
echo ""
echo "=========================================="
