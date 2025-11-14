from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# Garante que o caminho para o .env seja relativo ao arquivo config.py
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')

class Settings(BaseSettings):
    # Aponta explicitamente para o arquivo .env
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding='utf-8', extra='ignore')

    POSTGRES_USER: str = "clinica_user"
    POSTGRES_PASSWORD: str = "clinica_pass"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "clinica_saude"
    
    SECRET_KEY: str = "sua-chave-secreta-super-segura-mude-em-producao-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    APP_ENV: str = "production" # 'production' ou 'test'
    
    # Pode ser sobrescrito pela variável de ambiente
    DATABASE_URL: str | None = None

    @property
    def TESTING(self) -> bool:
        return self.APP_ENV == "test"

    @property
    def database_url(self) -> str:
        # Se DATABASE_URL estiver definida (docker-compose), usar ela
        if self.DATABASE_URL:
            return self.DATABASE_URL
            
        if self.TESTING:
            # Usar SQLite em memória para testes
            return "sqlite:///./test.db"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
