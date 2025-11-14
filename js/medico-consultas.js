// Variáveis globais
let medicoId = null;
let todasConsultas = [];

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

// Carregar consultas ao iniciar
document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('medico');
    
    medicoId = api.getUserId();
    
    // Carregar dados do médico na navbar
    await carregarDadosMedico();
    
    // Definir datas padrão (últimos 30 dias até hoje)
    const hoje = new Date();
    const dataFim = hoje.toISOString().split('T')[0];
    const dataInicio = new Date(hoje.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    document.getElementById('dataInicio').value = dataInicio;
    document.getElementById('dataFim').value = dataFim;
    
    await carregarConsultas();
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

// Carregar consultas do médico
async function carregarConsultas() {
    try {
        showLoading();
        
        const dataInicio = document.getElementById('dataInicio').value;
        const dataFim = document.getElementById('dataFim').value;
        
        let url = `/medicos/consultas/${medicoId}`;
        
        if (dataInicio && dataFim) {
            url += `?data_inicio=${dataInicio}&data_fim=${dataFim}`;
        } else if (dataInicio) {
            url += `?data_inicio=${dataInicio}`;
        } else if (dataFim) {
            url += `?data_fim=${dataFim}`;
        }
        
        todasConsultas = await api.get(url);
        renderizarConsultas(todasConsultas);
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar consultas:', error);
        showMessage('Erro ao carregar consultas.', 'error');
        hideLoading();
    }
}

// Renderizar lista de consultas
function renderizarConsultas(consultas) {
    const container = document.getElementById('listaConsultas');
    
    if (!container) return;
    
    if (!consultas || consultas.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <i class="fas fa-calendar-times" style="font-size: 48px; margin-bottom: 15px; color: #ccc;"></i>
                <p style="font-size: 16px;">Nenhuma consulta encontrada no período selecionado.</p>
            </div>
        `;
        return;
    }
    
    // Ordenar por data mais recente primeiro
    consultas.sort((a, b) => new Date(b.data_hora_inicio) - new Date(a.data_hora_inicio));
    
    const statusConfig = {
        'agendada': { color: '#3498db', text: 'Agendada', icon: 'clock' },
        'confirmada': { color: '#27ae60', text: 'Confirmada', icon: 'check-circle' },
        'cancelada': { color: '#e74c3c', text: 'Cancelada', icon: 'times-circle' },
        'realizada': { color: '#27ae60', text: 'Realizada', icon: 'check-circle' },
        'faltou': { color: '#e67e22', text: 'Faltou', icon: 'exclamation-circle' }
    };
    
    const html = consultas.map(consulta => {
        const dataHora = new Date(consulta.data_hora_inicio);
        const data = dataHora.toLocaleDateString('pt-BR');
        const horario = dataHora.toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'});
        const statusInfo = statusConfig[consulta.status] || statusConfig['agendada'];
        const planoSaude = consulta.paciente?.plano_saude?.nome || 'Particular';
        
        // Mostrar botão de observação apenas para consultas realizadas ou agendadas
        const podeAdicionarObservacao = ['agendada', 'confirmada', 'realizada'].includes(consulta.status);
        
        return `
            <div style="background: white; border: 1px solid #e0e0e0; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 10px 0; color: var(--primary-color); font-size: 18px;">
                            <i class="fas fa-user-circle"></i> ${consulta.paciente?.nome || 'Paciente'}
                        </h4>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; font-size: 14px; color: #555;">
                            <div>
                                <i class="far fa-calendar"></i> <strong>Data:</strong> ${data}
                            </div>
                            <div>
                                <i class="far fa-clock"></i> <strong>Horário:</strong> ${horario}
                            </div>
                            <div>
                                <i class="fas fa-hospital"></i> <strong>Plano:</strong> ${planoSaude}
                            </div>
                            <div>
                                <i class="fas fa-${statusInfo.icon}" style="color: ${statusInfo.color};"></i> 
                                <strong>Status:</strong> <span style="color: ${statusInfo.color};">${statusInfo.text}</span>
                            </div>
                        </div>
                    </div>
                    <div>
                        <button onclick="verDetalhesConsulta(${consulta.id_consulta})" class="btn btn-primary" style="padding: 8px 15px;">
                            <i class="fas fa-eye"></i> Ver Detalhes
                        </button>
                        ${podeAdicionarObservacao ? `
                            <button onclick="abrirModalObservacao(${consulta.id_consulta})" class="btn btn-secondary" style="padding: 8px 15px; margin-left: 5px; background: #27ae60;">
                                <i class="fas fa-notes-medical"></i> Observações
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

function filtrarConsultas() {
    carregarConsultas();
}

function limparFiltro() {
    const hoje = new Date();
    const dataFim = hoje.toISOString().split('T')[0];
    const dataInicio = new Date(hoje.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    document.getElementById('dataInicio').value = dataInicio;
    document.getElementById('dataFim').value = dataFim;
    
    carregarConsultas();
}

// Ver detalhes da consulta
async function verDetalhesConsulta(consultaId) {
    const consulta = todasConsultas.find(c => c.id_consulta === consultaId);
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
    
    // Buscar observação se existir
    let observacaoHtml = '';
    try {
        const observacao = await api.get(`/medicos/observacoes/${consultaId}?medico_id=${medicoId}`);
        if (observacao && observacao.descricao) {
            const dataObs = new Date(observacao.data_criacao).toLocaleString('pt-BR');
            observacaoHtml = `
                <div style="border-top: 2px solid #eee; margin-top: 20px; padding-top: 15px;">
                    <strong style="color: #666; display: block; margin-bottom: 10px;">
                        <i class="fas fa-notes-medical"></i> Observação Médica
                    </strong>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #27ae60;">
                        <div style="font-size: 12px; color: #888; margin-bottom: 8px;">
                            Registrada em: ${dataObs}
                        </div>
                        <div style="white-space: pre-wrap; line-height: 1.6;">
                            ${observacao.descricao}
                        </div>
                    </div>
                    <button onclick="editarObservacao(${consultaId}, ${observacao.id_observacao})" class="btn btn-secondary" style="margin-top: 10px; padding: 8px 15px;">
                        <i class="fas fa-edit"></i> Editar Observação
                    </button>
                </div>
            `;
        }
    } catch (error) {
        // Sem observação ainda
        const podeAdicionar = ['agendada', 'confirmada', 'realizada'].includes(consulta.status);
        if (podeAdicionar) {
            observacaoHtml = `
                <div style="border-top: 2px solid #eee; margin-top: 20px; padding-top: 15px;">
                    <button onclick="abrirModalObservacao(${consultaId})" class="btn btn-primary" style="width: 100%; padding: 12px;">
                        <i class="fas fa-plus-circle"></i> Adicionar Observação Médica
                    </button>
                </div>
            `;
        }
    }
    
    // Criar modal
    const modal = document.createElement('div');
    modal.id = 'modalDetalhes';
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
        
        ${observacaoHtml}
        
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

// Abrir modal de observação
function abrirModalObservacao(consultaId) {
    fecharDetalhes();
    
    const modalHtml = `
        <div class="modal-overlay" onclick="fecharModalObservacao()">
            <div class="modal-content" onclick="event.stopPropagation()" style="max-width: 600px;">
                <div class="modal-header">
                    <h3>Adicionar Observação</h3>
                    <button onclick="fecharModalObservacao()" class="btn-close">&times;</button>
                </div>
                <form id="formObservacao" onsubmit="salvarObservacao(event, ${consultaId})">
                    <div class="modal-body">
                        <div class="form-group">
                            <label for="descricaoObservacao">Observações / Diagnóstico</label>
                            <textarea id="descricaoObservacao" required rows="6" 
                                placeholder="Registre suas observações sobre a consulta (visível apenas para você e administração)"
                            ></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" onclick="fecharModalObservacao()" class="btn btn-outline">Cancelar</button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Salvar Observação
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// Salvar observação
async function salvarObservacao(event, consultaId) {
    event.preventDefault();
    
    const descricao = document.getElementById('descricaoObservacao').value.trim();
    
    if (!descricao) {
        showMessage('Por favor, preencha a observação', 'error');
        return;
    }
    
    try {
        await api.post(API_CONFIG.ENDPOINTS.MEDICO_OBSERVACAO_CRIAR(medicoId, consultaId), {
            descricao: descricao
        });
        
        showMessage('Observação salva com sucesso!', 'success');
        fecharModalObservacao();
        await carregarConsultas();
    } catch (error) {
        console.error('Erro ao salvar observação:', error);
        showMessage('Erro ao salvar observação: ' + error.message, 'error');
    }
}

// Fechar modais
function fecharDetalhes() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}

function fecharModalObservacao() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}

// Filtrar consultas
function filtrarConsultas() {
    const dataInicio = document.getElementById('dataInicio')?.value;
    const dataFim = document.getElementById('dataFim')?.value;
    
    let consultasFiltradas = [...todasConsultas];
    
    if (dataInicio) {
        consultasFiltradas = consultasFiltradas.filter(c => {
            const dataConsulta = new Date(c.data_hora_inicio).toISOString().split('T')[0];
            return dataConsulta >= dataInicio;
        });
    }
    
    if (dataFim) {
        consultasFiltradas = consultasFiltradas.filter(c => {
            const dataConsulta = new Date(c.data_hora_inicio).toISOString().split('T')[0];
            return dataConsulta <= dataFim;
        });
    }
    
    renderizarConsultas(consultasFiltradas);
}

// Limpar filtro
function limparFiltro() {
    document.getElementById('dataInicio').value = '';
    document.getElementById('dataFim').value = '';
    renderizarConsultas(todasConsultas);
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

// Abrir modal para adicionar/editar observação
function abrirModalObservacao(consultaId, observacaoId = null) {
    // Fechar modal de detalhes se estiver aberto
    const modalDetalhes = document.getElementById('modalDetalhes');
    if (modalDetalhes) modalDetalhes.remove();
    
    const consulta = todasConsultas.find(c => c.id_consulta === consultaId);
    if (!consulta) {
        showMessage('Consulta não encontrada', 'error');
        return;
    }
    
    const isEdicao = observacaoId !== null;
    const titulo = isEdicao ? 'Editar Observação Médica' : 'Adicionar Observação Médica';
    
    const modal = document.createElement('div');
    modal.id = 'modalObservacao';
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
        z-index: 10001;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 10px;
        max-width: 700px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    `;
    
    modalContent.innerHTML = `
        <h3 style="color: var(--primary-color); margin-top: 0; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-notes-medical"></i> ${titulo}
        </h3>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid var(--primary-color);">
            <div style="font-size: 14px;">
                <strong>Paciente:</strong> ${consulta.paciente?.nome}<br>
                <strong>Data:</strong> ${new Date(consulta.data_hora_inicio).toLocaleDateString('pt-BR')}
            </div>
        </div>
        
        <form id="formObservacao">
            <div class="form-group">
                <label for="descricaoObservacao" style="display: block; margin-bottom: 8px; font-weight: bold; color: #333;">
                    <i class="fas fa-file-medical-alt"></i> Observação / Diagnóstico / Prescrição
                </label>
                <textarea 
                    id="descricaoObservacao" 
                    rows="10" 
                    required
                    placeholder="Registre aqui o diagnóstico, prescrição médica, recomendações e observações sobre a consulta...&#10;&#10;Esta informação é visível apenas para você e a administração da clínica."
                    style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-family: inherit; font-size: 14px; resize: vertical; min-height: 200px;"
                ></textarea>
                <small style="color: #666; display: block; margin-top: 5px;">
                    <i class="fas fa-info-circle"></i> Mínimo 10 caracteres
                </small>
            </div>
            
            <div style="margin-top: 25px; text-align: right; display: flex; gap: 10px; justify-content: flex-end;">
                <button type="button" id="btnCancelar" class="btn btn-outline" style="padding: 10px 25px;">
                    Cancelar
                </button>
                <button type="submit" class="btn btn-primary" style="padding: 10px 25px;">
                    <i class="fas fa-save"></i> ${isEdicao ? 'Atualizar' : 'Salvar'}
                </button>
            </div>
        </form>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Se for edição, buscar observação existente
    if (isEdicao) {
        carregarObservacaoParaEdicao(consultaId, observacaoId);
    }
    
    // Event listeners
    document.getElementById('btnCancelar').addEventListener('click', () => modal.remove());
    document.getElementById('formObservacao').addEventListener('submit', (e) => {
        e.preventDefault();
        salvarObservacao(consultaId, observacaoId);
    });
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

// Carregar observação para edição
async function carregarObservacaoParaEdicao(consultaId, observacaoId) {
    try {
        const observacao = await api.get(`/medicos/observacoes/${consultaId}?medico_id=${medicoId}`);
        if (observacao && observacao.descricao) {
            document.getElementById('descricaoObservacao').value = observacao.descricao;
        }
    } catch (error) {
        console.error('Erro ao carregar observação:', error);
    }
}

// Salvar observação
async function salvarObservacao(consultaId, observacaoId = null) {
    const descricao = document.getElementById('descricaoObservacao').value.trim();
    
    if (descricao.length < 10) {
        showMessage('A observação deve ter no mínimo 10 caracteres', 'error');
        return;
    }
    
    try {
        showLoading();
        
        if (observacaoId) {
            // Atualizar observação existente
            await api.put(`/medicos/observacoes/${observacaoId}?medico_id=${medicoId}`, {
                descricao: descricao
            });
            showMessage('Observação atualizada com sucesso!', 'success');
        } else {
            // Criar nova observação
            await api.post(`/medicos/observacoes?medico_id=${medicoId}`, {
                id_consulta_fk: consultaId,
                descricao: descricao
            });
            showMessage('Observação registrada com sucesso!', 'success');
        }
        
        // Fechar modal
        const modal = document.getElementById('modalObservacao');
        if (modal) modal.remove();
        
        hideLoading();
        
        // Recarregar consultas
        await carregarConsultas();
        
    } catch (error) {
        console.error('Erro ao salvar observação:', error);
        showMessage(error.message || 'Erro ao salvar observação', 'error');
        hideLoading();
    }
}

// Editar observação (atalho para abrir modal de edição)
function editarObservacao(consultaId, observacaoId) {
    // Fechar modal de detalhes
    const modalDetalhes = document.getElementById('modalDetalhes');
    if (modalDetalhes) modalDetalhes.remove();
    
    // Abrir modal de edição
    abrirModalObservacao(consultaId, observacaoId);
}
