// Consultas do Paciente - Integrado com API
let consultaAtual = null;
let consultas = [];

document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('paciente');
    
    await carregarNomePaciente();
    await carregarConsultas();
    configurarModalStyle();
});

async function carregarConsultas() {
    try {
        const pacienteId = api.getUserId();
        console.log('🔄 Carregando consultas do paciente:', pacienteId);
        
        const response = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_CONSULTAS_LISTAR(pacienteId));
        consultas = response;
        
        console.log('✅ Consultas carregadas:', consultas);
        
        renderizarConsultasFuturas();
        renderizarHistorico();
    } catch (error) {
        console.error('❌ Erro ao carregar consultas:', error);
        showMessage('Erro ao carregar consultas. Tente novamente.', 'error');
        
        // Mostrar mensagem de erro nas tabelas
        document.querySelector('.card:first-of-type tbody').innerHTML = 
            '<tr><td colspan="5" class="text-center" style="color: red;">Erro ao carregar consultas. Recarregue a página.</td></tr>';
        document.querySelector('.card:nth-of-type(2) tbody').innerHTML = 
            '<tr><td colspan="4" class="text-center" style="color: red;">Erro ao carregar histórico. Recarregue a página.</td></tr>';
    }
}

function renderizarConsultasFuturas() {
    const tbody = document.querySelector('.card:first-of-type tbody');
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    const consultasFuturas = consultas.filter(c => {
        const dataConsulta = new Date(c.data_hora_inicio || c.data_hora);
        return dataConsulta >= hoje && ['agendada', 'confirmada'].includes(c.status);
    });
    
    if (consultasFuturas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhuma consulta futura agendada</td></tr>';
        return;
    }
    
    tbody.innerHTML = consultasFuturas.map(consulta => {
        // Suporta tanto 'id' quanto 'id_consulta'
        const consultaId = consulta.id_consulta || consulta.id;
        const dataHora = consulta.data_hora_inicio || consulta.data_hora;
        return `
            <tr>
                <td>${formatDateTime(dataHora)}</td>
                <td>${consulta.medico?.especialidade?.nome || 'N/A'}</td>
                <td>${consulta.medico?.nome || 'N/A'} - CRM ${consulta.medico?.crm || ''}</td>
                <td>${renderizarStatusBadge(consulta.status)}</td>
                <td>
                    <button class="btn btn-secondary" style="padding: 5px 10px; margin-right: 5px;" 
                            onclick="abrirModalReagendar(${consultaId})">Reagendar</button>
                    <button class="btn btn-tertiary" style="padding: 5px 10px;" 
                            onclick="abrirModalCancelar(${consultaId})">Cancelar</button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderizarHistorico() {
    const tbody = document.querySelector('.card:nth-of-type(2) tbody');
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    const consultasPassadas = consultas.filter(c => {
        const dataConsulta = new Date(c.data_hora_inicio || c.data_hora);
        return dataConsulta < hoje || ['cancelada', 'realizada', 'faltou'].includes(c.status);
    }).sort((a, b) => new Date(b.data_hora_inicio || b.data_hora) - new Date(a.data_hora_inicio || a.data_hora));
    
    if (consultasPassadas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Nenhuma consulta no histórico</td></tr>';
        return;
    }
    
    tbody.innerHTML = consultasPassadas.map(consulta => {
        const dataHora = consulta.data_hora_inicio || consulta.data_hora;
        return `
            <tr>
                <td>${formatDateTime(dataHora)}</td>
                <td>${consulta.medico?.especialidade?.nome || 'N/A'}</td>
                <td>${consulta.medico?.nome || 'N/A'} - CRM ${consulta.medico?.crm || ''}</td>
                <td>${renderizarStatusBadge(consulta.status)}</td>
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

function formatDateTime(isoString) {
    const date = new Date(isoString);
    const dia = String(date.getDate()).padStart(2, '0');
    const mes = String(date.getMonth() + 1).padStart(2, '0');
    const ano = date.getFullYear();
    const hora = String(date.getHours()).padStart(2, '0');
    const minuto = String(date.getMinutes()).padStart(2, '0');
    return `${dia}/${mes}/${ano} ${hora}:${minuto}`;
}

// ==================== REAGENDAMENTO ====================
async function abrirModalReagendar(consultaId) {
    console.log('📅 Abrindo modal de reagendamento para consulta ID:', consultaId);
    console.log('📋 Consultas disponíveis:', consultas);
    
    // Suportar tanto 'id' quanto 'id_consulta'
    consultaAtual = consultas.find(c => (c.id_consulta || c.id) === consultaId);
    
    if (!consultaAtual) {
        console.error('❌ Consulta não encontrada:', consultaId);
        console.error('IDs disponíveis:', consultas.map(c => c.id_consulta || c.id));
        showMessage('Erro: Consulta não encontrada', 'error');
        return;
    }
    
    console.log('✅ Consulta encontrada:', consultaAtual);
    
    // Suportar ambos os formatos de data
    const dataHoraConsulta = consultaAtual.data_hora_inicio || consultaAtual.data_hora;
    
    // Verificar se pode reagendar (RN1 - 24h)
    const dataConsulta = new Date(dataHoraConsulta);
    const agora = new Date();
    const diferencaHoras = (dataConsulta - agora) / (1000 * 60 * 60);
    
    if (diferencaHoras < 24) {
        showMessage('Não é possível reagendar consultas com menos de 24 horas de antecedência (RN1).', 'error');
        return;
    }
    
    // Preencher informações da consulta atual
    document.getElementById('detalhes-consulta-atual').innerHTML = `
        ${formatDateTime(dataHoraConsulta)}<br>
        ${consultaAtual.medico?.nome} - ${consultaAtual.medico?.especialidade?.nome}
    `;
    
    // Configurar data mínima (amanhã)
    const amanha = new Date();
    amanha.setDate(amanha.getDate() + 1);
    document.getElementById('nova-data').min = amanha.toISOString().split('T')[0];
    
    // PREENCHER formulário com dados atuais da consulta
    const dataAtualConsulta = new Date(dataHoraConsulta);
    const dataFormatada = dataAtualConsulta.toISOString().split('T')[0]; // YYYY-MM-DD
    const horaFormatada = String(dataAtualConsulta.getHours()).padStart(2, '0') + ':' + 
                          String(dataAtualConsulta.getMinutes()).padStart(2, '0'); // HH:MM
    
    // Preencher campo de data com a data atual da consulta
    document.getElementById('nova-data').value = dataFormatada;
    
    // Carregar horários disponíveis para a data atual e preencher o horário
    await carregarHorariosDisponiveisInicial(horaFormatada);
    
    // Limpar mensagem de erro
    document.getElementById('reagendar-error-message').style.display = 'none';
    
    // Mostrar modal
    document.getElementById('modal-reagendar').style.display = 'flex';
    
    // Configurar listener de mudança de data
    document.getElementById('nova-data').addEventListener('change', carregarHorariosDisponiveis);
}

// Função auxiliar para carregar horários e preencher com o horário atual
async function carregarHorariosDisponiveisInicial(horarioAtual) {
    const data = document.getElementById('nova-data').value;
    const selectHora = document.getElementById('nova-hora');
    
    if (!data || !consultaAtual) return;
    
    try {
        const response = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_HORARIOS_DISPONIVEIS(
            consultaAtual.id_medico_fk
        ) + `?data=${data}`);
        
        selectHora.innerHTML = '<option value="">Selecione um horário</option>';
        
        // Sempre adicionar o horário atual da consulta como primeira opção
        const optionAtual = document.createElement('option');
        optionAtual.value = horarioAtual;
        optionAtual.textContent = horarioAtual + ' (horário atual)';
        optionAtual.selected = true;
        selectHora.appendChild(optionAtual);
        
        // O backend retorna: { data: "...", horarios_disponiveis: ["09:00", "10:00", ...] }
        const horarios = response.horarios_disponiveis || [];
        
        if (horarios.length === 0) {
            return; // Pelo menos tem o horário atual
        }
        
        // Adicionar outros horários disponíveis
        horarios.forEach(horario => {
            // Evitar duplicar o horário atual
            if (horario !== horarioAtual) {
                const option = document.createElement('option');
                option.value = horario;
                option.textContent = horario;
                selectHora.appendChild(option);
            }
        });
    } catch (error) {
        console.error('Erro ao carregar horários:', error);
        // Mesmo com erro, manter o horário atual selecionado
        selectHora.innerHTML = `<option value="${horarioAtual}" selected>${horarioAtual} (horário atual)</option>`;
    }
}

async function carregarHorariosDisponiveis() {
    const data = document.getElementById('nova-data').value;
    const selectHora = document.getElementById('nova-hora');
    
    if (!data || !consultaAtual) return;
    
    try {
        const response = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_HORARIOS_DISPONIVEIS(
            consultaAtual.id_medico_fk
        ) + `?data=${data}`);
        
        selectHora.innerHTML = '<option value="">Selecione um horário</option>';
        
        // O backend retorna: { data: "...", horarios_disponiveis: ["09:00", "10:00", ...] }
        const horarios = response.horarios_disponiveis || [];
        
        if (horarios.length === 0) {
            selectHora.innerHTML = '<option value="">Nenhum horário disponível</option>';
            return;
        }
        
        horarios.forEach(horario => {
            const option = document.createElement('option');
            option.value = horario;
            option.textContent = horario;
            selectHora.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar horários:', error);
        selectHora.innerHTML = '<option value="">Erro ao carregar horários</option>';
    }
}

function fecharModalReagendar() {
    document.getElementById('modal-reagendar').style.display = 'none';
    consultaAtual = null;
}

document.getElementById('form-reagendar').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const novaData = document.getElementById('nova-data').value;
    const novaHora = document.getElementById('nova-hora').value;
    const motivo = document.getElementById('motivo-reagendamento').value;
    
    if (!novaData || !novaHora) {
        mostrarErroReagendar('Por favor, preencha data e horário');
        return;
    }
    
    try {
        // Criar data_hora_inicio no formato ISO
        const novaDataHoraInicio = `${novaData}T${novaHora}:00`;
        const pacienteId = api.getUserId();
        
        // Usar id_consulta ou id (suporte para ambos)
        const consultaId = consultaAtual.id_consulta || consultaAtual.id;
        
        // Incluir paciente_id como query parameter
        const url = `${API_CONFIG.ENDPOINTS.PACIENTE_CONSULTA_REAGENDAR(consultaId)}?paciente_id=${pacienteId}`;
        
        await api.put(url, {
            nova_data_hora_inicio: novaDataHoraInicio,
            motivo_reagendamento: motivo
        });
        
        fecharModalReagendar();
        showMessage('Consulta reagendada com sucesso!', 'success');
        await carregarConsultas();
    } catch (error) {
        console.error('Erro ao reagendar:', error);
        // Melhor tratamento de erros
        let mensagemErro = 'Erro ao reagendar consulta';
        
        if (error.response && error.response.detail) {
            mensagemErro = error.response.detail;
        } else if (error.message) {
            mensagemErro = error.message;
        }
        
        mostrarErroReagendar(mensagemErro);
    }
});

function mostrarErroReagendar(mensagem) {
    const errorDiv = document.getElementById('reagendar-error-message');
    
    // Se for um array de erros (validação do Pydantic)
    if (Array.isArray(mensagem)) {
        errorDiv.textContent = mensagem.map(err => err.msg || err).join(', ');
    } else if (typeof mensagem === 'object') {
        // Se for um objeto, tentar extrair mensagens
        errorDiv.textContent = JSON.stringify(mensagem);
    } else {
        errorDiv.textContent = mensagem;
    }
    
    errorDiv.style.display = 'block';
    
    // Esconder automaticamente após 5 segundos
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// ==================== CANCELAMENTO ====================
function abrirModalCancelar(consultaId) {
    console.log('🗑️ Abrindo modal de cancelamento para consulta ID:', consultaId);
    
    // Suportar tanto 'id' quanto 'id_consulta'
    consultaAtual = consultas.find(c => (c.id_consulta || c.id) === consultaId);
    
    if (!consultaAtual) {
        console.error('❌ Consulta não encontrada:', consultaId);
        showMessage('Erro: Consulta não encontrada', 'error');
        return;
    }
    
    const dataHoraConsulta = consultaAtual.data_hora_inicio || consultaAtual.data_hora;
    
    // Verificar se pode cancelar (RN1 - 24h)
    const dataConsulta = new Date(dataHoraConsulta);
    const agora = new Date();
    const diferencaHoras = (dataConsulta - agora) / (1000 * 60 * 60);
    
    if (diferencaHoras < 24) {
        showMessage('Não é possível cancelar consultas com menos de 24 horas de antecedência (RN1).', 'error');
        return;
    }
    
    // Preencher informações da consulta
    document.getElementById('detalhes-consulta-cancelar').innerHTML = `
        ${formatDateTime(dataHoraConsulta)}<br>
        ${consultaAtual.medico?.nome} - ${consultaAtual.medico?.especialidade?.nome}
    `;
    
    // Limpar formulário
    document.getElementById('form-cancelar').reset();
    document.getElementById('cancelar-error-message').style.display = 'none';
    
    // Mostrar modal
    document.getElementById('modal-cancelar').style.display = 'flex';
}

function fecharModalCancelar() {
    document.getElementById('modal-cancelar').style.display = 'none';
    consultaAtual = null;
}

document.getElementById('form-cancelar').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const motivo = document.getElementById('motivo-cancelamento').value;
    const pacienteId = api.getUserId();
    
    console.log('🗑️ Iniciando cancelamento:', {
        consultaId: consultaAtual.id_consulta,
        pacienteId,
        motivo
    });
    
    try {
        // Usar id_consulta ou id (suporte para ambos)
        const consultaId = consultaAtual.id_consulta || consultaAtual.id;
        
        // Incluir paciente_id como query parameter
        const url = `${API_CONFIG.ENDPOINTS.PACIENTE_CONSULTA_CANCELAR(consultaId)}?paciente_id=${pacienteId}`;
        
        console.log('📡 URL do cancelamento:', url);
        
        // Enviar dados diretamente (não dentro de "data")
        const resultado = await api.delete(url, {
            motivo_cancelamento: motivo || null
        });
        
        console.log('✅ Cancelamento bem-sucedido:', resultado);
        
        fecharModalCancelar();
        showMessage('Consulta cancelada com sucesso!', 'success');
        await carregarConsultas();
    } catch (error) {
        console.error('❌ Erro ao cancelar:', error);
        
        // Melhor tratamento de mensagens de erro
        let mensagemErro = 'Erro ao cancelar consulta';
        
        if (error.response && error.response.detail) {
            if (typeof error.response.detail === 'string') {
                mensagemErro = error.response.detail;
            } else if (Array.isArray(error.response.detail)) {
                mensagemErro = error.response.detail.map(err => err.msg || err).join(', ');
            }
        } else if (error.message) {
            mensagemErro = error.message;
        }
        
        mostrarErroCancelar(mensagemErro);
    }
});

function mostrarErroCancelar(mensagem) {
    const errorDiv = document.getElementById('cancelar-error-message');
    
    // Tratar arrays e objetos
    if (Array.isArray(mensagem)) {
        errorDiv.textContent = mensagem.map(err => err.msg || err).join(', ');
    } else if (typeof mensagem === 'object') {
        errorDiv.textContent = JSON.stringify(mensagem);
    } else {
        errorDiv.textContent = mensagem;
    }
    
    errorDiv.style.display = 'block';
    
    // Esconder automaticamente após 5 segundos
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Configurar estilo dos modais
function configurarModalStyle() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.background = 'rgba(0, 0, 0, 0.7)';
        modal.style.display = 'none';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.zIndex = '9999';
    });
    
    const modalContents = document.querySelectorAll('.modal-content');
    modalContents.forEach(content => {
        content.style.position = 'relative';
        content.style.background = 'white';
        content.style.borderRadius = '10px';
        content.style.padding = '30px';
        content.style.maxWidth = '600px';
        content.style.width = '90%';
        content.style.maxHeight = '90vh';
        content.style.overflowY = 'auto';
    });
    
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(btn => {
        btn.style.position = 'absolute';
        btn.style.top = '15px';
        btn.style.right = '20px';
        btn.style.fontSize = '28px';
        btn.style.fontWeight = 'bold';
        btn.style.color = '#999';
        btn.style.cursor = 'pointer';
        btn.style.lineHeight = '1';
    });
}

// Helper para exibir mensagens
function showMessage(message, type = 'success') {
    // Remove mensagens anteriores
    const existingAlert = document.querySelector('.alert-message');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    const alertHTML = `
        <div class="alert-message ${alertClass}" style="
            position: fixed; 
            top: 20px; 
            right: 20px; 
            z-index: 99999; 
            min-width: 300px;
            max-width: 500px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease-out;
        ">
            <strong>${type === 'success' ? '✅' : '❌'}</strong> ${message}
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHTML);
    
    setTimeout(() => {
        const alert = document.querySelector('.alert-message');
        if (alert) {
            alert.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => alert.remove(), 300);
        }
    }, 4000);
}

function calcularHoraFim(dataHoraInicio) {
    const inicio = new Date(dataHoraInicio);
    inicio.setMinutes(inicio.getMinutes() + 30); // Consulta padrão de 30 minutos
    return inicio.toISOString().slice(0, 19);
}

// Função para carregar nome do paciente na navbar
async function carregarNomePaciente() {
    try {
        const pacienteId = api.getUserId();
        const perfil = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_PERFIL(pacienteId));
        
        const nomeNavbar = document.querySelector('.nav-user span strong');
        if (nomeNavbar && perfil.nome) {
            // Pegar apenas o primeiro nome
            const primeiroNome = perfil.nome.split(' ')[0];
            nomeNavbar.textContent = primeiroNome;
        }
    } catch (error) {
        console.error('Erro ao carregar nome do paciente:', error);
    }
}
