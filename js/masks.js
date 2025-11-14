// Máscaras para campos de formulário

// Máscara de CPF (000.000.000-00)
function maskCPF(value) {
    return value
        .replace(/\D/g, '') // Remove tudo que não é dígito
        .slice(0, 11) // Limita a 11 dígitos
        .replace(/(\d{3})(\d)/, '$1.$2') // Coloca um ponto após os primeiros 3 dígitos
        .replace(/(\d{3})(\d)/, '$1.$2') // Coloca um ponto após os próximos 3 dígitos
        .replace(/(\d{3})(\d{1,2})$/, '$1-$2'); // Coloca um hífen antes dos últimos 2 dígitos
}

// Máscara de Telefone ((00) 00000-0000)
function maskPhone(value) {
    value = value.replace(/\D/g, ''); // Remove tudo que não é dígito
    
    if (value.length <= 10) {
        // Formato: (00) 0000-0000
        return value
            .replace(/(\d{2})(\d)/, '($1) $2')
            .replace(/(\d{4})(\d)/, '$1-$2');
    } else {
        // Formato: (00) 00000-0000
        return value
            .replace(/(\d{2})(\d)/, '($1) $2')
            .replace(/(\d{5})(\d)/, '$1-$2')
            .slice(0, 15); // Limita o tamanho
    }
}

// Máscara de CEP (00000-000)
function maskCEP(value) {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{5})(\d)/, '$1-$2')
        .slice(0, 9);
}

// Máscara de Data (DD/MM/AAAA)
function maskDate(value) {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{2})(\d)/, '$1/$2')
        .replace(/(\d{2})(\d)/, '$1/$2')
        .slice(0, 10);
}

// Máscara de CRM (00000-UF)
function maskCRM(value) {
    return value
        .replace(/[^\d\w]/g, '') // Remove caracteres especiais
        .replace(/(\d{5})([A-Za-z])/, '$1-$2')
        .toUpperCase()
        .slice(0, 8);
}

// Máscara de Carteirinha de Convênio (apenas números e letras)
function maskCarteirinha(value) {
    return value
        .replace(/[^\dA-Za-z]/g, '')
        .toUpperCase()
        .slice(0, 20);
}

// Remove a máscara (deixa apenas números)
function removeMask(value) {
    return value.replace(/\D/g, '');
}

// Aplica máscaras automaticamente nos inputs
function applyMasks() {
    // CPF
    document.querySelectorAll('input[id*="cpf"], input[name*="cpf"]').forEach(input => {
        input.addEventListener('input', function(e) {
            e.target.value = maskCPF(e.target.value);
        });
    });

    // Telefone
    document.querySelectorAll('input[id*="telefone"], input[name*="telefone"], input[type="tel"]').forEach(input => {
        input.addEventListener('input', function(e) {
            e.target.value = maskPhone(e.target.value);
        });
    });

    // CEP
    document.querySelectorAll('input[id*="cep"], input[name*="cep"]').forEach(input => {
        input.addEventListener('input', function(e) {
            e.target.value = maskCEP(e.target.value);
        });
    });

    // Data
    document.querySelectorAll('input[id*="data"], input[name*="data"], input[type="date"]').forEach(input => {
        // Para campos tipo date, não aplicar máscara (navegador já gerencia)
        if (input.type !== 'date') {
            input.addEventListener('input', function(e) {
                e.target.value = maskDate(e.target.value);
            });
        }
    });

    // CRM
    document.querySelectorAll('input[id*="crm"], input[name*="crm"]').forEach(input => {
        input.addEventListener('input', function(e) {
            e.target.value = maskCRM(e.target.value);
        });
    });

    // Carteirinha
    document.querySelectorAll('input[id*="carteirinha"], input[name*="carteirinha"]').forEach(input => {
        input.addEventListener('input', function(e) {
            e.target.value = maskCarteirinha(e.target.value);
        });
    });
}

// Aplica as máscaras quando o DOM estiver carregado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyMasks);
} else {
    applyMasks();
}

// Função para mostrar mensagens de feedback
function showMessage(message, type = 'info') {
    // Remove mensagem anterior se existir
    const existingMsg = document.querySelector('.alert-message');
    if (existingMsg) {
        existingMsg.remove();
    }

    // Cria nova mensagem
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert-message alert-${type}`;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
    `;

    // Define cores e ícones baseado no tipo
    const styles = {
        success: {
            bg: '#d4edda',
            border: '#c3e6cb',
            color: '#155724',
            icon: '✓'
        },
        error: {
            bg: '#f8d7da',
            border: '#f5c6cb',
            color: '#721c24',
            icon: '✕'
        },
        warning: {
            bg: '#fff3cd',
            border: '#ffeaa7',
            color: '#856404',
            icon: '⚠'
        },
        info: {
            bg: '#d1ecf1',
            border: '#bee5eb',
            color: '#0c5460',
            icon: 'ℹ'
        }
    };

    const style = styles[type] || styles.info;
    messageDiv.style.backgroundColor = style.bg;
    messageDiv.style.border = `1px solid ${style.border}`;
    messageDiv.style.color = style.color;

    messageDiv.innerHTML = `
        <span style="font-weight: bold; font-size: 18px;">${style.icon}</span>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="
            margin-left: auto;
            background: none;
            border: none;
            color: inherit;
            cursor: pointer;
            font-size: 20px;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        ">×</button>
    `;

    document.body.appendChild(messageDiv);

    // Remove automaticamente após 5 segundos
    setTimeout(() => {
        if (messageDiv.parentElement) {
            messageDiv.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => messageDiv.remove(), 300);
        }
    }, 5000);
}

// Adiciona animações CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
