from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Date, Time, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class StatusConsulta(str, enum.Enum):
    AGENDADA = "agendada"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    REALIZADA = "realizada"
    FALTOU = "faltou"

# ===== ENTIDADES CONFORME MER_Estrutura.txt =====

class Especialidade(Base):
    """
    Entidade: ESPECIALIDADE
    - id_especialidade (PK)
    - nome (UK)
    """
    __tablename__ = "especialidade"
    
    id_especialidade = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    
    # Relacionamentos
    medicos = relationship("Medico", back_populates="especialidade")

class PlanoSaude(Base):
    """
    Entidade: PLANO_SAUDE (Conforme MER, não Convênio)
    - id_plano_saude (PK)
    - nome
    - cobertura_info
    """
    __tablename__ = "plano_saude"
    
    id_plano_saude = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cobertura_info = Column(Text)
    
    # Relacionamentos
    pacientes = relationship("Paciente", back_populates="plano_saude")

class Administrador(Base):
    """
    Entidade: ADMINISTRADOR
    - id_admin (PK)
    - nome
    - email (UK)
    - senha_hash
    - papel
    """
    __tablename__ = "administrador"
    
    id_admin = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    papel = Column(String(100))
    
    # Relacionamentos
    relatorios = relationship("Relatorio", back_populates="administrador")

class Medico(Base):
    """
    Entidade: MEDICO
    - id_medico (PK)
    - nome
    - cpf (UK)
    - email (UK)
    - senha_hash
    - crm (UK)
    - telefone
    - id_especialidade_fk (FK)
    """
    __tablename__ = "medico"
    
    id_medico = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    crm = Column(String(20), unique=True, nullable=False)
    telefone = Column(String(20), nullable=True)
    id_especialidade_fk = Column(Integer, ForeignKey("especialidade.id_especialidade"), nullable=False)
    
    # Relacionamentos
    especialidade = relationship("Especialidade", back_populates="medicos")
    horarios_trabalho = relationship("HorarioTrabalho", back_populates="medico")
    consultas = relationship("Consulta", back_populates="medico")
    bloqueios = relationship("BloqueioHorario", back_populates="medico")

class Paciente(Base):
    """
    Entidade: PACIENTE
    - id_paciente (PK)
    - nome
    - cpf (UK)
    - email (UK)
    - senha_hash
    - telefone
    - data_nascimento
    - esta_bloqueado
    - id_plano_saude_fk (FK, Nullable)
    """
    __tablename__ = "paciente"
    
    id_paciente = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    telefone = Column(String(20))
    data_nascimento = Column(Date, nullable=False)
    esta_bloqueado = Column(Boolean, default=False)
    id_plano_saude_fk = Column(Integer, ForeignKey("plano_saude.id_plano_saude"), nullable=True)
    
    # Relacionamentos
    plano_saude = relationship("PlanoSaude", back_populates="pacientes")
    consultas = relationship("Consulta", back_populates="paciente")

class Relatorio(Base):
    """
    Entidade: RELATORIO
    - id_relatorio (PK)
    - tipo
    - data_geracao
    - dados_resultado
    - id_admin_fk (FK)
    """
    __tablename__ = "relatorio"
    
    id_relatorio = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(100), nullable=False)
    data_geracao = Column(DateTime, default=datetime.utcnow)
    dados_resultado = Column(Text)
    id_admin_fk = Column(Integer, ForeignKey("administrador.id_admin"), nullable=False)
    
    # Relacionamentos
    administrador = relationship("Administrador", back_populates="relatorios")

class HorarioTrabalho(Base):
    """
    Entidade: HORARIO_TRABALHO
    - id_horario (PK)
    - dia_semana
    - hora_inicio
    - hora_fim
    - id_medico_fk (FK)
    """
    __tablename__ = "horario_trabalho"
    
    id_horario = Column(Integer, primary_key=True, index=True)
    dia_semana = Column(Integer, nullable=False)  # 0=Segunda, 6=Domingo
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    id_medico_fk = Column(Integer, ForeignKey("medico.id_medico"), nullable=False)
    
    # Relacionamentos
    medico = relationship("Medico", back_populates="horarios_trabalho")

class Consulta(Base):
    """
    Entidade: CONSULTA
    - id_consulta (PK)
    - data_hora_inicio
    - data_hora_fim
    - status
    - id_paciente_fk (FK)
    - id_medico_fk (FK)
    """
    __tablename__ = "consulta"
    
    id_consulta = Column(Integer, primary_key=True, index=True)
    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime, nullable=True)
    status = Column(String(50), default="Agendada")
    id_paciente_fk = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_medico_fk = Column(Integer, ForeignKey("medico.id_medico"), nullable=False)
    
    # Relacionamentos
    paciente = relationship("Paciente", back_populates="consultas")
    medico = relationship("Medico", back_populates="consultas")
    observacao = relationship("Observacao", back_populates="consulta", uselist=False)

class Observacao(Base):
    """
    Entidade: OBSERVACAO
    - id_observacao (PK)
    - descricao
    - data_criacao
    - id_consulta_fk (FK)
    """
    __tablename__ = "observacao"
    
    id_observacao = Column(Integer, primary_key=True, index=True)
    descricao = Column(Text, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    id_consulta_fk = Column(Integer, ForeignKey("consulta.id_consulta"), unique=True, nullable=False)
    
    # Relacionamentos
    consulta = relationship("Consulta", back_populates="observacao")

class BloqueioHorario(Base):
    """
    Entidade: BLOQUEIO_HORARIO
    - id_bloqueio (PK)
    - data
    - hora_inicio
    - hora_fim
    - motivo
    - id_medico_fk (FK)
    """
    __tablename__ = "bloqueio_horario"
    
    id_bloqueio = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    motivo = Column(String(200))
    id_medico_fk = Column(Integer, ForeignKey("medico.id_medico"), nullable=False)
    
    # Relacionamentos
    medico = relationship("Medico", back_populates="bloqueios")
