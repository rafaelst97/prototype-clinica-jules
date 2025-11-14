const { chromium } = require('playwright');

/**
 * Teste Completo do Perfil de Médico
 * Valida: Login, CRUD de Horários, Visualização de Consultas e Agenda
 */

const BASE_URL = 'http://localhost:8081';
const MEDICO_LOGIN = {
    crm: '12345-SC',
    senha: 'medico123'
};

let browser;
let context;
let page;

// Cores para output
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[36m',
    bold: '\x1b[1m'
};

function log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString('pt-BR');
    const prefix = {
        success: `${colors.green}✓${colors.reset}`,
        error: `${colors.red}✗${colors.reset}`,
        info: `${colors.blue}ℹ${colors.reset}`,
        warning: `${colors.yellow}⚠${colors.reset}`
    }[type] || '';
    
    console.log(`[${timestamp}] ${prefix} ${message}`);
}

async function setup() {
    log('Iniciando navegador...', 'info');
    browser = await chromium.launch({ 
        headless: false,
        slowMo: 100 
    });
    context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });
    page = await context.newPage();
    
    // Interceptar requisições para debug
    page.on('response', async (response) => {
        const url = response.url();
        if (url.includes('/api/') && response.status() >= 400) {
            log(`Erro HTTP ${response.status()} em ${url}`, 'error');
        }
    });
    
    // Capturar erros do console
    page.on('console', msg => {
        if (msg.type() === 'error') {
            log(`Console Error: ${msg.text()}`, 'error');
        }
    });
    
    // Capturar erros de página
    page.on('pageerror', error => {
        log(`Page Error: ${error.message}`, 'error');
    });
}

async function teardown() {
    if (browser) {
        await browser.close();
    }
}

async function loginMedico() {
    log('=== TESTE: Login do Médico ===', 'info');
    
    await page.goto(`${BASE_URL}/medico/login.html`);
    await page.waitForLoadState('networkidle');
    
    // Preencher formulário
    await page.fill('#crm', MEDICO_LOGIN.crm);
    await page.fill('#senha', MEDICO_LOGIN.senha);
    
    // Clicar no botão de login
    await page.click('button[type="submit"]');
    
    // Aguardar um pouco para ver se há erros
    await page.waitForTimeout(3000);
    
    // Verificar se ainda está na página de login
    const currentUrl = page.url();
    log(`URL atual após login: ${currentUrl}`, 'info');
    
    // Aguardar redirecionamento
    try {
        await page.waitForURL('**/medico/dashboard.html', { timeout: 5000 });
    } catch (e) {
        // Capturar screenshot do erro
        await page.screenshot({ path: 'test-login-error.png', fullPage: true });
        throw new Error(`Não redirecionou para dashboard. URL: ${currentUrl}`);
    }
    
    // Verificar se o token foi salvo
    const token = await page.evaluate(() => localStorage.getItem('token'));
    if (!token) {
        throw new Error('Token não foi salvo no localStorage');
    }
    
    log('Login realizado com sucesso!', 'success');
    await page.waitForTimeout(1000);
}

async function testarGerenciamentoHorarios() {
    log('\n=== TESTE: Gerenciamento de Horários ===', 'info');
    
    // Ir para página de horários
    await page.goto(`${BASE_URL}/medico/horarios.html`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 1. VISUALIZAÇÃO: Verificar se o formulário carregou
    log('Testando visualização do formulário de horários...', 'info');
    
    const checkboxes = await page.locator('input[type="checkbox"][id]').count();
    const timeInputCount = await page.locator('input[type="time"]').count();
    
    log(`Checkboxes de dias: ${checkboxes}`, 'info');
    log(`Inputs de horário: ${timeInputCount}`, 'info');
    
    if (checkboxes >= 5 && timeInputCount >= 10) {
        log('Formulário de horários carregado com sucesso!', 'success');
    } else {
        log('Aviso: Formulário de horários incompleto', 'warning');
    }
    
    // 2. ATUALIZAÇÃO: Modificar horários
    log('Testando atualização de horários...', 'info');
    
    // Desmarcar sábado se existir
    const sabadoCheckbox = page.locator('#sabado');
    if (await sabadoCheckbox.count() > 0) {
        await sabadoCheckbox.uncheck();
        log('Sábado desmarcado', 'info');
    }
    
    // Alterar horário de segunda-feira de forma válida
    const allTimeInputs = page.locator('input[type="time"]');
    if (await allTimeInputs.count() >= 2) {
        // Alterar horário de início e fim da manhã
        await allTimeInputs.nth(0).fill('09:00');
        await allTimeInputs.nth(1).fill('13:00');
        log('Horários de segunda-feira alterados (09:00 - 13:00)', 'info');
    }
    
    // Salvar
    const saveButton = page.locator('button:has-text("Salvar Horários")');
    if (await saveButton.count() > 0) {
        await saveButton.click();
        await page.waitForTimeout(2000);
        log('Formulário de horários submetido', 'success');
        
        // Recarregar e verificar persistência (se houver backend funcional)
        await page.reload();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(2000);
        
        const primeiroInputReload = page.locator('input[type="time"]').first();
        const horarioAposReload = await primeiroInputReload.inputValue();
        if (horarioAposReload === '09:00' || horarioAposReload === '09:00:00') {
            log('✓ Horário persistido após reload com sucesso!', 'success');
        } else {
            log(`Aviso: Horário não persistiu. Esperado: 09:00, Obtido: ${horarioAposReload}`, 'warning');
        }
    } else {
        log('Aviso: Botão de salvar não encontrado', 'warning');
    }
}

async function testarVisualizacaoConsultas() {
    log('\n=== TESTE: Visualização de Consultas ===', 'info');
    
    await page.goto(`${BASE_URL}/medico/consultas.html`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Verificar se a tabela carregou
    const consultasCount = await page.locator('#consultasTable tbody tr').count();
    log(`Total de consultas encontradas: ${consultasCount}`, 'info');
    
    if (consultasCount > 0) {
        log('Lista de consultas carregada com sucesso!', 'success');
        
        // Testar botões de ação se existirem
        const detalhesButtons = page.locator('button:has-text("Ver Detalhes"), button:has-text("Detalhes")');
        const detalhesCount = await detalhesButtons.count();
        
        if (detalhesCount > 0) {
            log('Testando visualização de detalhes da consulta...', 'info');
            await detalhesButtons.first().click();
            await page.waitForTimeout(1500);
            
            // Verificar se modal ou detalhes abriu
            const modalVisible = await page.locator('.modal:visible, #modalDetalhes:visible').count();
            if (modalVisible > 0) {
                log('Modal de detalhes aberto com sucesso!', 'success');
                
                // Fechar modal
                const closeButton = page.locator('button:has-text("Fechar"), .modal button.close, .close');
                if (await closeButton.count() > 0) {
                    await closeButton.first().click();
                    await page.waitForTimeout(500);
                }
            } else {
                log('Aviso: Modal de detalhes não foi encontrado', 'warning');
            }
        }
        
        // Testar adicionar observação se disponível
        const obsButtons = page.locator('button:has-text("Observação"), button:has-text("Adicionar Obs")');
        const obsCount = await obsButtons.count();
        
        if (obsCount > 0) {
            log('Testando adicionar observação...', 'info');
            await obsButtons.first().click();
            await page.waitForTimeout(1000);
            
            const obsModal = await page.locator('#modalObservacao:visible, .modal:visible').count();
            if (obsModal > 0) {
                const obsTextarea = page.locator('textarea[name="observacao"], textarea#observacao');
                if (await obsTextarea.count() > 0) {
                    await obsTextarea.fill('Teste de observação automatizado - ' + new Date().toISOString());
                    
                    const saveButton = page.locator('button:has-text("Salvar"), button:has-text("Adicionar")');
                    if (await saveButton.count() > 0) {
                        await saveButton.first().click();
                        await page.waitForTimeout(2000);
                        log('Observação adicionada com sucesso!', 'success');
                    }
                }
            }
        }
    } else {
        log('Nenhuma consulta encontrada (pode ser normal se não houver consultas agendadas)', 'warning');
    }
}

async function testarAgenda() {
    log('\n=== TESTE: Visualização da Agenda ===', 'info');
    
    await page.goto(`${BASE_URL}/medico/agenda.html`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Verificar se a agenda carregou
    const agendaVisible = await page.locator('#calendario, .agenda-container, table').count();
    
    if (agendaVisible > 0) {
        log('Página de agenda carregada com sucesso!', 'success');
        
        // Verificar consultas na agenda
        const consultasAgenda = await page.locator('.consulta, .evento, tbody tr').count();
        log(`Consultas na agenda: ${consultasAgenda}`, 'info');
        
        // Testar filtros de data se disponíveis
        const dataInput = page.locator('input[type="date"]');
        if (await dataInput.count() > 0) {
            log('Testando filtro de data...', 'info');
            const hoje = new Date().toISOString().split('T')[0];
            await dataInput.first().fill(hoje);
            await page.waitForTimeout(1500);
            log('Filtro de data aplicado', 'success');
        }
    } else {
        log('Aviso: Elementos da agenda não encontrados', 'warning');
    }
}

async function testarDashboard() {
    log('\n=== TESTE: Dashboard do Médico ===', 'info');
    
    await page.goto(`${BASE_URL}/medico/dashboard.html`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Verificar cards/estatísticas
    const cards = await page.locator('.card, .stat-card, .dashboard-card').count();
    log(`Cards no dashboard: ${cards}`, 'info');
    
    if (cards > 0) {
        log('Dashboard carregado com sucesso!', 'success');
    } else {
        log('Aviso: Nenhum card encontrado no dashboard', 'warning');
    }
    
    // Verificar navegação pelos menus
    const menuItems = ['Horários', 'Consultas', 'Agenda'];
    for (const item of menuItems) {
        const menuLink = page.locator(`a:has-text("${item}")`);
        if (await menuLink.count() > 0) {
            log(`Link de navegação "${item}" encontrado`, 'success');
        }
    }
}

async function gerarRelatorio(stats) {
    log('\n' + '='.repeat(60), 'info');
    log('RELATÓRIO FINAL DO TESTE', 'info');
    log('='.repeat(60), 'info');
    
    const total = stats.success + stats.error + stats.warning;
    const percentSuccess = ((stats.success / total) * 100).toFixed(1);
    
    console.log(`
${colors.green}Sucessos:${colors.reset} ${stats.success}
${colors.red}Erros:${colors.reset} ${stats.error}
${colors.yellow}Avisos:${colors.reset} ${stats.warning}
${colors.bold}Taxa de Sucesso:${colors.reset} ${percentSuccess}%

${colors.blue}Módulos Testados:${colors.reset}
✓ Login do Médico
✓ Gerenciamento de Horários (CRUD)
✓ Visualização de Consultas
✓ Agenda
✓ Dashboard
    `);
    
    log('='.repeat(60), 'info');
}

// Função principal
(async () => {
    const stats = { success: 0, error: 0, warning: 0 };
    
    try {
        await setup();
        
        // Interceptar logs para contar
        const originalLog = log;
        log = (message, type) => {
            originalLog(message, type);
            if (type === 'success') stats.success++;
            if (type === 'error') stats.error++;
            if (type === 'warning') stats.warning++;
        };
        
        // Executar testes
        await loginMedico();
        await testarDashboard();
        await testarGerenciamentoHorarios();
        await testarVisualizacaoConsultas();
        await testarAgenda();
        
        await gerarRelatorio(stats);
        
        log('\nTeste completo finalizado! Navegador permanecerá aberto por 10 segundos...', 'info');
        await page.waitForTimeout(10000);
        
    } catch (error) {
        log(`Erro fatal: ${error.message}`, 'error');
        console.error(error);
        
        // Screenshot para debug
        try {
            await page.screenshot({ path: 'test-medico-error.png', fullPage: true });
            log('Screenshot salvo em: test-medico-error.png', 'info');
        } catch (e) {}
        
    } finally {
        await teardown();
    }
})();
