const http = require('http');

// Teste 1: API
console.log(' Testando API...');
http.get('http://localhost:8000/pacientes/planos-saude', (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        const planos = JSON.parse(data);
        console.log( API retornou  planos);
        planos.forEach(p => console.log(  -  (ID: )));
    });
}).on('error', err => console.error(' Erro API:', err.message));

// Teste 2: HTML
console.log('\n Testando HTML...');
http.get('http://localhost/paciente/cadastro.html', (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        console.log( HTML carregado ( bytes));
        const hasSelect = data.includes('id=\"convenio\"');
        const hasScript = data.includes('paciente-cadastro.js');
        console.log(  - Tem select convenio: );
        console.log(  - Carrega paciente-cadastro.js: );
    });
}).on('error', err => console.error(' Erro HTML:', err.message));
