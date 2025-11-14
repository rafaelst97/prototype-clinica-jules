// Gerenciamento de Horários do Médico - Integrado com API
let medicoId = null;
let horariosAtuais = [];
let bloqueiosAtuais = [];

document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('medico');
    
    medicoId = api.getUserId();
    
    // Carregar dados do médico na navbar
    await carregarDadosMedico();
    
    // Carregar horários existentes
    await carregarHorarios();
    
    // Carregar bloqueios existentes
    await carregarBloqueios();
    
    // Configurar data mínima para bloqueio (hoje)
    const inputData = document.getElementById('data-bloqueio');
    if (inputData) {
        const hoje = new Date().toISOString().split('T')[0];
        inputData.min = hoje;
        inputData.value = hoje;
    }
    
    // Se veio do dashboard com hash #bloqueio, rolar até a seção
    if (window.location.hash === '#bloqueio') {
        setTimeout(() => {
            const bloqueioCard = document.getElementById('bloqueio');
            if (bloqueioCard) {
                bloqueioCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Adicionar destaque temporário
                bloqueioCard.style.boxShadow = '0 0 20px rgba(231, 76, 60, 0.3)';
                setTimeout(() => {
                    bloqueioCard.style.boxShadow = '';
                }, 2000);
            }
        }, 300);
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

// Carregar horários do médico
async function carregarHorarios() {
    try {
        const horarios = await api.get(`/medicos/horarios/${medicoId}`);
        horariosAtuais = horarios;
        
        // Preencher checkboxes e inputs com horários existentes
        preencherFormularioComHorarios(horarios);
    } catch (error) {
        console.error('Erro ao carregar horários:', error);
        showMessage('Erro ao carregar horários.', 'error');
    }
}

function preencherFormularioComHorarios(horarios) {
    // Limpar todos os checkboxes primeiro
    const diasSemana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta'];
    diasSemana.forEach(dia => {
        const checkbox = document.getElementById(dia);
        if (checkbox) checkbox.checked = false;
    });
    
    // Agrupar horários por dia da semana
    const horariosPorDia = {};
    horarios.forEach(h => {
        if (!horariosPorDia[h.dia_semana]) {
            horariosPorDia[h.dia_semana] = [];
        }
        horariosPorDia[h.dia_semana].push(h);
    });
    
    // Preencher formulário
    diasSemana.forEach((dia, index) => {
        const diaSemana = index; // 0=Segunda (mas no banco é 0)
        const horariosDay = horariosPorDia[diaSemana] || [];
        
        if (horariosDay.length > 0) {
            const checkbox = document.getElementById(dia);
            if (checkbox) {
                checkbox.checked = true;
                
                const diaDiv = checkbox.closest('div').parentElement;
                const inputs = diaDiv.querySelectorAll('input[type="time"]');
                
                // Primeiro período (manhã geralmente)
                if (inputs[0] && horariosDay[0]) {
                    inputs[0].value = horariosDay[0].hora_inicio;
                }
                if (inputs[1] && horariosDay[0]) {
                    inputs[1].value = horariosDay[0].hora_fim;
                }
                
                // Segundo período (tarde)
                if (horariosDay.length > 1) {
                    if (inputs[2]) inputs[2].value = horariosDay[1].hora_inicio;
                    if (inputs[3]) inputs[3].value = horariosDay[1].hora_fim;
                }
            }
        }
    });
}

// Salvar horários do médico
document.getElementById('horariosForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    try {
        showLoading();
        
        // Coletar horários dos checkboxes marcados
        const diasSemana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta'];
        const horarios = [];
        
        diasSemana.forEach((dia, index) => {
            const checkbox = document.getElementById(dia);
            if (checkbox && checkbox.checked) {
                const diaDiv = checkbox.closest('div').parentElement;
                const inputs = diaDiv.querySelectorAll('input[type="time"]');
                
                // Primeiro período (manhã/período principal)
                if (inputs.length >= 2 && inputs[0].value && inputs[1].value) {
                    horarios.push({
                        dia_semana: index, // 0=Segunda, 1=Terça, etc
                        hora_inicio: inputs[0].value,
                        hora_fim: inputs[1].value
                    });
                }
                
                // Segundo período (tarde)
                if (inputs.length >= 4 && inputs[2].value && inputs[3].value) {
                    horarios.push({
                        dia_semana: index,
                        hora_inicio: inputs[2].value,
                        hora_fim: inputs[3].value
                    });
                }
            }
        });
        
        if (horarios.length === 0) {
            showMessage('Selecione pelo menos um dia da semana e configure os horários!', 'error');
            hideLoading();
            return;
        }
        
        console.log('Enviando horários:', { horarios });
        
        // Passo 1: Deletar todos os horários antigos primeiro
        if (horariosAtuais.length > 0) {
            await deletarTodosHorarios();
        }
        
        // Passo 2: Inserir os novos horários
        await api.post(`/medicos/horarios?medico_id=${medicoId}`, { horarios });
        
        showMessage('Horários salvos com sucesso!', 'success');
        hideLoading();
        
        // Recarregar horários
        await carregarHorarios();
        
    } catch (error) {
        console.error('Erro ao salvar horários:', error);
        showMessage(error.message || 'Erro ao salvar horários', 'error');
        hideLoading();
    }
});

// Deletar todos os horários do médico
async function deletarTodosHorarios() {
    try {
        // Deletar cada horário individualmente
        for (const horario of horariosAtuais) {
            await api.delete(`/medicos/horarios/${horario.id_horario}?medico_id=${medicoId}`);
        }
    } catch (error) {
        console.error('Erro ao deletar horários antigos:', error);
        throw new Error('Erro ao atualizar horários. Tente novamente.');
    }
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

// ============ Funções de Bloqueio de Horários ============

// Carregar bloqueios do médico
async function carregarBloqueios() {
    try {
        const hoje = new Date().toISOString().split('T')[0];
        const bloqueios = await api.get(`/medicos/bloqueios?medico_id=${medicoId}&data_inicio=${hoje}`);
        bloqueiosAtuais = bloqueios;
        
        renderizarBloqueios(bloqueios);
    } catch (error) {
        console.error('Erro ao carregar bloqueios:', error);
        const tbody = document.getElementById('lista-bloqueios');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">Erro ao carregar bloqueios</td></tr>';
        }
    }
}

function renderizarBloqueios(bloqueios) {
    const tbody = document.getElementById('lista-bloqueios');
    if (!tbody) return;
    
    if (bloqueios.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Nenhum bloqueio ativo</td></tr>';
        return;
    }
    
    tbody.innerHTML = bloqueios.map(bloqueio => {
        const dataFormatada = new Date(bloqueio.data + 'T00:00:00').toLocaleDateString('pt-BR');
        const periodo = `${bloqueio.hora_inicio.substring(0, 5)} - ${bloqueio.hora_fim.substring(0, 5)}`;
        const motivo = bloqueio.motivo || 'Não informado';
        
        return `
            <tr>
                <td>${dataFormatada}</td>
                <td>${periodo}</td>
                <td>${motivo}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="excluirBloqueio(${bloqueio.id_bloqueio})" title="Excluir bloqueio">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Formulário de bloqueio
document.getElementById('form-bloquear')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    try {
        const data = document.getElementById('data-bloqueio').value;
        const horaInicio = document.getElementById('hora-inicio-bloqueio').value;
        const horaFim = document.getElementById('hora-fim-bloqueio').value;
        const motivo = document.getElementById('motivo-bloqueio').value;
        
        // Validar hora_fim > hora_inicio
        if (horaFim <= horaInicio) {
            showMessage('Hora de fim deve ser posterior à hora de início', 'error');
            return;
        }
        
        showLoading();
        
        const bloqueioData = {
            data: data,
            hora_inicio: horaInicio,
            hora_fim: horaFim,
            motivo: motivo || null
        };
        
        await api.post(`/medicos/bloqueios?medico_id=${medicoId}`, bloqueioData);
        
        showMessage('Horário bloqueado com sucesso!', 'success');
        hideLoading();
        
        // Limpar formulário
        document.getElementById('form-bloquear').reset();
        const hoje = new Date().toISOString().split('T')[0];
        document.getElementById('data-bloqueio').value = hoje;
        
        // Recarregar bloqueios
        await carregarBloqueios();
        
    } catch (error) {
        console.error('Erro ao bloquear horário:', error);
        showMessage(error.message || 'Erro ao bloquear horário', 'error');
        hideLoading();
    }
});

// Excluir bloqueio
async function excluirBloqueio(bloqueioId) {
    if (!confirm('Deseja realmente excluir este bloqueio?')) {
        return;
    }
    
    try {
        showLoading();
        
        await api.delete(`/medicos/bloqueios/${bloqueioId}?medico_id=${medicoId}`);
        
        showMessage('Bloqueio excluído com sucesso!', 'success');
        hideLoading();
        
        // Recarregar bloqueios
        await carregarBloqueios();
        
    } catch (error) {
        console.error('Erro ao excluir bloqueio:', error);
        showMessage(error.message || 'Erro ao excluir bloqueio', 'error');
        hideLoading();
    }
}
