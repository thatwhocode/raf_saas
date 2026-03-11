from src.auth.user_repo import UserRepository
from src.auth.schemas.user import UserCreate, UserLoginEmail, UserUpdate,  UserLoginUsername, UserRead
from fastapi import HTTPException, status, Depends
from src.core.security import get_password_hash, verify_password
from shared_packages.core.security import create_access_token
from src.auth.schemas.token import Token
from jose.jwt import decode, JWTError
from shared_packages.core.config import SharedBaseSettings
settings = SharedBaseSettings()
from sqlalchemy import func, select
from uuid import UUID
class AuthService:
    def __init__(self, userRepo: UserRepository):
        self.user_repo = userRepo
    def _generate_token_response(self, user) -> dict:
        access_token = create_access_token(
            data={
                "sub": str(user.id), 
                "email": user.email 
            }
        )
        return {"access_token": access_token, "token_type": "bearer"}
    async def register_user(self, user_data: UserCreate):
        email =  await self.user_repo.find_user_email(user_data.email)
        if email :
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="this email already in use")
    
        username =  await self.user_repo.find_username(user_data.username)
        if username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                     detail="this username already exist")
        new_user = await self.user_repo.create_user(user_data)
        await self.user_repo.session.commit()
        await self.user_repo.session.refresh(new_user)
        return new_user
    
    async def login_with_email(self, user_data:UserLoginEmail ) -> Token:
        user  = await self.user_repo.find_user_email(user_email=user_data.email)
        if user == None or not verify_password(user_data.password.get_secret_value(), user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="Wrong login or password")
        return self._generate_token_response(user)
    async def login_with_username(self, user_data:UserLoginUsername ) -> Token:
        user  = await self.user_repo.find_username(username=user_data.username)
        print(f"DEBUG: User found: {user.username if user else 'None'}")
        if user == None or not verify_password(user_data.password.get_secret_value(), user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="Wrong login or password")
        return self._generate_token_response(user)
    async def get_user_from_token(self, token : Token)-> UserRead:
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                               detail="Couldn`t verify credentials",
                                               headers={"WWW-Authenticate: Bearer"})
        try:
            payload = decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id : str = payload.get("sub")
        except JWTError:
            raise credentials_exception
        user = await self.user_repo.find_user_by_id(user_id)
        if user is None:
            raise credentials_exception
        return user
    async def update_profile(self, user_id : UUID, update_data : UserUpdate) -> UserRead:
        data_to_update = update_data.model_dump(exclude_unset=True)
    
        if not data_to_update:
            return await self.user_repo.find_user_by_id(user_id)
        
        return await self.user_repo.update_user_by_id(user_id, data_to_update)
    