# Guia de Contribuição - Clínica Saúde+

## 🤝 Como Contribuir

Obrigado por considerar contribuir com o projeto Clínica Saúde+! 

## 📋 Processo de Contribuição

### 1. Fork o Projeto

```bash
# Clone seu fork
git clone https://github.com/SEU_USUARIO/prototype-melhoria.git
cd prototype-melhoria

# Adicione o repositório original como upstream
git remote add upstream https://github.com/rafaelst97/prototype-melhoria.git
```

### 2. Crie uma Branch

```bash
# Atualize sua main
git checkout main
git pull upstream main

# Crie uma branch para sua feature/fix
git checkout -b feature/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

### 3. Faça suas Alterações

- Escreva código limpo e bem documentado
- Siga as convenções de código do projeto
- Adicione testes se aplicável
- Atualize a documentação se necessário

### 4. Commit suas Mudanças

Use mensagens de commit descritivas seguindo o padrão Conventional Commits:

```bash
git add .
git commit -m "feat: adiciona funcionalidade X"
# ou
git commit -m "fix: corrige bug Y"
# ou
git commit -m "docs: atualiza documentação Z"
```

#### Tipos de Commit

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, espaços em branco, etc
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Tarefas de manutenção

### 5. Push para seu Fork

```bash
git push origin feature/nome-da-feature
```

### 6. Abra um Pull Request

1. Vá para https://github.com/rafaelst97/prototype-melhoria
2. Clique em "Pull Requests" > "New Pull Request"
3. Selecione "compare across forks"
4. Selecione sua branch
5. Preencha o template do PR

## 🧪 Executando Testes

Antes de submeter seu PR, certifique-se de que todos os testes passam:

```bash
cd backend
python -m pytest tests/ -v
```

## 📝 Padrões de Código

### Python (Backend)

- Siga a PEP 8
- Use type hints
- Docstrings para funções e classes
- Máximo 100 caracteres por linha

```python
def criar_consulta(
    paciente_id: int,
    medico_id: int,
    data_hora: datetime
) -> Consulta:
    """
    Cria uma nova consulta no sistema.
    
    Args:
        paciente_id: ID do paciente
        medico_id: ID do médico
        data_hora: Data e hora da consulta
        
    Returns:
        Objeto Consulta criado
        
    Raises:
        HTTPException: Se houver conflito de horário
    """
    # implementação
```

### JavaScript (Frontend)

- Use ES6+
- Const/let ao invés de var
- Arrow functions quando apropriado
- Async/await para promises
- Comentários JSDoc para funções complexas

```javascript
/**
 * Carrega consultas do paciente
 * @param {number} pacienteId - ID do paciente
 * @returns {Promise<Array>} Lista de consultas
 */
async function carregarConsultas(pacienteId) {
    try {
        const consultas = await api.get(`/pacientes/${pacienteId}/consultas`);
        return consultas;
    } catch (error) {
        console.error('Erro ao carregar consultas:', error);
        throw error;
    }
}
```

### HTML/CSS

- Indentação de 4 espaços
- Classes semânticas
- Mobile-first
- Acessibilidade (ARIA labels quando necessário)

## 🐛 Reportando Bugs

Ao reportar um bug, inclua:

1. **Descrição clara** do problema
2. **Passos para reproduzir**
3. **Comportamento esperado** vs **comportamento atual**
4. **Screenshots** se aplicável
5. **Ambiente** (navegador, SO, versão do Docker)

Exemplo:

```markdown
## Descrição
O botão de salvar horários não funciona no módulo médico.

## Passos para Reproduzir
1. Faça login como médico
2. Vá em "Horários de Atendimento"
3. Marque segunda-feira
4. Clique em "Salvar Horários"

## Comportamento Esperado
Horários devem ser salvos e mensagem de sucesso exibida.

## Comportamento Atual
Nada acontece, nenhuma mensagem é exibida.

## Ambiente
- Navegador: Chrome 120
- SO: Windows 11
- Docker: 24.0.6
```

## 💡 Sugerindo Funcionalidades

Para sugerir novas funcionalidades:

1. Verifique se já não existe uma issue similar
2. Abra uma nova issue com tag `enhancement`
3. Descreva detalhadamente:
   - O problema que a feature resolve
   - Como deveria funcionar
   - Benefícios para o sistema
   - Mockups/wireframes se possível

## ✅ Checklist antes do PR

- [ ] Código está funcionando localmente
- [ ] Testes passam (`pytest tests/`)
- [ ] Sem erros no console do navegador
- [ ] Documentação atualizada
- [ ] Commits seguem padrão Conventional Commits
- [ ] Branch está atualizada com main
- [ ] PR tem descrição clara

## 🎯 Áreas que Precisam de Ajuda

- 📱 Melhorias de responsividade mobile
- ♿ Acessibilidade (WCAG 2.1)
- 🌐 Internacionalização (i18n)
- 🧪 Cobertura de testes
- 📚 Documentação
- 🎨 Melhorias de UI/UX

## 👥 Equipe Principal

- **CAIO CÉSAR SABINO SOARES**
- **JÚLIA CANSIAN ROCHA**
- **RAFAEL DOS SANTOS**

## 📞 Contato

- Issues: https://github.com/rafaelst97/prototype-melhoria/issues
- Email: [criar email do projeto se houver]

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a licença MIT.

---

**Obrigado por contribuir com o Clínica Saúde+! 🏥💙**
