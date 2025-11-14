# Guia de Correção dos Testes Pendentes
**Data:** 26/10/2025  
**Status Atual:** 55/83 testes passando (66%)  
**Meta:** 80/83 testes passando (>96%)

## 📊 Resumo dos Problemas

### Por Tipo de Erro
- **404 Not Found**: 8 testes - Rotas não implementadas
- **422 Unprocessable**: 7 testes - Schema validation
- **405 Method Not Allowed**: 3 testes - Método HTTP incorreto
- **TypeError**: 5 testes - Campos do modelo
- **AttributeError**: 4 testes - Acesso a campos None

## 🔧 Correções por Arquivo

### 1. test_endpoints_pacientes.py (8 testes falhando)

#### Problema 1: POST /pacientes/ retorna 404
```python
# Teste que falha
def test_criar_paciente(client, convenio):
    response = client.post("/pacientes/", json=dados)
    assert response.status_code == 201  # Retorna 404
```

**Solução**: Implementar rota em `app/routers/pacientes.py`
```python
@router.post("/", response_model=PacienteResponse, status_code=201)
def criar_paciente(
    paciente_data: PacienteCreate,
    db: Session = Depends(get_db)
):
    # Verificar CPF duplicado
    if db.query(Paciente).filter(Paciente.cpf == paciente_data.cpf).first():
        raise HTTPException(400, "CPF já cadastrado")
    
    # Criar usuário
    usuario = Usuario(
        email=paciente_data.email,
        nome=paciente_data.nome,
        tipo=TipoUsuario.PACIENTE
    )
    usuario.senha_hash = get_password_hash(paciente_data.senha)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    
    # Criar paciente
    paciente = Paciente(
        usuario_id=usuario.id,
        cpf=paciente_data.cpf,
        data_nascimento=paciente_data.data_nascimento,
        telefone=paciente_data.telefone,
        convenio_id=paciente_data.convenio_id,
        numero_carteirinha=paciente_data.numero_carteirinha
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    
    return paciente
```

#### Problema 2: Cancelamento retorna 422
```python
# Teste que falha
response = client.delete(
    f"/pacientes/consultas/{consulta.id}",
    headers={"Authorization": f"Bearer {token_paciente}"}
)
```

**Causa**: Rota espera formato diferente ou campo faltando

**Solução**: Verificar assinatura da rota
```python
# Verificar em app/routers/pacientes.py
@router.delete("/consultas/{consulta_id}")
def cancelar_consulta(
    consulta_id: int,  # Certifique-se que é int, não str
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ...
```

#### Problema 3: Buscar médicos retorna 404
```python
response = client.get(f"/pacientes/medicos?especialidade_id={especialidade.id}")
```

**Solução**: Implementar rota em `app/routers/pacientes.py`
```python
@router.get("/medicos", response_model=List[MedicoResponse])
def buscar_medicos(
    especialidade_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Medico)
    if especialidade_id:
        query = query.filter(Medico.especialidade_id == especialidade_id)
    return query.all()

@router.get("/medicos/{medico_id}/horarios", response_model=List[HorarioResponse])
def listar_horarios(medico_id: int, db: Session = Depends(get_db)):
    return db.query(HorarioDisponivel).filter(
        HorarioDisponivel.medico_id == medico_id
    ).all()
```

### 2. test_endpoints_medicos.py (10 testes falhando)

#### Problema 1: TypeError com Observacao
```python
# Erro: 'observacao' is an invalid keyword argument
observacao = Observacao(
    consulta_id=consulta.id,
    observacao="Teste"
)
```

**Causa**: Campo do modelo tem nome diferente

**Solução**: Verificar models.py
```python
# Se o campo no modelo é 'texto' ao invés de 'observacao':
class Observacao(Base):
    __tablename__ = "observacoes"
    
    id = Column(Integer, primary_key=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id"), unique=True)
    texto = Column(Text)  # ← Campo correto
    prescricao = Column(Text)
    diagnostico = Column(String(255))
```

Então ajustar nos testes:
```python
observacao = Observacao(
    consulta_id=consulta.id,
    texto="Teste"  # ← Usar nome correto
)
```

#### Problema 2: Marcar consulta como realizada retorna 404
```python
response = client.patch(
    f"/medicos/consultas/{consulta.id}/realizar",
    headers={"Authorization": f"Bearer {token_medico}"}
)
```

**Solução**: Implementar rotas em `app/routers/medicos.py`
```python
@router.patch("/consultas/{consulta_id}/realizar")
def marcar_como_realizada(
    consulta_id: int,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta or consulta.medico_id != current_user.medico.id:
        raise HTTPException(404, "Consulta não encontrada")
    
    consulta.status = StatusConsulta.REALIZADA
    atualizar_faltas_consecutivas(db, consulta.paciente_id, compareceu=True)
    db.commit()
    return consulta

@router.patch("/consultas/{consulta_id}/faltou")
def marcar_como_faltou(
    consulta_id: int,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta or consulta.medico_id != current_user.medico.id:
        raise HTTPException(404, "Consulta não encontrada")
    
    consulta.status = StatusConsulta.FALTOU
    atualizar_faltas_consecutivas(db, consulta.paciente_id, compareceu=False)
    db.commit()
    return consulta
```

#### Problema 3: Atualizar perfil retorna 405
```python
response = client.put("/medicos/perfil", json=dados, headers=...)
```

**Causa**: Rota espera PATCH ao invés de PUT

**Solução**: Ajustar teste OU implementar ambos os métodos
```python
# Opção 1: Ajustar teste
response = client.patch("/medicos/perfil", json=dados, headers=...)

# Opção 2: Suportar ambos no router
@router.put("/perfil")
@router.patch("/perfil")
def atualizar_perfil_medico(...):
    # ...
```

### 3. test_admin_relatorios.py (8 testes falhando)

#### Problema 1: TypeError nos relatórios
```python
# Erro: Function.__init__() got an unexpected keyword argument
response = client.get(
    f"/admin/relatorios/consultas-por-medico?data_inicio={data_inicio}&data_fim={data_fim}",
    headers={"Authorization": f"Bearer {token_admin}"}
)
```

**Causa**: Problema na função de geração de relatório

**Solução**: Verificar assinatura em `app/utils/relatorios.py`
```python
def gerar_relatorio_consultas_por_medico(
    db: Session,
    data_inicio: date,
    data_fim: date,
    admin_id: int
) -> dict:
    # Certifique-se que todos os parâmetros estão sendo passados
    # e que não há argumentos extras
```

#### Problema 2: AttributeError com medico.especialidade
```python
# Erro: 'NoneType' object has no attribute 'id'
# Em relatorios.py: medico.especialidade.nome
```

**Solução**: Adicionar verificação de None
```python
# Antes
especialidade_nome = medico.especialidade.nome

# Depois
especialidade_nome = medico.especialidade.nome if medico.especialidade else "Sem especialidade"
```

#### Problema 3: Desbloquear paciente retorna 405
```python
response = client.patch(
    f"/admin/pacientes/{paciente.id}/desbloquear",
    headers={"Authorization": f"Bearer {token_admin}"}
)
```

**Causa**: Rota implementada com método diferente

**Solução**: Verificar rota em `app/routers/admin.py`
```python
# Se está implementado como POST, mudar para PATCH
@router.patch("/pacientes/{paciente_id}/desbloquear")  # ← Usar PATCH
def desbloquear_paciente(
    paciente_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(404, "Paciente não encontrado")
    
    paciente.usuario.bloqueado = False
    paciente.faltas_consecutivas = 0
    db.commit()
    return {"message": "Paciente desbloqueado com sucesso"}
```

#### Problema 4: Dashboard admin campos faltando
```python
# Teste espera: consultas_agendadas, consultas_realizadas
# API retorna: consultas_hoje, total_pacientes
```

**Solução**: Ajustar resposta em `app/routers/admin.py`
```python
@router.get("/dashboard")
def get_dashboard(
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_consultas = db.query(Consulta).count()
    consultas_agendadas = db.query(Consulta).filter(
        Consulta.status == StatusConsulta.AGENDADA
    ).count()
    consultas_realizadas = db.query(Consulta).filter(
        Consulta.status == StatusConsulta.REALIZADA
    ).count()
    total_pacientes = db.query(Paciente).count()
    total_medicos = db.query(Medico).count()
    
    return {
        "total_consultas": total_consultas,
        "consultas_agendadas": consultas_agendadas,  # ← Adicionar
        "consultas_realizadas": consultas_realizadas,  # ← Adicionar
        "total_pacientes": total_pacientes,
        "total_medicos": total_medicos
    }
```

## 🛠️ Checklist de Correções

### Alta Prioridade (Impacto em múltiplos testes)
- [ ] Implementar POST /pacientes/ (2 testes)
- [ ] Corrigir nome dos campos em Observacao (4 testes)
- [ ] Implementar PATCH /medicos/consultas/{id}/realizar (3 testes)
- [ ] Ajustar resposta dashboard admin (1 teste)

### Média Prioridade (Rotas faltantes)
- [ ] GET /pacientes/medicos (1 teste)
- [ ] GET /pacientes/medicos/{id}/horarios (1 teste)
- [ ] PUT/PATCH /medicos/perfil (1 teste)
- [ ] PATCH /admin/pacientes/{id}/desbloquear (1 teste)
- [ ] PATCH /admin/pacientes/{id}/bloquear (1 teste)

### Baixa Prioridade (Ajustes finos)
- [ ] Melhorar mensagens de erro (validação)
- [ ] Adicionar tratamento de None em relatórios (3 testes)
- [ ] Validar schemas de request/response (422 errors)

## 🧪 Como Testar Após Correções

```bash
# Testar arquivo específico
pytest tests/test_endpoints_pacientes.py -v

# Testar teste específico
pytest tests/test_endpoints_pacientes.py::test_criar_paciente -v

# Testar com mais detalhes
pytest tests/test_endpoints_pacientes.py -vv --tb=long

# Rodar todos e ver resumo
pytest tests/ -v --tb=short | grep -E "PASSED|FAILED"
```

## 📝 Template de Correção

Para cada teste falhando:

1. **Identificar o erro**
   ```bash
   pytest tests/test_X.py::test_Y -vv
   ```

2. **Localizar o código relacionado**
   - Ver traceback do erro
   - Abrir arquivo do router/model mencionado

3. **Fazer a correção**
   - Implementar rota faltante OU
   - Ajustar nome de campo OU
   - Mudar método HTTP OU
   - Adicionar validação

4. **Testar a correção**
   ```bash
   pytest tests/test_X.py::test_Y -v
   ```

5. **Commitar**
   ```bash
   git add .
   git commit -m "fix: corrige teste test_Y - implementa rota Z"
   ```

## ⏱️ Estimativa de Tempo

| Tarefa | Tempo | Prioridade |
|--------|-------|------------|
| Implementar rotas faltantes | 2h | Alta |
| Corrigir campos de modelo | 1h | Alta |
| Ajustar métodos HTTP | 30min | Média |
| Tratamento de None | 1h | Média |
| Validação de schemas | 1h | Baixa |
| **TOTAL** | **5.5h** | - |

## 🎯 Meta Final

Com essas correções, esperamos atingir:
- **Meta Mínima**: 70/83 testes (84%)
- **Meta Desejada**: 80/83 testes (96%)
- **Meta Ideal**: 83/83 testes (100%)

---

**Última Atualização:** 26/10/2025  
**Autor:** IA Assistant  
**Status:** 📋 Guia pronto para execução
