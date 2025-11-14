/**
 * Configuração de Ambiente
 * Sistema Clínica Saúde+ v2.0.0
 * 
 * Detecta automaticamente o ambiente e configura a URL da API
 */

(function() {
    'use strict';

    // Detectar ambiente
    const hostname = window.location.hostname;
    let apiUrl;

    // 1. Produção - Render.com
    if (hostname.includes('onrender.com')) {
        apiUrl = 'https://clinica-saude-backend.onrender.com';
    }
    // 2. GitHub Codespaces
    else if (hostname.includes('github.dev')) {
        // Substitui porta 80 por 8000 para acessar o backend
        apiUrl = window.location.origin.replace('-80.', '-8000.');
    }
    // 3. Railway.app
    else if (hostname.includes('railway.app')) {
        apiUrl = window.ENV?.API_URL || 'https://clinica-saude-backend.up.railway.app';
    }
    // 4. Fly.io
    else if (hostname.includes('fly.dev')) {
        apiUrl = window.ENV?.API_URL || 'https://clinica-saude-backend.fly.dev';
    }
    // 5. Localhost (desenvolvimento)
    else {
        apiUrl = 'http://localhost:8000';
    }

    // Criar objeto de configuração global
    window.ENV = window.ENV || {};
    window.ENV.API_URL = apiUrl;

    // Log para debug (remover em produção)
    console.log('🌐 Ambiente detectado:', hostname);
    console.log('🔗 API URL configurada:', apiUrl);

})();
