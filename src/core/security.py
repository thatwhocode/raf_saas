from passlib.context import CryptContext
from shared_packages.core.config import SharedBaseSettings
class Settings(SharedBaseSettings):
    APP_NAME: str="Auth"
settings = Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")
def verify_password(plain_password : str, hashed_password : str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str)->str:
    return pwd_context.hash(password)
