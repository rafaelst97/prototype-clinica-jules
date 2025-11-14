// js/utils.js

// Função auxiliar para exibir mensagens
function showMessage(message, type = 'success') {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    const alertContainer = document.createElement('div');
    alertContainer.style.position = 'fixed';
    alertContainer.style.top = '20px';
    alertContainer.style.right = '20px';
    alertContainer.style.zIndex = '1050';
    alertContainer.style.maxWidth = '350px';

    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert" style="animation: slideInRight 0.5s;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;

    alertContainer.innerHTML = alertHTML;
    document.body.appendChild(alertContainer);

    setTimeout(() => {
        alertContainer.style.animation = 'slideOutRight 0.5s forwards';
        setTimeout(() => alertContainer.remove(), 500);
    }, 4000);
}

// Função para formatar data
function formatDate(dateString) {
    if (!dateString) return '';
    try {
        const date = new Date(dateString);
        // Adiciona o fuso horário para corrigir a data
        const userTimezoneOffset = date.getTimezoneOffset() * 60000;
        return new Date(date.getTime() + userTimezoneOffset).toLocaleDateString('pt-BR');
    } catch (e) {
        console.error("Erro ao formatar data:", e);
        return dateString;
    }
}

// Função para formatar hora
function formatTime(timeString) {
    if (!timeString) return '';
    return timeString.substring(0, 5); // HH:MM
}

// Função para formatar data e hora juntas
function formatDateTime(dateTimeString) {
    if (!dateTimeString) return '';
    try {
        const date = new Date(dateTimeString);
        return `${date.toLocaleDateString('pt-BR')} ${date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
    } catch (e) {
        console.error("Erro ao formatar data e hora:", e);
        return dateTimeString;
    }
}

// Função para converter data e hora para formato ISO (data_hora_inicio/fim)
function toISODateTime(date, time) {
    if (!date || !time) return null;
    return `${date}T${time}:00`;
}

// Função para extrair data de datetime ISO
function extractDate(dateTimeString) {
    if (!dateTimeString) return '';
    return dateTimeString.split('T')[0];
}

// Função para extrair hora de datetime ISO
function extractTime(dateTimeString) {
    if (!dateTimeString) return '';
    const timePart = dateTimeString.split('T')[1];
    return timePart ? timePart.substring(0, 5) : '';
}

// Função para calcular hora fim (adiciona 30 minutos por padrão)
function calcularHoraFim(horaInicio, duracaoMinutos = 30) {
    if (!horaInicio) return '';
    const [hora, minuto] = horaInicio.split(':').map(Number);
    if (isNaN(hora) || isNaN(minuto)) return '';

    const totalMinutos = hora * 60 + minuto + duracaoMinutos;
    const novaHora = Math.floor(totalMinutos / 60) % 24;
    const novoMinuto = totalMinutos % 60;

    return `${String(novaHora).padStart(2, '0')}:${String(novoMinuto).padStart(2, '0')}`;
}

// Validação de CPF
function validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]+/g, '');
    if (cpf === '' || cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;

    let soma = 0, resto;
    for (let i = 1; i <= 9; i++) soma += parseInt(cpf.substring(i - 1, i)) * (11 - i);
    resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(cpf.substring(9, 10))) return false;

    soma = 0;
    for (let i = 1; i <= 10; i++) soma += parseInt(cpf.substring(i - 1, i)) * (12 - i);
    resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;

    return resto === parseInt(cpf.substring(10, 11));
}

// Exibir/ocultar senha
function togglePasswordVisibility(inputId, iconElement) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        iconElement.classList.remove('fa-eye');
        iconElement.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        iconElement.classList.remove('fa-eye-slash');
        iconElement.classList.add('fa-eye');
    }
}

// Debounce para evitar múltiplas submissões
function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Capitalizar primeira letra
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}
