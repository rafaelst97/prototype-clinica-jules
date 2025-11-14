"""
Router de Autenticação - Sistema Clínica Saúde+
Atualizado para trabalhar com modelo conforme MER
Suporta login para Paciente, Médico e Administrador
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.models import Paciente, Medico, Administrador
from app.schemas.schemas import Token, LoginRequest, AlterarSenhaRequest
from app.utils.auth import verify_password, create_access_token, get_password_hash
from app.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Autenticação"])


class LoginCRMRequest(BaseModel):
    crm: str
    senha: str


def autenticar_usuario(email: str, senha: str, db: Session) -> tuple:
    """
    Tenta autenticar usuário em todas as tabelas (Paciente, Medico, Administrador)
    
    Returns:
        tuple: (user_object, user_type: str) ou (None, None)
    """
    # Tentar autenticar como Paciente
    paciente = db.query(Paciente).filter(Paciente.email == email).first()
    if paciente and verify_password(senha, paciente.senha_hash):
        return paciente, "paciente"
    
    # Tentar autenticar como Médico
    medico = db.query(Medico).filter(Medico.email == email).first()
    if medico and verify_password(senha, medico.senha_hash):
        return medico, "medico"
    
    # Tentar autenticar como Administrador
    admin = db.query(Administrador).filter(Administrador.email == email).first()
    if admin and verify_password(senha, admin.senha_hash):
        return admin, "administrador"
    
    return None, None


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login unificado para todos os tipos de usuários (Paciente, Médico, Administrador)
    Conforme requisito: Login com e-mail e senha alfanumérica (8 a 20 caracteres)
    """
    usuario, tipo_usuario = autenticar_usuario(login_data.email, login_data.senha, db)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar se paciente está bloqueado (RN3)
    if tipo_usuario == "paciente" and usuario.esta_bloqueado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta bloqueada por faltas consecutivas. Entre em contato com a administração."
        )
    
    # Criar token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Definir user_id baseado no tipo
    if tipo_usuario == "paciente":
        user_id = usuario.id_paciente
    elif tipo_usuario == "medico":
        user_id = usuario.id_medico
    else:  # administrador
        user_id = usuario.id_admin
    
    access_token = create_access_token(
        data={
            "sub": usuario.email,
            "tipo": tipo_usuario,
            "id": user_id  # Mudado de user_id para id
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": tipo_usuario,
        "user_id": user_id
    }


@router.post("/login/crm", response_model=Token)
def login_medico_por_crm(login_data: LoginCRMRequest, db: Session = Depends(get_db)):
    """
    Login alternativo para médicos usando CRM ao invés de email
    """
    medico = db.query(Medico).filter(Medico.crm == login_data.crm).first()
    
    if not medico or not verify_password(login_data.senha, medico.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CRM ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": medico.email,
            "tipo": "medico",
            "user_id": medico.id_medico
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "medico",
        "user_id": medico.id_medico
    }


@router.post("/alterar-senha")
def alterar_senha(
    dados: AlterarSenhaRequest,
    email: str,
    tipo_usuario: str,
    db: Session = Depends(get_db)
):
    """
    Altera senha do usuário
    Conforme requisito UML: Usuario.alterarSenha(novaSenha)
    
    Args:
        email: Email do usuário (obtido do token JWT)
        tipo_usuario: Tipo do usuário ('paciente', 'medico', 'administrador')
    """
    # Buscar usuário conforme tipo
    if tipo_usuario == "paciente":
        usuario = db.query(Paciente).filter(Paciente.email == email).first()
    elif tipo_usuario == "medico":
        usuario = db.query(Medico).filter(Medico.email == email).first()
    elif tipo_usuario == "administrador":
        usuario = db.query(Administrador).filter(Administrador.email == email).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de usuário inválido"
        )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar senha atual
    if not verify_password(dados.senha_atual, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta"
        )
    
    # Verificar se senha nova é diferente
    if dados.senha_atual == dados.senha_nova:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha deve ser diferente da senha atual"
        )
    
    # Atualizar senha
    usuario.senha_hash = get_password_hash(dados.senha_nova)
    db.commit()
    
    return {
        "sucesso": True,
        "mensagem": "Senha alterada com sucesso"
    }


@router.get("/verificar-token")
def verificar_token(email: str, tipo_usuario: str, user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para verificar se token ainda é válido e retornar dados básicos do usuário
    Útil para o frontend verificar autenticação
    """
    # Buscar usuário conforme tipo
    if tipo_usuario == "paciente":
        usuario = db.query(Paciente).filter(Paciente.id_paciente == user_id).first()
    elif tipo_usuario == "medico":
        usuario = db.query(Medico).filter(Medico.id_medico == user_id).first()
    elif tipo_usuario == "administrador":
        usuario = db.query(Administrador).filter(Administrador.id_admin == user_id).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de usuário inválido"
        )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar se paciente está bloqueado
    if tipo_usuario == "paciente" and usuario.esta_bloqueado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta bloqueada"
        )
    
    return {
        "valido": True,
        "user_id": user_id,
        "tipo_usuario": tipo_usuario,
        "nome": usuario.nome,
        "email": usuario.email
    }
