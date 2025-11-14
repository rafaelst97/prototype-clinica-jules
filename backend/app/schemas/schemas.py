"""
Schemas Pydantic para validação de entrada/saída da API
Atualizado para refletir o modelo de dados conforme MER_Estrutura.txt
"""
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, date, time
from typing import Optional, List
from enum import Enum

class StatusConsulta(str, Enum):
    AGENDADA = "agendada"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    REALIZADA = "realizada"
    FALTOU = "faltou"

# ============ Auth Schemas ============
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str  # 'paciente', 'medico', 'administrador'
    user_id: int

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class AlterarSenhaRequest(BaseModel):
    senha_atual: str
    senha_nova: str
    
    @validator('senha_nova')
    def validar_senha_alfanumerica(cls, v):
        """Valida senha alfanumérica de 8-20 caracteres"""
        if len(v) < 8 or len(v) > 20:
            raise ValueError('Senha deve ter entre 8 e 20 caracteres')
        
        tem_letra = any(c.isalpha() for c in v)
        tem_numero = any(c.isdigit() for c in v)
        
        if not (tem_letra and tem_numero):
            raise ValueError('Senha deve conter letras e números (alfanumérica)')
        
        return v

# ============ Especialidade Schemas ============
class EspecialidadeBase(BaseModel):
    nome: str

class EspecialidadeCreate(EspecialidadeBase):
    pass

class EspecialidadeResponse(EspecialidadeBase):
    id_especialidade: int
    
    class Config:
        from_attributes = True

# ============ PlanoSaude Schemas ============
class PlanoSaudeBase(BaseModel):
    nome: str
    cobertura_info: Optional[str] = None

class PlanoSaudeCreate(PlanoSaudeBase):
    pass

class PlanoSaudeUpdate(BaseModel):
    nome: Optional[str] = None
    cobertura_info: Optional[str] = None

class PlanoSaudeResponse(PlanoSaudeBase):
    id_plano_saude: int
    
    class Config:
        from_attributes = True

# ============ Administrador Schemas ============
class AdministradorBase(BaseModel):
    nome: str
    email: EmailStr
    papel: Optional[str] = None

class AdministradorCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    papel: Optional[str] = None
    
    @validator('senha')
    def validar_senha_alfanumerica(cls, v):
        """Valida senha alfanumérica de 8-20 caracteres"""
        if len(v) < 8 or len(v) > 20:
            raise ValueError('Senha deve ter entre 8 e 20 caracteres')
        
        tem_letra = any(c.isalpha() for c in v)
        tem_numero = any(c.isdigit() for c in v)
        
        if not (tem_letra and tem_numero):
            raise ValueError('Senha deve conter letras e números (alfanumérica)')
        
        return v

class AdministradorResponse(AdministradorBase):
    id_admin: int
    
    class Config:
        from_attributes = True

# ============ Medico Schemas ============
class MedicoBase(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    crm: str
    id_especialidade_fk: int

class MedicoCreate(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    senha: str
    crm: str
    telefone: Optional[str] = None
    id_especialidade_fk: int
    
    @validator('senha')
    def validar_senha_alfanumerica(cls, v):
        """Valida senha alfanumérica de 8-20 caracteres"""
        if len(v) < 8 or len(v) > 20:
            raise ValueError('Senha deve ter entre 8 e 20 caracteres')
        
        tem_letra = any(c.isalpha() for c in v)
        tem_numero = any(c.isdigit() for c in v)
        
        if not (tem_letra and tem_numero):
            raise ValueError('Senha deve conter letras e números (alfanumérica)')
        
        return v
    
    @validator('cpf')
    def validar_cpf_formato(cls, v):
        """Valida formato do CPF"""
        if v:
            cpf_limpo = v.replace('.', '').replace('-', '').replace(' ', '')
            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                raise ValueError('CPF deve conter 11 dígitos')
        return v

class MedicoUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    email: Optional[EmailStr] = None
    crm: Optional[str] = None
    telefone: Optional[str] = None
    senha: Optional[str] = None
    id_especialidade_fk: Optional[int] = None
    
    @validator('senha')
    def validar_senha_alfanumerica(cls, v):
        """Valida senha alfanumérica de 8-20 caracteres se fornecida"""
        if v is None:
            return v
        if len(v) < 8 or len(v) > 20:
            raise ValueError('Senha deve ter entre 8 e 20 caracteres')
        
        tem_letra = any(c.isalpha() for c in v)
        tem_numero = any(c.isdigit() for c in v)
        
        if not (tem_letra and tem_numero):
            raise ValueError('Senha deve conter letras e números')
        
        return v

class MedicoResponse(BaseModel):
    id_medico: int
    nome: str
    cpf: str
    email: str
    crm: str
    telefone: Optional[str] = None
    id_especialidade_fk: int
    especialidade: Optional[EspecialidadeResponse] = None
    
    class Config:
        from_attributes = True

# ============ Paciente Schemas ============
class PacienteBase(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    telefone: Optional[str] = None
    data_nascimento: date
    id_plano_saude_fk: Optional[int] = None

class PacienteCreate(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    senha: str
    telefone: Optional[str] = None
    data_nascimento: date
    id_plano_saude_fk: Optional[int] = None
    
    @validator('senha')
    def validar_senha_alfanumerica(cls, v):
        """Valida senha alfanumérica de 8-20 caracteres"""
        if len(v) < 8 or len(v) > 20:
            raise ValueError('Senha deve ter entre 8 e 20 caracteres')
        
        tem_letra = any(c.isalpha() for c in v)
        tem_numero = any(c.isdigit() for c in v)
        
        if not (tem_letra and tem_numero):
            raise ValueError('Senha deve conter letras e números (alfanumérica)')
        
        return v
    
    @validator('cpf')
    def validar_cpf_formato(cls, v):
        """Valida formato do CPF"""
        if v:
            cpf_limpo = v.replace('.', '').replace('-', '').replace(' ', '')
            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                raise ValueError('CPF deve conter 11 dígitos')
        return v

class PacienteUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    id_plano_saude_fk: Optional[int] = None

class PacienteAlterarSenha(BaseModel):
    senha_atual: str
    senha_nova: str

class PacienteResponse(BaseModel):
    id_paciente: int
    nome: str
    cpf: str
    email: str
    telefone: Optional[str] = None
    data_nascimento: date
    esta_bloqueado: bool
    id_plano_saude_fk: Optional[int] = None
    plano_saude: Optional[PlanoSaudeResponse] = None
    
    class Config:
        from_attributes = True

class PacienteAdminResponse(PacienteResponse):
    """Schema estendido para admin com estatísticas de consultas"""
    total_consultas: int = 0  # Total de consultas realizadas
    consultas_agendadas: int = 0  # Consultas futuras (status: agendada)
    
    class Config:
        from_attributes = True

# ============ HorarioTrabalho Schemas ============
class HorarioTrabalhoBase(BaseModel):
    dia_semana: int = Field(..., ge=0, le=6)
    hora_inicio: time
    hora_fim: time

class HorarioTrabalhoCreate(HorarioTrabalhoBase):
    id_medico_fk: Optional[int] = None  # Pode ser obtido do token JWT

class HorarioTrabalhoMultiplosCreate(BaseModel):
    horarios: List[HorarioTrabalhoBase]

class HorarioTrabalhoResponse(HorarioTrabalhoBase):
    id_horario: int
    id_medico_fk: int
    
    class Config:
        from_attributes = True

# ============ Consulta Schemas ============
class ConsultaBase(BaseModel):
    data_hora_inicio: datetime
    data_hora_fim: datetime
    id_paciente_fk: int
    id_medico_fk: int

class ConsultaCreate(BaseModel):
    data_hora: datetime
    id_medico: int
    tipo: str = "Consulta"

class ConsultaUpdate(BaseModel):
    nova_data_hora: datetime

class ConsultaCancelar(BaseModel):
    motivo_cancelamento: Optional[str] = None

class ConsultaReagendar(BaseModel):
    nova_data_hora_inicio: datetime

class ConsultaResponse(BaseModel):
    id_consulta: int
    data_hora_inicio: datetime
    data_hora_fim: Optional[datetime] = None
    status: str
    id_paciente_fk: int
    id_medico_fk: int
    medico: Optional['MedicoResponse'] = None
    paciente: Optional['PacienteResponse'] = None
    
    class Config:
        from_attributes = True

# ============ Observacao Schemas ============
class ObservacaoBase(BaseModel):
    descricao: str

class ObservacaoCreate(ObservacaoBase):
    id_consulta_fk: int

class ObservacaoUpdate(ObservacaoBase):
    pass

class ObservacaoResponse(ObservacaoBase):
    id_observacao: int
    id_consulta_fk: int
    data_criacao: datetime
    
    class Config:
        from_attributes = True

# ============ Relatorio Schemas ============
class RelatorioBase(BaseModel):
    tipo: str

class RelatorioCreate(RelatorioBase):
    pass

class RelatorioResponse(RelatorioBase):
    id_relatorio: int
    data_geracao: datetime
    dados_resultado: Optional[str] = None
    id_admin_fk: int
    
    class Config:
        from_attributes = True

# ============ Schemas para Relatórios Específicos ============
class RelatorioConsultasPorMedico(BaseModel):
    medico_nome: str
    especialidade: str
    total_consultas: int
    consultas_realizadas: int
    consultas_canceladas: int

class RelatorioConsultasPorEspecialidade(BaseModel):
    especialidade: str
    total_consultas: int
    total_medicos: int

class RelatorioCancelamentos(BaseModel):
    total_consultas: int
    total_cancelamentos: int
    taxa_cancelamento: float

class RelatorioPacientesFrequentes(BaseModel):
    paciente_nome: str
    cpf: str
    total_consultas: int
    ultima_consulta: Optional[datetime] = None

class EstatisticasDashboard(BaseModel):
    total_pacientes: int
    total_medicos: int
    total_consultas: int
    consultas_hoje: int
    consultas_semana: int
    consultas_mes: int
    consultas_agendadas: int
    consultas_realizadas: int

# ============ Bloqueio Horario Schemas ============
class BloqueioHorarioBase(BaseModel):
    data: date
    hora_inicio: time
    hora_fim: time
    motivo: Optional[str] = None

class BloqueioHorarioCreate(BloqueioHorarioBase):
    pass

class BloqueioHorarioResponse(BloqueioHorarioBase):
    id_bloqueio: int
    id_medico_fk: int
    
    class Config:
        from_attributes = True

# ============ Schemas Auxiliares ============
class HorariosDisponiveisResponse(BaseModel):
    data: date
    horarios_disponiveis: List[str]

class MensagemResponse(BaseModel):
    mensagem: str

# Resolver referências forward (circular references)
ConsultaResponse.model_rebuild()
MedicoResponse.model_rebuild()
PacienteResponse.model_rebuild()
