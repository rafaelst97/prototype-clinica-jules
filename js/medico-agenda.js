// Agenda do Médico - Integrado com API
let medicoId = null;
let consultasAgenda = [];

// Funções de formatação
function formatarCPF(cpf) {
    if (!cpf) return 'N/A';
    const cleaned = cpf.replace(/\D/g, '');
    if (cleaned.length !== 11) return cpf;
    return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

function formatarTelefone(telefone) {
    if (!telefone) return 'N/A';
    const cleaned = telefone.replace(/\D/g, '');
    if (cleaned.length === 11) {
        return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (cleaned.length === 10) {
        return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return telefone;
}

document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('medico');
    
    medicoId = api.getUserId();
    
    // Carregar dados do médico
    await carregarDadosMedico();
    
    const filtroData = document.getElementById('filtroData');
    if (filtroData) {
        const today = new Date().toISOString().split('T')[0];
        filtroData.value = today;
        
        filtroData.addEventListener('change', async function() {
            await carregarAgenda(this.value);
        });
        
        // Carregar agenda do dia atual
        await carregarAgenda(today);
    }
});

async function carregarDadosMedico() {
    try {
        const medico = await api.get(`/medicos/perfil/${medicoId}`);
        
        // Atualizar CRM na navbar
        const navUser = document.querySelector('.nav-user span');
        if (navUser && medico.crm) {
            navUser.innerHTML = `Dr(a). <strong>${medico.nome}</strong> - CRM ${medico.crm}`;
        }
    } catch (error) {
        console.error('Erro ao carregar dados do médico:', error);
    }
}

async function carregarAgenda(data) {
    try {
        showLoading();
        
        // Usar endpoint com filtro de data
        const url = `/medicos/consultas/${medicoId}?data_inicio=${data}&data_fim=${data}`;
        consultasAgenda = await api.get(url);
        
        renderizarAgenda();
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar agenda:', error);
        showMessage('Erro ao carregar agenda.', 'error');
        hideLoading();
    }
}

function renderizarAgenda() {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;
    
    if (consultasAgenda.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 30px;">Nenhuma consulta agendada para esta data</td></tr>';
        return;
    }
    
    // Ordenar por data_hora_inicio
    consultasAgenda.sort((a, b) => new Date(a.data_hora_inicio) - new Date(b.data_hora_inicio));
    
    tbody.innerHTML = consultasAgenda.map(consulta => {
        const data = new Date(consulta.data_hora_inicio).toLocaleDateString('pt-BR');
        const horario = new Date(consulta.data_hora_inicio).toLocaleTimeString('pt-BR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const statusHtml = renderizarStatusBadge(consulta.status);
        const planoSaude = consulta.paciente?.plano_saude?.nome || 'Particular';
        const cpfFormatado = formatarCPF(consulta.paciente?.cpf);
        
        return `
            <tr>
                <td>${data}</td>
                <td>${horario}</td>
                <td>${consulta.paciente?.nome || 'N/A'}</td>
                <td>${cpfFormatado}</td>
                <td>${planoSaude}</td>
                <td>${statusHtml}</td>
                <td>
                    <button class="btn btn-primary" onclick="verDetalhes(${consulta.id_consulta})" style="padding: 5px 10px;">
                        Ver Detalhes
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderizarStatusBadge(status) {
    const statusConfig = {
        'agendada': { icon: 'clock', color: '#3498db', text: 'Agendada' },
        'confirmada': { icon: 'check-circle', color: '#27ae60', text: 'Confirmada' },
        'cancelada': { icon: 'times-circle', color: '#e74c3c', text: 'Cancelada' },
        'realizada': { icon: 'check-circle', color: '#27ae60', text: 'Realizada' },
        'faltou': { icon: 'exclamation-circle', color: '#e67e22', text: 'Faltou' }
    };
    
    const config = statusConfig[status] || statusConfig['agendada'];
    return `<span style="color: ${config.color};"><i class="fas fa-${config.icon}"></i> ${config.text}</span>`;
}

function extractTime(isoString) {
    const date = new Date(isoString);
    const hora = String(date.getHours()).padStart(2, '0');
    const minuto = String(date.getMinutes()).padStart(2, '0');
    return `${hora}:${minuto}`;
}

async function marcarRealizada(consultaId) {
    if (!confirm('Confirmar que esta consulta foi realizada?')) return;
    
    try {
        await api.put(API_CONFIG.ENDPOINTS.MEDICO_CONSULTA_ATUALIZAR_STATUS(medicoId, consultaId), {
            status: 'realizada'
        });
        
        showMessage('Consulta marcada como realizada!', 'success');
        await carregarAgenda(document.getElementById('filtroData').value);
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
        showMessage(error.message || 'Erro ao atualizar status.', 'error');
    }
}

async function marcarFaltou(consultaId) {
    if (!confirm('Confirmar que o paciente faltou à consulta?')) return;
    
    try {
        await api.put(API_CONFIG.ENDPOINTS.MEDICO_CONSULTA_ATUALIZAR_STATUS(medicoId, consultaId), {
            status: 'faltou'
        });
        
        showMessage('Consulta marcada como faltou. O sistema irá verificar se o paciente deve ser bloqueado (RN3).', 'success');
        await carregarAgenda(document.getElementById('filtroData').value);
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
        showMessage(error.message || 'Erro ao atualizar status.', 'error');
    }
}

function verDetalhes(consultaId) {
    const consulta = consultasAgenda.find(c => c.id_consulta === consultaId);
    if (!consulta) {
        showMessage('Consulta não encontrada', 'error');
        return;
    }
    
    const data = new Date(consulta.data_hora_inicio).toLocaleDateString('pt-BR');
    const horarioInicio = new Date(consulta.data_hora_inicio).toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    const horarioFim = new Date(consulta.data_hora_fim).toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    const planoSaude = consulta.paciente?.plano_saude?.nome || 'Particular';
    const cpfFormatado = formatarCPF(consulta.paciente?.cpf);
    const telefoneFormatado = formatarTelefone(consulta.paciente?.telefone);
    const statusConfig = {
        'agendada': { icon: 'clock', color: '#3498db', text: 'Agendada' },
        'confirmada': { icon: 'check-circle', color: '#27ae60', text: 'Confirmada' },
        'cancelada': { icon: 'times-circle', color: '#e74c3c', text: 'Cancelada' },
        'realizada': { icon: 'check-circle', color: '#27ae60', text: 'Realizada' },
        'faltou': { icon: 'exclamation-circle', color: '#e67e22', text: 'Faltou' }
    };
    const statusInfo = statusConfig[consulta.status] || statusConfig['agendada'];
    
    // Criar modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 10px;
        max-width: 600px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    `;
    
    modalContent.innerHTML = `
        <h3 style="color: var(--primary-color); margin-top: 0; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-calendar-check"></i> Detalhes da Consulta
        </h3>
        
        <div style="display: grid; gap: 15px;">
            <div style="border-bottom: 1px solid #eee; padding-bottom: 10px;">
                <strong style="color: #666; display: block; margin-bottom: 5px;">Data e Horário</strong>
                <div style="font-size: 16px;">
                    <i class="far fa-calendar"></i> ${data} | 
                    <i class="far fa-clock"></i> ${horarioInicio} - ${horarioFim}
                </div>
            </div>
            
            <div style="border-bottom: 1px solid #eee; padding-bottom: 10px;">
                <strong style="color: #666; display: block; margin-bottom: 5px;">Paciente</strong>
                <div style="font-size: 16px;">
                    <i class="fas fa-user"></i> ${consulta.paciente?.nome || 'N/A'}
                </div>
            </div>
            
            <div style="border-bottom: 1px solid #eee; padding-bottom: 10px;">
                <strong style="color: #666; display: block; margin-bottom: 5px;">CPF</strong>
                <div style="font-size: 16px;">
                    <i class="fas fa-id-card"></i> ${cpfFormatado}
                </div>
            </div>
            
            <div style="border-bottom: 1px solid #eee; padding-bottom: 10px;">
                <strong style="color: #666; display: block; margin-bottom: 5px;">Contatos</strong>
                <div style="font-size: 16px;">
                    <div style="margin-bottom: 5px;">
                        <i class="fas fa-phone"></i> ${telefoneFormatado}
                    </div>
                    <div>
                        <i class="fas fa-envelope"></i> ${consulta.paciente?.email || 'N/A'}
                    </div>
                </div>
            </div>
            
            <div style="border-bottom: 1px solid #eee; padding-bottom: 10px;">
                <strong style="color: #666; display: block; margin-bottom: 5px;">Plano de Saúde</strong>
                <div style="font-size: 16px;">
                    <i class="fas fa-hospital"></i> ${planoSaude}
                </div>
            </div>
            
            <div>
                <strong style="color: #666; display: block; margin-bottom: 5px;">Status</strong>
                <div style="font-size: 16px; color: ${statusInfo.color};">
                    <i class="fas fa-${statusInfo.icon}"></i> ${statusInfo.text}
                </div>
            </div>
        </div>
        
        <div style="margin-top: 25px; text-align: right;">
            <button id="closeModal" class="btn btn-primary" style="padding: 10px 30px;">
                Fechar
            </button>
        </div>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Fechar modal ao clicar no botão ou fora do conteúdo
    document.getElementById('closeModal').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

function showLoading() {
    const loading = document.createElement('div');
    loading.id = 'loading';
    loading.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255,255,255,0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    loading.innerHTML = '<i class="fas fa-spinner fa-spin" style="font-size: 48px; color: var(--primary-color);"></i>';
    document.body.appendChild(loading);
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.remove();
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
