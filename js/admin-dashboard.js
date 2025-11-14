// Dashboard Admin - Integrado com API
document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('admin');
    
    await carregarDadosDashboard();
});

async function carregarDadosDashboard() {
    try {
        console.log('📊 Carregando dados do dashboard administrativo...');
        console.log('Token:', localStorage.getItem('token') ? 'Presente' : 'Ausente');
        console.log('User Type:', localStorage.getItem('user_type'));
        
        // Carregar estatísticas
        const stats = await api.get(API_CONFIG.ENDPOINTS.ADMIN_DASHBOARD);
        console.log('✅ Estatísticas carregadas:', stats);
        
        // Atualizar cards de estatísticas
        atualizarEstatisticas(stats);
        
        // Carregar consultas recentes
        await carregarConsultasRecentes();
        
        // Carregar alertas
        await carregarAlertas();
        
    } catch (error) {
        console.error('❌ Erro ao carregar dashboard:', error);
        console.error('Detalhes do erro:', error.message);
        
        // Mostrar erro mais detalhado
        let mensagemErro = 'Erro ao carregar dados do dashboard.';
        if (error.message) {
            mensagemErro += ' ' + error.message;
        }
        
        showMessage(mensagemErro, 'error');
        
        // Atualizar UI para mostrar erro
        const cards = document.querySelectorAll('.grid-2 .card:first-child h4');
        cards.forEach(card => {
            card.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        });
    }
}

function atualizarEstatisticas(stats) {
    // Atualizar números nos cards
    const cards = document.querySelectorAll('.grid-2 .card:first-child h4');
    
    if (cards[0]) cards[0].textContent = stats.total_pacientes || 0;
    if (cards[1]) cards[1].textContent = stats.total_medicos || 0;
    if (cards[2]) cards[2].textContent = stats.consultas_mes || 0;
    if (cards[3]) {
        // Calcular cancelamentos (consultas com status Cancelada)
        cards[3].textContent = '...'; // Será atualizado em carregarConsultasRecentes
    }
    
    console.log('📈 Estatísticas atualizadas:', stats);
}

async function carregarConsultasRecentes() {
    try {
        console.log('📅 Carregando consultas recentes...');
        const consultas = await api.get(API_CONFIG.ENDPOINTS.ADMIN_CONSULTAS);
        
        // Ordenar por data (mais recentes primeiro)
        const consultasOrdenadas = consultas.sort((a, b) => {
            return new Date(b.data_hora_inicio) - new Date(a.data_hora_inicio);
        });
        
        // Pegar apenas as 10 mais recentes
        const consultasRecentes = consultasOrdenadas.slice(0, 10);
        
        // Contar cancelamentos
        const cancelamentos = consultas.filter(c => c.status.toLowerCase() === 'cancelada').length;
        const cards = document.querySelectorAll('.grid-2 .card:first-child h4');
        if (cards[3]) {
            cards[3].textContent = cancelamentos;
        }
        console.log(`📊 Cancelamentos encontrados: ${cancelamentos}`);
        
        // Renderizar tabela
        const tbody = document.querySelector('.card.mt-20 tbody');
        if (!tbody) return;
        
        if (consultasRecentes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhuma consulta registrada</td></tr>';
            return;
        }
        
        tbody.innerHTML = consultasRecentes.map(consulta => {
            const dataHora = new Date(consulta.data_hora_inicio);
            const dataFormatada = dataHora.toLocaleDateString('pt-BR');
            const horaFormatada = dataHora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            
            const statusConfig = {
                'agendada': { cor: 'var(--secondary-color)', icone: 'fa-clock' },
                'realizada': { cor: 'var(--tertiary-color)', icone: 'fa-check-circle' },
                'cancelada': { cor: 'var(--accent-color)', icone: 'fa-times-circle' },
                'faltou': { cor: '#ff6b6b', icone: 'fa-user-times' }
            };
            
            const statusLower = consulta.status.toLowerCase();
            const config = statusConfig[statusLower] || { cor: '#666', icone: 'fa-question-circle' };
            const statusCapitalizado = consulta.status.charAt(0).toUpperCase() + consulta.status.slice(1).toLowerCase();
            
            return `
                <tr>
                    <td>${dataFormatada} ${horaFormatada}</td>
                    <td>${consulta.paciente?.nome || 'N/A'}</td>
                    <td>${consulta.medico?.nome || 'N/A'}</td>
                    <td>${consulta.medico?.especialidade?.nome || 'N/A'}</td>
                    <td><span style="color: ${config.cor};"><i class="fas ${config.icone}"></i> ${statusCapitalizado}</span></td>
                </tr>
            `;
        }).join('');
        
        console.log(`✅ ${consultasRecentes.length} consultas renderizadas`);
        
    } catch (error) {
        console.error('❌ Erro ao carregar consultas:', error);
        const tbody = document.querySelector('.card.mt-20 tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="color: var(--accent-color);">Erro ao carregar consultas</td></tr>';
        }
    }
}

async function carregarAlertas() {
    try {
        console.log('⚠️ Carregando alertas...');
        
        // Carregar pacientes
        const pacientes = await api.get(API_CONFIG.ENDPOINTS.ADMIN_PACIENTES);
        
        // Contar pacientes bloqueados
        const pacientesBloqueados = pacientes.filter(p => p.esta_bloqueado).length;
        
        // Atualizar alertas
        const alertContainer = document.querySelector('.card.mt-20:last-of-type');
        if (!alertContainer) return;
        
        const alertasHTML = [];
        
        if (pacientesBloqueados > 0) {
            alertasHTML.push(`
                <div class="alert alert-warning">
                    <strong>${pacientesBloqueados} ${pacientesBloqueados === 1 ? 'paciente está' : 'pacientes estão'}</strong> bloqueado(s) por faltas consecutivas
                </div>
            `);
        }
        
        // Adicionar mais alertas conforme necessário
        alertasHTML.push(`
            <div class="alert alert-info">
                Sistema operando normalmente - ${new Date().toLocaleDateString('pt-BR')}
            </div>
        `);
        
        const headerHTML = alertContainer.querySelector('.card-header').outerHTML;
        alertContainer.innerHTML = headerHTML + alertasHTML.join('');
        
        console.log('✅ Alertas atualizados');
        
    } catch (error) {
        console.error('❌ Erro ao carregar alertas:', error);
    }
}

function showMessage(message, type = 'error') {
    const alertClass = type === 'error' ? 'alert-error' : 'alert-success';
    const alertHTML = `
        <div class="alert ${alertClass}" style="position: fixed; top: 20px; right: 20px; z-index: 9999; animation: slideIn 0.3s ease-out;">
            ${message}
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHTML);
    
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            alert.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => alert.remove(), 300);
        }
    }, 4000);
}
