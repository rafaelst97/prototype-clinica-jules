#!/bin/bash

# Script de setup para GitHub Codespaces
# Sistema Clínica Saúde+ v2.0.0

echo "=================================================="
echo "🏥 Configurando Clínica Saúde+ no Codespaces..."
echo "=================================================="

# Navegar para o diretório do backend
cd /app/backend || exit 1

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir -r requirements-test.txt

# Voltar para o diretório raiz
cd /app || exit 1

# Dar permissões de execução para scripts
echo "🔧 Configurando permissões..."
chmod +x .devcontainer/setup.sh 2>/dev/null || true

# Exibir mensagem de sucesso
echo ""
echo "=================================================="
echo "✅ Setup concluído com sucesso!"
echo "=================================================="
echo ""
echo "🚀 Próximos passos:"
echo ""
echo "1. Inicie os containers Docker:"
echo "   docker-compose up -d"
echo ""
echo "2. Acesse o sistema:"
echo "   - Frontend: Porta 80 (será aberta automaticamente)"
echo "   - Backend API: Porta 8000"
echo "   - PostgreSQL: Porta 5432"
echo "   - pgAdmin: Porta 5050"
echo ""
echo "3. Usuários de teste:"
echo "   - Paciente: maria@email.com / paciente123"
echo "   - Médico: joao1@clinica.com / medico123"
echo "   - Admin: admin@clinica.com / admin123"
echo ""
echo "=================================================="
echo "📚 Documentação: README.md"
echo "🐛 Issues: https://github.com/rafaelst97/prototype-melhoria/issues"
echo "=================================================="
