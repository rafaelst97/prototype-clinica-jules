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

# ============ Usuario Schemas ============
class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str

class UsuarioCreate(UsuarioBase):
    senha: str
    tipo: TipoUsuario
    
    @validator('senha')
    def validar_senha_alfanumerica(cls, v):
        """Valida senha alfanumérica de 8-20 caracteres conforme requisitos"""
        if len(v) < 8 or len(v) > 20:
            raise ValueError('Senha deve ter entre 8 e 20 caracteres')
        
        tem_letra = any(c.isalpha() for c in v)
        tem_numero = any(c.isdigit() for c in v)
        
        if not (tem_letra and tem_numero):
            raise ValueError('Senha deve conter letras e números (alfanumérica)')
        
        return v

class UsuarioResponse(UsuarioBase):
    id: int
    tipo: TipoUsuario
    ativo: bool
    bloqueado: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ============ Especialidade Schemas ============
class EspecialidadeBase(BaseModel):
    nome: str
    descricao: Optional[str] = None

class EspecialidadeCreate(EspecialidadeBase):
    pass

class EspecialidadeResponse(EspecialidadeBase):
    id: int
    ativo: bool
    
    class Config:
        from_attributes = True

# ============ Convenio Schemas ============
class ConvenioBase(BaseModel):
    nome: str
    codigo: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    descricao: Optional[str] = None

class ConvenioCreate(ConvenioBase):
    codigo: str  # Obrigatório na criação

class ConvenioUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class ConvenioResponse(ConvenioBase):
    id: int
    ativo: bool
    criado_em: datetime
    
    class Config:
        from_attributes = True

# ============ Paciente Schemas ============
class PacienteBase(BaseModel):
    cpf: str
    data_nascimento: date
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    convenio_id: Optional[int] = None
    numero_carteirinha: Optional[str] = None

class PacienteCreate(BaseModel):
    # Dados do usuário
    email: EmailStr
    senha: str
    nome: str
    # Dados do paciente
    cpf: str
    data_nascimento: date
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    convenio_id: Optional[int] = None
    numero_carteirinha: Optional[str] = None
    
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
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    convenio_id: Optional[int] = None
    numero_carteirinha: Optional[str] = None

class PacienteResponse(PacienteBase):
    id: int
    usuario_id: int
    usuario: UsuarioResponse
    convenio: Optional[ConvenioResponse] = None
    
    class Config:
        from_attributes = True

# ============ Medico Schemas ============
class MedicoBase(BaseModel):
    cpf: Optional[str] = None
    crm: str
    especialidade_id: int
    telefone: Optional[str] = None
    valor_consulta: Optional[float] = None
    tempo_consulta: int = 30

class MedicoCreate(BaseModel):
    # Dados do usuário
    email: EmailStr
    senha: str
    nome: str
    # Dados do médico
    cpf: str  # Obrigatório conforme MER
    crm: str
    especialidade_id: int
    telefone: Optional[str] = None
    valor_consulta: Optional[float] = None
    tempo_consulta: int = 30
    
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
    especialidade_id: Optional[int] = None
    telefone: Optional[str] = None
    valor_consulta: Optional[float] = None
    tempo_consulta: Optional[int] = None

class MedicoResponse(MedicoBase):
    id: int
    usuario_id: int
    usuario: UsuarioResponse
    especialidade: EspecialidadeResponse
    
    class Config:
        from_attributes = True

# ============ Horario Disponivel Schemas ============
class HorarioDisponivelBase(BaseModel):
    dia_semana: int = Field(..., ge=0, le=6)
    hora_inicio: time
    hora_fim: time

class HorarioDisponivelCreate(HorarioDisponivelBase):
    pass  # medico_id é obtido do token JWT, não enviado no body

class HorariosMultiplosCreate(BaseModel):
    horarios: List[HorarioDisponivelCreate]

class HorarioDisponivelResponse(HorarioDisponivelBase):
    id: int
    medico_id: int
    ativo: bool
    
    class Config:
        from_attributes = True

# ============ Bloqueio Horario Schemas ============
class BloqueioHorarioBase(BaseModel):
    data: date
    hora_inicio: time
    hora_fim: time
    motivo: Optional[str] = None

class BloqueioHorarioCreate(BloqueioHorarioBase):
    medico_id: int

class BloqueioHorarioResponse(BloqueioHorarioBase):
    id: int
    medico_id: int
    
    class Config:
        from_attributes = True

# ============ Consulta Schemas ============
class ConsultaBase(BaseModel):
    data: date
    hora: time
    motivo_consulta: Optional[str] = None

class ConsultaCreate(ConsultaBase):
    medico_id: int

class ConsultaUpdate(BaseModel):
    status: Optional[StatusConsulta] = None

class ConsultaCancelar(BaseModel):
    motivo_cancelamento: Optional[str] = None

class ConsultaReagendar(BaseModel):
    nova_data: date
    nova_hora: time
    motivo_reagendamento: Optional[str] = None

class ConsultaResponse(ConsultaBase):
    id: int
    paciente_id: int
    medico_id: int
    status: StatusConsulta
    criado_em: datetime
    cancelado_em: Optional[datetime] = None
    motivo_cancelamento: Optional[str] = None
    
    class Config:
        from_attributes = True

class ConsultaDetalhada(ConsultaResponse):
    paciente: PacienteResponse
    medico: MedicoResponse
    
    class Config:
        from_attributes = True

# ============ Observacao Schemas ============
class ObservacaoBase(BaseModel):
    descricao: str

class ObservacaoCreate(ObservacaoBase):
    consulta_id: int

class ObservacaoUpdate(ObservacaoBase):
    pass

class ObservacaoResponse(ObservacaoBase):
    id: int
    consulta_id: int
    data_criacao: datetime
    
    class Config:
        from_attributes = True

# ============ Admin Schemas ============
class AdminCreate(BaseModel):
    email: EmailStr
    senha: str
    nome: str
    cargo: Optional[str] = None

class AdminResponse(BaseModel):
    id: int
    usuario_id: int
    cargo: Optional[str] = None
    usuario: UsuarioResponse
    
    class Config:
        from_attributes = True

# ============ Relatorios Schemas ============
class RelatorioBase(BaseModel):
    tipo: str
    parametros: Optional[str] = None

class RelatorioCreate(RelatorioBase):
    pass

class RelatorioResponse(RelatorioBase):
    id: int
    admin_id: int
    data_geracao: datetime
    dados_resultado: Optional[str] = None
    arquivo_path: Optional[str] = None
    
    class Config:
        from_attributes = True

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
    total_remarcacoes: int

class RelatorioPacientesFrequentes(BaseModel):
    paciente_nome: str
    cpf: str
    total_consultas: int
    ultima_consulta: Optional[date] = None

class EstatisticasDashboard(BaseModel):
    total_pacientes: int
    total_medicos: int
    total_consultas: int
    consultas_hoje: int
    consultas_semana: int
    consultas_mes: int
    consultas_agendadas: int
    consultas_realizadas: int

class HorarioDisponivel(BaseModel):
    data: date
    horarios: List[str]
