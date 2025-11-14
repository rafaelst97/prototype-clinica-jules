// Dashboard do Médico - Integrado com API
let medicoId = null;

document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('medico');
    
    medicoId = api.getUserId();
    await carregarDadosMedico();
    await carregarConsultasHoje();
    await carregarEstatisticas();
});

async function carregarDadosMedico() {
    try {
        const medico = await api.get(`/medicos/perfil/${medicoId}`);
        
        const doctorNameElement = document.getElementById('doctorName');
        if (doctorNameElement) {
            doctorNameElement.textContent = medico.nome || 'Médico';
        }
        
        // Atualizar CRM na navbar
        const navUser = document.querySelector('.nav-user span');
        if (navUser && medico.crm) {
            navUser.innerHTML = `Dr(a). <strong id="doctorName">${medico.nome}</strong> - CRM ${medico.crm}`;
        }
    } catch (error) {
        console.error('Erro ao carregar dados do médico:', error);
        showMessage('Erro ao carregar dados do médico', 'error');
    }
}

async function carregarConsultasHoje() {
    try {
        const consultasHoje = await api.get(`/medicos/consultas/hoje/${medicoId}`);
        
        const tbody = document.querySelector('tbody');
        if (!tbody) return;
        
        if (consultasHoje.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 30px;">Nenhuma consulta agendada para hoje</td></tr>';
            return;
        }
        
        tbody.innerHTML = consultasHoje.map(consulta => {
            const horario = new Date(consulta.data_hora_inicio).toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            const statusHtml = consulta.status === 'agendada' 
                ? '<span style="color: var(--tertiary-color);"><i class="fas fa-check-circle"></i> Confirmada</span>'
                : consulta.status === 'realizada'
                ? '<span style="color: var(--secondary-color);"><i class="fas fa-check"></i> Realizada</span>'
                : '<span style="color: var(--danger-color);"><i class="fas fa-times-circle"></i> Cancelada</span>';
            
            return `
                <tr>
                    <td>${horario}</td>
                    <td>${consulta.paciente.nome}</td>
                    <td>${statusHtml}</td>
                    <td><a href="consultas.html" style="color: var(--secondary-color);">Ver</a></td>
                </tr>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Erro ao carregar consultas:', error);
        showMessage('Erro ao carregar consultas do dia', 'error');
    }
}

async function carregarEstatisticas() {
    try {
        const stats = await api.get(`/medicos/estatisticas/${medicoId}`);
        
        // Atualizar cards de estatísticas
        const estatisticasDiv = document.querySelector('.card:nth-child(2) > div:nth-child(2)');
        if (estatisticasDiv) {
            estatisticasDiv.innerHTML = `
                <div style="padding: 15px; background: var(--light-bg); border-radius: 5px;">
                    <h4 style="color: var(--secondary-color); margin-bottom: 5px;">${stats.consultas_hoje}</h4>
                    <p>Consultas Hoje</p>
                </div>
                <div style="padding: 15px; background: var(--light-bg); border-radius: 5px;">
                    <h4 style="color: var(--tertiary-color); margin-bottom: 5px;">${stats.consultas_semana}</h4>
                    <p>Consultas Esta Semana</p>
                </div>
                <div style="padding: 15px; background: var(--light-bg); border-radius: 5px;">
                    <h4 style="color: var(--accent-color); margin-bottom: 5px;">${stats.horarios_bloqueados}</h4>
                    <p>Horários Bloqueados</p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        showMessage('Erro ao carregar estatísticas', 'error');
    }
}

function showMessage(message, type = 'info') {
    const colors = {
        'success': { bg: '#27ae60', icon: 'fa-check-circle' },
        'error': { bg: '#e74c3c', icon: 'fa-exclamation-circle' },
        'warning': { bg: '#f39c12', icon: 'fa-exclamation-triangle' },
        'info': { bg: '#3498db', icon: 'fa-info-circle' }
    };
    
    const config = colors[type] || colors['info'];
    
    const alert = document.createElement('div');
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${config.bg};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10001;
        min-width: 300px;
        max-width: 500px;
        font-size: 15px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    alert.innerHTML = `
        <i class="fas ${config.icon}" style="font-size: 20px;"></i>
        <span style="flex: 1;">${message}</span>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => alert.remove(), 300);
    }, 4000);
}
