// Dashboard do Paciente
document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('paciente');
    
    await carregarDadosDashboard();
});

async function carregarDadosDashboard() {
    try {
        const pacienteId = api.getUserId();
        console.log('📊 Carregando dashboard para paciente ID:', pacienteId);
        
        if (!pacienteId) {
            throw new Error('ID do paciente não encontrado. Faça login novamente.');
        }
        
        // Carregar perfil do paciente
        console.log('📡 Buscando perfil...');
        const perfil = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_PERFIL(pacienteId));
        console.log('✅ Perfil carregado:', perfil);
        
        // Atualizar nome do usuário
        const userNameElement = document.getElementById('userName');
        if (userNameElement && perfil.nome) {
            userNameElement.textContent = perfil.nome.split(' ')[0]; // Primeiro nome
        }
        
        // Atualizar nome na navbar
        const nomeNavbar = document.querySelector('.nav-user span strong');
        if (nomeNavbar && perfil.nome) {
            nomeNavbar.textContent = perfil.nome.split(' ')[0];
        }
        
        // Carregar consultas
        console.log('📡 Buscando consultas...');
        const consultas = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_CONSULTAS_LISTAR(pacienteId));
        console.log('✅ Consultas carregadas:', consultas);
        
        // Renderizar próximas consultas
        renderizarProximasConsultas(consultas);
        
        // Renderizar resumo
        renderizarResumo(consultas, perfil);
        
        console.log('✅ Dashboard carregado com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao carregar dados do dashboard:', error);
        console.error('Detalhes do erro:', error.message, error.stack);
        
        // Mostrar mensagem específica baseada no erro
        let mensagem = 'Erro ao carregar dados. ';
        if (error.message) {
            mensagem += error.message;
        } else {
            mensagem += 'Tente recarregar a página.';
        }
        
        showMessage(mensagem, 'error');
        
        // Exibir mensagem nas tabelas também
        const tbody = document.getElementById('proximas-consultas-tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center" style="color: red;">Erro ao carregar consultas. Recarregue a página.</td></tr>';
        }
    }
}

function renderizarProximasConsultas(consultas) {
    const tbody = document.getElementById('proximas-consultas-tbody');
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    // Filtrar consultas futuras
    const consultasFuturas = consultas.filter(c => {
        const dataConsulta = new Date(c.data_hora_inicio || c.data_hora);
        return dataConsulta >= hoje && ['agendada', 'confirmada'].includes(c.status);
    }).slice(0, 3); // Mostrar apenas as próximas 3
    
    if (consultasFuturas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Nenhuma consulta agendada</td></tr>';
        return;
    }
    
    tbody.innerHTML = consultasFuturas.map(consulta => {
        const dataHora = consulta.data_hora_inicio || consulta.data_hora;
        return `
            <tr>
                <td data-label="Data/Hora">${formatDateTime(dataHora)}</td>
                <td data-label="Especialidade">${consulta.medico?.especialidade?.nome || 'N/A'}</td>
                <td data-label="Médico">${consulta.medico?.nome || 'N/A'}</td>
                <td data-label="Ações">
                    <a href="consultas.html" style="color: var(--secondary-color);">Ver detalhes</a>
                </td>
            </tr>
        `;
    }).join('');
}

function renderizarResumo(consultas, perfil) {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    // Contar consultas
    const realizadas = consultas.filter(c => c.status === 'realizada').length;
    const agendadas = consultas.filter(c => {
        const dataConsulta = new Date(c.data_hora_inicio || c.data_hora);
        return dataConsulta >= hoje && ['agendada', 'confirmada'].includes(c.status);
    }).length;
    
    // Última consulta realizada
    const ultimaRealizada = consultas
        .filter(c => c.status === 'realizada')
        .sort((a, b) => new Date(b.data_hora_inicio || b.data_hora) - new Date(a.data_hora_inicio || a.data_hora))[0];
    
    // Atualizar elementos
    document.getElementById('total-realizadas').textContent = realizadas;
    document.getElementById('total-agendadas').textContent = agendadas;
    document.getElementById('convenio-nome').textContent = perfil.plano_saude?.nome || 'Particular';
    
    if (ultimaRealizada) {
        const dataHora = ultimaRealizada.data_hora_inicio || ultimaRealizada.data_hora;
        document.getElementById('ultima-consulta').textContent = formatDate(dataHora);
        document.getElementById('ultima-especialidade').textContent = ultimaRealizada.medico?.especialidade?.nome || 'N/A';
    } else {
        document.getElementById('ultima-consulta').textContent = 'Nenhuma consulta realizada';
        document.getElementById('ultima-especialidade').textContent = '-';
    }
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

function formatDate(isoString) {
    const date = new Date(isoString);
    const dia = String(date.getDate()).padStart(2, '0');
    const mes = String(date.getMonth() + 1).padStart(2, '0');
    const ano = date.getFullYear();
    return `${dia}/${mes}/${ano}`;
}

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
