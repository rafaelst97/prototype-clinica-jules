// Agendar Consulta - Integrado com API
document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('paciente');
    
    // Carregar nome do paciente na navbar
    await carregarNomePaciente();
    
    const especialidadeSelect = document.getElementById('especialidade');
    const medicoSelect = document.getElementById('medico');
    const dataInput = document.getElementById('data');
    const horarioSelect = document.getElementById('horario');
    
    // Carregar especialidades
    await carregarEspecialidades();
    
    // Quando selecionar especialidade, carregar médicos
    especialidadeSelect?.addEventListener('change', async function() {
        const especialidadeId = this.value;
        medicoSelect.disabled = !especialidadeId;
        medicoSelect.innerHTML = '<option value="">Selecione um médico</option>';
        dataInput.disabled = true;
        horarioSelect.disabled = true;
        
        if (especialidadeId) {
            await carregarMedicos(especialidadeId);
        }
    });
    
    // Quando selecionar médico, habilitar data
    medicoSelect?.addEventListener('change', function() {
        dataInput.disabled = !this.value;
        horarioSelect.disabled = true;
        horarioSelect.innerHTML = '<option value="">Selecione um horário</option>';
        
        if (this.value) {
            // Definir data mínima como amanhã
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            dataInput.min = tomorrow.toISOString().split('T')[0];
        }
    });
    
    // Quando selecionar data, carregar horários disponíveis
    dataInput?.addEventListener('change', async function() {
        const medicoId = medicoSelect.value;
        const data = this.value;
        
        if (medicoId && data) {
            await carregarHorariosDisponiveis(medicoId, data);
        }
    });
    
    // Submissão do formulário
    document.getElementById('agendarForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const medicoId = medicoSelect.value;
        const data = dataInput.value;
        const horario = horarioSelect.value;
        
        if (!medicoId || !data || !horario) {
            showMessage('Por favor, preencha todos os campos obrigatórios!', 'error');
            return;
        }
        
        await agendarConsulta(medicoId, data, horario);
    });
});

// Carregar especialidades
async function carregarEspecialidades() {
    try {
        const especialidades = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_ESPECIALIDADES);
        const especialidadeSelect = document.getElementById('especialidade');
        
        if (!especialidadeSelect) return;
        
        especialidadeSelect.innerHTML = '<option value="">Selecione uma especialidade</option>';
        
        especialidades.forEach(esp => {
            const option = document.createElement('option');
            option.value = esp.id_especialidade;
            option.textContent = esp.nome;
            especialidadeSelect.appendChild(option);
        });
        
        console.log(`✅ ${especialidades.length} especialidades carregadas`);
    } catch (error) {
        console.error('Erro ao carregar especialidades:', error);
        showMessage('Erro ao carregar especialidades', 'error');
    }
}

// Carregar médicos por especialidade
async function carregarMedicos(especialidadeId) {
    try {
        console.log(`📡 Buscando médicos para especialidade ID: ${especialidadeId}`);
        const medicos = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_MEDICOS, { especialidade_id: especialidadeId });
        console.log('📋 Resposta da API:', medicos);
        console.log('📋 Tipo:', typeof medicos, 'É array?', Array.isArray(medicos));
        
        const medicoSelect = document.getElementById('medico');
        
        if (!medicoSelect) {
            console.error('❌ Elemento #medico não encontrado!');
            return;
        }
        
        medicoSelect.innerHTML = '<option value="">Selecione um médico</option>';
        
        if (medicos && medicos.length > 0) {
            medicos.forEach(medico => {
                const option = document.createElement('option');
                option.value = medico.id_medico;
                option.textContent = `${medico.nome} - CRM ${medico.crm}`;
                medicoSelect.appendChild(option);
            });
            console.log(`✅ ${medicos.length} médicos carregados com sucesso`);
            medicoSelect.disabled = false;
        } else {
            console.warn('⚠️ Nenhum médico encontrado');
            medicoSelect.innerHTML = '<option value="">Nenhum médico disponível</option>';
            showMessage('Nenhum médico disponível para esta especialidade', 'warning');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar médicos:', error);
        const medicoSelect = document.getElementById('medico');
        if (medicoSelect) {
            medicoSelect.innerHTML = '<option value="">Erro ao carregar médicos</option>';
        }
        showMessage('Erro ao carregar médicos', 'error');
    }
}

// Carregar horários disponíveis
async function carregarHorariosDisponiveis(medicoId, data) {
    try {
        console.log(`📡 Buscando horários para médico ID: ${medicoId}, data: ${data}`);
        const response = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_HORARIOS_DISPONIVEIS(medicoId), { data });
        console.log('📋 Resposta horários:', response);
        
        const horarioSelect = document.getElementById('horario');
        
        if (!horarioSelect) return;
        
        horarioSelect.innerHTML = '<option value="">Selecione um horário</option>';
        horarioSelect.disabled = false;
        
        // O backend retorna: { data: "...", horarios_disponiveis: ["09:00", "10:00", ...] }
        const horarios = response.horarios_disponiveis || [];
        
        if (horarios && horarios.length > 0) {
            horarios.forEach(horario => {
                const option = document.createElement('option');
                option.value = horario;
                option.textContent = horario;
                horarioSelect.appendChild(option);
            });
            console.log(`✅ ${horarios.length} horários disponíveis carregados`);
        } else {
            console.warn('⚠️ Nenhum horário disponível para esta data');
            horarioSelect.innerHTML = '<option value="">Nenhum horário disponível</option>';
            showMessage('Nenhum horário disponível para esta data', 'warning');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar horários:', error);
        const horarioSelect = document.getElementById('horario');
        if (horarioSelect) {
            horarioSelect.innerHTML = '<option value="">Erro ao carregar horários</option>';
        }
        showMessage('Erro ao carregar horários disponíveis', 'error');
    }
}

// Agendar consulta
async function agendarConsulta(medicoId, data, horario) {
    const btnSubmit = document.querySelector('#agendarForm button[type="submit"]');
    const originalText = btnSubmit ? btnSubmit.innerHTML : '';
    
    try {
        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Agendando...';
        }
        
        const pacienteId = api.getUserId();
        
        // Criar data_hora no formato ISO (conforme schema ConsultaCreate)
        const dataHora = toISODateTime(data, horario);
        
        const dadosConsulta = {
            data_hora: dataHora,
            id_medico: parseInt(medicoId),
            tipo: "Consulta"
        };
        
        // Incluir paciente_id como query parameter
        const url = `${API_CONFIG.ENDPOINTS.PACIENTE_CONSULTAS}?paciente_id=${pacienteId}`;
        
        console.log('📤 Agendando consulta:', { url, dadosConsulta });
        await api.post(url, dadosConsulta);
        
        showMessage('Consulta agendada com sucesso!', 'success');
        
        setTimeout(() => {
            window.location.href = 'consultas.html';
        }, 2000);
        
    } catch (error) {
        console.error('❌ Erro ao agendar consulta:', error);
        
        // Melhor tratamento de mensagens de erro
        let mensagemErro = 'Erro ao agendar consulta';
        
        if (error.response && error.response.detail) {
            // Erro do backend (FastAPI)
            if (typeof error.response.detail === 'string') {
                mensagemErro = error.response.detail;
            } else if (Array.isArray(error.response.detail)) {
                // Erros de validação do Pydantic
                mensagemErro = error.response.detail.map(err => err.msg || err).join(', ');
            }
        } else if (error.message) {
            mensagemErro = error.message;
        }
        
        showMessage(mensagemErro, 'error');
        
        if (btnSubmit) {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = originalText;
        }
    }
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
