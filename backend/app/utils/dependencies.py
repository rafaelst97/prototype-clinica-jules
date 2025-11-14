from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, TipoUsuario
from app.utils.auth import decode_access_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """Retorna o usuário atual baseado no token JWT"""
    token = credentials.credentials
    email = decode_access_token(token)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    if usuario.bloqueado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário bloqueado. Entre em contato com a administração"
        )
    
    return usuario

def get_current_paciente(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Verifica se o usuário atual é um paciente"""
    if current_user.tipo != TipoUsuario.PACIENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para pacientes"
        )
    return current_user

def get_current_medico(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Verifica se o usuário atual é um médico"""
    if current_user.tipo != TipoUsuario.MEDICO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para médicos"
        )
    return current_user

def get_current_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Verifica se o usuário atual é um administrador"""
    if current_user.tipo != TipoUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para administradores"
        )
    return current_user
