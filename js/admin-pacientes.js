// Gerenciar Pacientes - Admin - Integrado com API
let pacientes = [];
let pacientesFiltrados = [];

document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('administrador');
    
    await carregarPacientes();
    configurarBusca();
});

// Carregar lista de pacientes
async function carregarPacientes() {
    try {
        showLoading();
        pacientes = await api.get(API_CONFIG.ENDPOINTS.ADMIN_PACIENTES_LISTAR);
        pacientesFiltrados = [...pacientes];
        renderizarPacientes();
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar pacientes:', error);
        showMessage('Erro ao carregar pacientes: ' + error.message, 'error');
        hideLoading();
    }
}

// Renderizar lista de pacientes
function renderizarPacientes() {
    const tbody = document.querySelector('tbody');
    
    if (!tbody) return;
    
    if (pacientesFiltrados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 30px;">Nenhum paciente encontrado</td></tr>';
        return;
    }
    
    tbody.innerHTML = pacientesFiltrados.map(paciente => {
        // Dados do paciente vindos do backend
        const planoSaude = paciente.plano_saude || null;
        const bloqueado = paciente.esta_bloqueado || false;
        
        // Estatísticas de consultas vindas do backend
        const totalConsultas = paciente.total_consultas || 0;
        const consultasAgendadas = paciente.consultas_agendadas || 0;
        
        // Determinar status
        let statusHtml = '';
        let rowStyle = '';
        
        if (bloqueado) {
            statusHtml = '<span style="color: var(--accent-color);"><i class="fas fa-ban"></i> Bloqueado</span>';
            rowStyle = 'background: #ffcccc;';
        } else if (consultasAgendadas >= 2) {
            // RN2: Limite de 2 consultas futuras - destacar quando atingir o limite
            statusHtml = '<span style="color: var(--accent-color);"><i class="fas fa-exclamation-circle"></i> Limite de Agendamentos</span>';
            rowStyle = 'background: #fff3cd;';
        } else {
            statusHtml = '<span style="color: var(--tertiary-color);"><i class="fas fa-check-circle"></i> Ativo</span>';
        }
        
        // Botões de ação
        let acoesHtml = '';
        if (bloqueado) {
            acoesHtml = `
                <button class="btn btn-tertiary" style="padding: 5px 10px; margin-right: 5px;" onclick="desbloquearPaciente(${paciente.id_paciente})">
                    <i class="fas fa-unlock"></i> Desbloquear
                </button>
                <button class="btn btn-secondary" style="padding: 5px 10px;" onclick="verDetalhesPaciente(${paciente.id_paciente})">
                    <i class="fas fa-eye"></i> Detalhes
                </button>
            `;
        } else {
            acoesHtml = `
                <button class="btn btn-secondary" style="padding: 5px 10px; margin-right: 5px;" onclick="verDetalhesPaciente(${paciente.id_paciente})">
                    <i class="fas fa-eye"></i> Ver Detalhes
                </button>
            `;
        }
        
        return `
            <tr style="${rowStyle}">
                <td>${paciente.nome || 'N/A'}</td>
                <td>${formatarCPF(paciente.cpf || '')}</td>
                <td>${formatarTelefone(paciente.telefone || '')}</td>
                <td>${planoSaude ? planoSaude.nome : 'Particular'}</td>
                <td style="text-align: center;">${totalConsultas}</td>
                <td style="text-align: center;">${consultasAgendadas}</td>
                <td>${statusHtml}</td>
                <td>${acoesHtml}</td>
            </tr>
        `;
    }).join('');
}

// Configurar busca
function configurarBusca() {
    const searchInput = document.getElementById('buscaPaciente');
    
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const termo = this.value.toLowerCase().trim();
        
        if (!termo) {
            pacientesFiltrados = [...pacientes];
        } else {
            pacientesFiltrados = pacientes.filter(paciente => {
                const nome = (paciente.nome || '').toLowerCase();
                const cpf = (paciente.cpf || '').replace(/\D/g, '');
                const termoBusca = termo.replace(/\D/g, '');
                
                return nome.includes(termo) || cpf.includes(termoBusca);
            });
        }
        
        renderizarPacientes();
    });
}

// Ver detalhes do paciente
async function verDetalhesPaciente(pacienteId) {
    try {
        showLoading();
        const paciente = await api.get(`/admin/pacientes/${pacienteId}`);
        hideLoading();
        
        // Buscar estatísticas de consultas
        const pacienteComEstatisticas = pacientes.find(p => p.id_paciente === pacienteId);
        const totalConsultas = pacienteComEstatisticas?.total_consultas || 0;
        const consultasAgendadas = pacienteComEstatisticas?.consultas_agendadas || 0;
        
        const detalhesHtml = `
            <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
                <h3 style="margin-bottom: 20px; color: var(--primary-color);">
                    <i class="fas fa-user"></i> Detalhes do Paciente
                </h3>
                
                <div style="margin-bottom: 15px;">
                    <strong>Nome:</strong> ${paciente.nome || 'N/A'}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Email:</strong> ${paciente.email || 'N/A'}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>CPF:</strong> ${formatarCPF(paciente.cpf || '')}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Data de Nascimento:</strong> ${formatarData(paciente.data_nascimento)}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Telefone:</strong> ${formatarTelefone(paciente.telefone || '')}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Convênio:</strong> ${paciente.plano_saude ? paciente.plano_saude.nome : 'Particular'}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Total de Consultas:</strong> ${totalConsultas}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Faltas:</strong> 0
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Status:</strong> 
                    ${paciente.esta_bloqueado ? 
                        '<span style="color: var(--accent-color);"><i class="fas fa-ban"></i> Bloqueado</span>' : 
                        '<span style="color: var(--tertiary-color);"><i class="fas fa-check-circle"></i> Ativo</span>'
                    }
                </div>
                
                <button onclick="fecharModal()" class="btn btn-secondary" style="margin-top: 20px;">
                    <i class="fas fa-times"></i> Fechar
                </button>
            </div>
        `;
        
        mostrarModal(detalhesHtml);
        
    } catch (error) {
        console.error('Erro ao carregar detalhes:', error);
        showMessage('Erro ao carregar detalhes do paciente: ' + error.message, 'error');
        hideLoading();
    }
}

// Desbloquear paciente (RN3 - desbloquear após 3 faltas consecutivas)
async function desbloquearPaciente(pacienteId) {
    if (!confirm('Deseja realmente desbloquear este paciente? Isso irá zerar o contador de faltas consecutivas.')) {
        return;
    }
    
    try {
        showLoading();
        await api.post(API_CONFIG.ENDPOINTS.ADMIN_PACIENTE_DESBLOQUEAR(pacienteId), {});
        showMessage('Paciente desbloqueado com sucesso! Contador de faltas zerado.', 'success');
        await carregarPacientes();
        hideLoading();
    } catch (error) {
        console.error('Erro ao desbloquear:', error);
        showMessage('Erro ao desbloquear paciente: ' + error.message, 'error');
        hideLoading();
    }
}

// Funções auxiliares de formatação
function formatarCPF(cpf) {
    if (!cpf) return 'N/A';
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

function formatarTelefone(telefone) {
    if (!telefone) return 'N/A';
    telefone = telefone.replace(/\D/g, '');
    if (telefone.length === 11) {
        return telefone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (telefone.length === 10) {
        return telefone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return telefone;
}

function formatarCEP(cep) {
    if (!cep) return 'N/A';
    cep = cep.replace(/\D/g, '');
    return cep.replace(/(\d{5})(\d{3})/, '$1-$2');
}

function formatarData(data) {
    if (!data) return 'N/A';
    const d = new Date(data + 'T00:00:00');
    return d.toLocaleDateString('pt-BR');
}

function formatarDataHora(dataHora) {
    if (!dataHora) return 'N/A';
    const d = new Date(dataHora);
    return d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR');
}

// Funções de UI
function mostrarModal(html) {
    const modal = document.createElement('div');
    modal.id = 'modalDetalhes';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        overflow-y: auto;
        padding: 20px;
    `;
    modal.innerHTML = html;
    modal.onclick = (e) => {
        if (e.target === modal) fecharModal();
    };
    document.body.appendChild(modal);
}

function fecharModal() {
    const modal = document.getElementById('modalDetalhes');
    if (modal) modal.remove();
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

function showMessage(message, type) {
    const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-danger' : 'alert-warning';
    const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-exclamation-triangle';
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass}`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10001;
        min-width: 300px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    alert.innerHTML = `<i class="fas ${icon}"></i> ${message}`;
    document.body.appendChild(alert);
    
    setTimeout(() => alert.remove(), 5000);
}
