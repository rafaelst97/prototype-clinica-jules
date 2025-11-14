#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║         🏥 Sistema Clínica Saúde+ - Full Stack 🏥          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "📦 Parando containers existentes..."
docker-compose down

echo ""
echo "🔨 Construindo imagens Docker..."
docker-compose build

echo ""
echo "🚀 Iniciando containers..."
docker-compose up -d

echo ""
echo "⏳ Aguardando serviços iniciarem (30s)..."
sleep 30

echo ""
echo "📊 Status dos containers:"
docker-compose ps

echo ""
echo "🌐 Serviços disponíveis:"
echo "   ✅ Frontend:    http://localhost"
echo "   ✅ API Docs:    http://localhost:8000/docs"
echo "   ✅ PostgreSQL:  localhost:5432"

echo ""
echo "🔑 Credenciais de Teste:"
echo "   Admin: admin@clinica.com / admin123"

echo ""
echo "📝 Comandos úteis:"
echo "   Ver logs:       docker-compose logs -f"
echo "   Parar:          docker-compose down"
echo "   Reiniciar:      docker-compose restart"
echo "   Resetar dados:  docker-compose down -v && docker-compose up -d"

echo ""
echo "✨ Sistema pronto para uso!"
echo ""
