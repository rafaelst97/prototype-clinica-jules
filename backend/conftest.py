"""
Configuração global de testes - Pytest Fixtures
Otimizado para máxima performance com caching e paralelização
"""
import pytest
from fastapi.testclient import TestClient as FastAPIClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, date, time

from app.main import app
from app.database import Base, get_db
from app.models.models import (
    Especialidade, PlanoSaude, Administrador, Medico, 
    Paciente, HorarioTrabalho, Consulta
)
from passlib.context import CryptContext

# Engine SQLite em memória com StaticPool para reutilização entre testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Reutiliza a mesma conexão em memória
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="session")
def db_engine():
    """Engine do banco - criado uma vez por sessão de testes"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Sessão de banco isolada por teste com rollback automático"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


import fastapi.testclient

@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de testes com banco de dados mockado"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with fastapi.testclient.TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ========== FIXTURES DE DADOS (CACHED) ==========

@pytest.fixture(scope="function")
def especialidade_cardiologia(db_session):
    """Especialidade: Cardiologia"""
    esp = Especialidade(nome="Cardiologia")
    db_session.add(esp)
    db_session.commit()
    db_session.refresh(esp)
    return esp


@pytest.fixture(scope="function")
def especialidade_ortopedia(db_session):
    """Especialidade: Ortopedia"""
    esp = Especialidade(nome="Ortopedia")
    db_session.add(esp)
    db_session.commit()
    db_session.refresh(esp)
    return esp


@pytest.fixture(scope="function")
def plano_unimed(db_session):
    """Plano de Saúde: Unimed"""
    plano = PlanoSaude(
        nome="Unimed",
        cobertura_info="Cobertura completa nacional"
    )
    db_session.add(plano)
    db_session.commit()
    db_session.refresh(plano)
    return plano


@pytest.fixture(scope="function")
def plano_sulamerica(db_session):
    """Plano de Saúde: SulAmérica"""
    plano = PlanoSaude(
        nome="SulAmérica",
        cobertura_info="Rede credenciada premium"
    )
    db_session.add(plano)
    db_session.commit()
    db_session.refresh(plano)
    return plano


@pytest.fixture(scope="function")
def admin_user(db_session):
    """Administrador do sistema"""
    admin = Administrador(
        nome="Admin Sistema",
        email="admin@test.com",
        senha_hash=pwd_context.hash("admin123"),
        papel="Admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def medico_cardiologista(db_session, especialidade_cardiologia):
    """Médico Cardiologista"""
    medico = Medico(
        nome="Dr. João Silva",
        cpf="11122233344",
        email="joao@test.com",
        senha_hash=pwd_context.hash("medico123"),
        crm="CRM-12345",
        id_especialidade_fk=especialidade_cardiologia.id_especialidade
    )
    db_session.add(medico)
    db_session.commit()
    db_session.refresh(medico)
    return medico


@pytest.fixture(scope="function")
def medico_ortopedista(db_session, especialidade_ortopedia):
    """Médico Ortopedista"""
    medico = Medico(
        nome="Dra. Maria Santos",
        cpf="55566677788",
        email="maria@test.com",
        senha_hash=pwd_context.hash("medico123"),
        crm="CRM-67890",
        id_especialidade_fk=especialidade_ortopedia.id_especialidade
    )
    db_session.add(medico)
    db_session.commit()
    db_session.refresh(medico)
    return medico


@pytest.fixture(scope="function")
def horarios_trabalho_cardio(db_session, medico_cardiologista):
    """Horários de trabalho do cardiologista (Seg-Sex 9h-17h)"""
    horarios = []
    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    
    for dia in dias_semana:
        horario = HorarioTrabalho(
            dia_semana=dia,
            hora_inicio=time(9, 0),
            hora_fim=time(17, 0),
            id_medico_fk=medico_cardiologista.id_medico
        )
        horarios.append(horario)
        db_session.add(horario)
    
    db_session.commit()
    for h in horarios:
        db_session.refresh(h)
    return horarios


@pytest.fixture(scope="function")
def paciente_teste(db_session, plano_unimed):
    """Paciente de teste"""
    paciente = Paciente(
        nome="Carlos Teste",
        cpf="99988877766",
        email="carlos@test.com",
        senha_hash=pwd_context.hash("paciente123"),
        telefone="47-99999-9999",
        data_nascimento=date(1990, 5, 15),
        id_plano_saude_fk=plano_unimed.id_plano_saude,
        esta_bloqueado=False
    )
    db_session.add(paciente)
    db_session.commit()
    db_session.refresh(paciente)
    return paciente


@pytest.fixture(scope="function")
def paciente_sem_plano(db_session):
    """Paciente sem plano de saúde (particular)"""
    paciente = Paciente(
        nome="Ana Particular",
        cpf="44455566677",
        email="ana@test.com",
        senha_hash=pwd_context.hash("paciente123"),
        telefone="47-88888-8888",
        data_nascimento=date(1985, 3, 20),
        id_plano_saude_fk=None,
        esta_bloqueado=False
    )
    db_session.add(paciente)
    db_session.commit()
    db_session.refresh(paciente)
    return paciente


@pytest.fixture(scope="function")
def token_admin(client, admin_user):
    """Token JWT do administrador"""
    response = client.post(
        "/auth/login",
        json={"email": "admin@test.com", "senha": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def token_medico(client, medico_cardiologista):
    """Token JWT do médico"""
    response = client.post(
        "/auth/login",
        json={"email": "joao@test.com", "senha": "medico123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def token_paciente(client, paciente_teste):
    """Token JWT do paciente"""
    response = client.post(
        "/auth/login",
        json={"email": "carlos@test.com", "senha": "paciente123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers_admin(token_admin):
    """Headers com autenticação de admin"""
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture(scope="function")
def auth_headers_medico(token_medico):
    """Headers com autenticação de médico"""
    return {"Authorization": f"Bearer {token_medico}"}


@pytest.fixture(scope="function")
def auth_headers_paciente(token_paciente):
    """Headers com autenticação de paciente"""
    return {"Authorization": f"Bearer {token_paciente}"}


@pytest.fixture(scope="function")
def consulta_agendada(db_session, paciente_teste, medico_cardiologista):
    """Cria uma consulta agendada para daqui a 48 horas."""
    data_hora = datetime.now() + timedelta(hours=48)
    consulta = Consulta(
        id_paciente_fk=paciente_teste.id_paciente,
        id_medico_fk=medico_cardiologista.id_medico,
        data_hora_inicio=data_hora,
        data_hora_fim=data_hora + timedelta(minutes=30),
        status="agendada"
    )
    db_session.add(consulta)
    db_session.commit()
    db_session.refresh(consulta)
    return consulta


@pytest.fixture(scope="function")
def consulta_proxima(db_session, paciente_teste, medico_cardiologista):
    """Cria uma consulta agendada para daqui a 12 horas."""
    data_hora = datetime.now() + timedelta(hours=12)
    consulta = Consulta(
        id_paciente_fk=paciente_teste.id_paciente,
        id_medico_fk=medico_cardiologista.id_medico,
        data_hora_inicio=data_hora,
        data_hora_fim=data_hora + timedelta(minutes=30),
        status="agendada"
    )
    db_session.add(consulta)
    db_session.commit()
    db_session.refresh(consulta)
    return consulta


@pytest.fixture(scope="function")
def paciente_com_duas_consultas(db_session, paciente_teste, medico_cardiologista):
    """Cria um paciente com duas consultas futuras já agendadas."""
    # Consulta 1
    data_1 = datetime.now() + timedelta(days=5)
    c1 = Consulta(
        id_paciente_fk=paciente_teste.id_paciente,
        id_medico_fk=medico_cardiologista.id_medico,
        data_hora_inicio=data_1,
        data_hora_fim=data_1 + timedelta(minutes=30),
        status="agendada"
    )
    # Consulta 2
    data_2 = datetime.now() + timedelta(days=8)
    c2 = Consulta(
        id_paciente_fk=paciente_teste.id_paciente,
        id_medico_fk=medico_cardiologista.id_medico,
        data_hora_inicio=data_2,
        data_hora_fim=data_2 + timedelta(minutes=30),
        status="agendada"
    )
    db_session.add_all([c1, c2])
    db_session.commit()
    return paciente_teste.id_paciente


@pytest.fixture(scope="function")
def paciente_bloqueado(db_session):
    """Cria um paciente que está bloqueado."""
    paciente = Paciente(
        nome="Paciente Bloqueado",
        cpf="12312312300",
        email="bloqueado@test.com",
        senha_hash=pwd_context.hash("senha123"),
        data_nascimento=date(1995, 1, 1),
        esta_bloqueado=True
    )
    db_session.add(paciente)
    db_session.commit()
    db_session.refresh(paciente)
    return paciente

@pytest.fixture(scope="function")
def medico_sem_horario(db_session, especialidade_ortopedia):
    """Cria um médico sem horário de trabalho configurado."""
    medico = Medico(
        nome="Dr. Sem Horário",
        cpf="98765432100",
        email="semhorario@test.com",
        senha_hash=pwd_context.hash("medico123"),
        crm="CRM-00000",
        id_especialidade_fk=especialidade_ortopedia.id_especialidade
    )
    db_session.add(medico)
    db_session.commit()
    db_session.refresh(medico)
    return medico

@pytest.fixture(scope="function")
def token_paciente_bloqueado(client, paciente_bloqueado):
    """Gera um token para o paciente bloqueado."""
    # Nota: O login pode falhar se a lógica de bloqueio estiver no endpoint de login.
    # A abordagem aqui é gerar o token diretamente para testar endpoints de agendamento.
    from app.utils.auth import create_access_token
    token = create_access_token(data={"sub": paciente_bloqueado.email, "user_type": "paciente", "user_id": paciente_bloqueado.id_paciente})
    return token

@pytest.fixture(scope="function")
def auth_headers_paciente_bloqueado(token_paciente_bloqueado):
    """Headers de autenticação para o paciente bloqueado."""
    return {"Authorization": f"Bearer {token_paciente_bloqueado}"}


@pytest.fixture(scope="function")
def token_medico_ortopedista(client, medico_ortopedista):
    """Token JWT do médico ortopedista"""
    response = client.post(
        "/auth/login",
        json={"email": "maria@test.com", "senha": "medico123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers_medico_ortopedista(token_medico_ortopedista):
    """Headers com autenticação de médico ortopedista"""
    return {"Authorization": f"Bearer {token_medico_ortopedista}"}
