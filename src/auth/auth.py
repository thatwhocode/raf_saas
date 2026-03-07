from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.auth.schemas.user import UserCreate, UserLoginEmail, UserRead, UserLoginUsername, UserUpdate, UserBase
from src.api.deps import Dependencies, AuthService, oauth2_scheme, AdminRequired
from src.auth.schemas.token import Token
from uuid import UUID
auth_router = APIRouter()

@auth_router.post("/register",  response_model = UserRead)
async def register(user_data : UserCreate, deps : Dependencies =  Depends(Dependencies)):
    result = await deps.auth_service.register_user(user_data=user_data)
    return result
@auth_router.post("/login_via_email", response_model=Token)
async def login_with_email(user_data : UserLoginEmail, deps: Dependencies = Depends(Dependencies)):
    result = await deps.auth_service.login_with_email(user_data=user_data)
    return result
@auth_router.post("/login_via_username", response_model= Token)
async def login_with_usernmae(user_data: UserLoginUsername, deps: Dependencies = Depends(Dependencies)):
    result = await deps.auth_service.login_with_username(user_data=user_data)
    return result
@auth_router.post("/token")
async def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    deps: Dependencies = Depends()
):

    if "@" in form_data.username:
        login_data = UserLoginEmail(
            email=form_data.username, 
            password=form_data.password
        )
        return await deps.auth_service.login_with_email(login_data)
    else:
        login_data = UserLoginUsername(
            username=form_data.username, 
            password=form_data.password
        )
        return await deps.auth_service.login_with_username(login_data)
@auth_router.get("/me", response_model=UserRead)
async def get_me(
    token: str = Depends(oauth2_scheme), 
    deps: Dependencies = Depends()
):
    user = await deps.auth_service.get_user_from_token(token)
    return user
@auth_router.patch("/me/update", response_model=UserRead)
async def update_my_profile(
    update_data: UserUpdate, 
    token: str = Depends(oauth2_scheme),
    deps: Dependencies = Depends(Dependencies)
):
    current_user = await deps.get_current_user(token)

    return await deps.auth_service.update_profile(current_user.id, update_data)
