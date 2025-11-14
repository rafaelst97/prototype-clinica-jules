from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import Usuario, Medico
from app.schemas import Token, LoginRequest, UsuarioResponse, AlterarSenhaRequest
from app.utils.auth import verify_password, create_access_token, get_password_hash
from app.utils.dependencies import get_current_user
from app.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login de usuário - retorna token JWT"""
    usuario = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not verify_password(login_data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
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
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.email, "tipo": usuario.tipo.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

class MedicoLoginRequest(BaseModel):
    crm: str
    senha: str

@router.post("/login/medico", response_model=Token)
def login_medico(login_data: MedicoLoginRequest, db: Session = Depends(get_db)):
    """Login de médico usando CRM - retorna token JWT"""
    # Buscar médico pelo CRM
    medico = db.query(Medico).filter(Medico.crm == login_data.crm).first()
    
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CRM ou senha incorretos"
        )
    
    # Buscar usuário associado
    usuario = db.query(Usuario).filter(Usuario.id == medico.usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CRM ou senha incorretos"
        )
    
    if not verify_password(login_data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CRM ou senha incorretos"
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
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.email, "tipo": usuario.tipo.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "nome": usuario.nome
    }

@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """Retorna dados do usuário logado"""
    return current_user

@router.put("/alterar-senha", status_code=status.HTTP_200_OK)
def alterar_senha(
    dados: AlterarSenhaRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera senha do usuário logado
    Conforme requisito UML: Usuario.alterarSenha()
    """
    
    # Verificar se senha atual está correta
    if not verify_password(dados.senha_atual, current_user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta"
        )
    
    # Verificar se senha nova é diferente da atual
    if dados.senha_atual == dados.senha_nova:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha deve ser diferente da senha atual"
        )
    
    # Atualizar senha
    current_user.senha_hash = get_password_hash(dados.senha_nova)
    db.commit()
    
    return {"message": "Senha alterada com sucesso"}
