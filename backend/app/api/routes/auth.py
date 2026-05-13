from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUserDep, DbSessionDep, SettingsDep
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: DbSessionDep) -> UserRead:
    """Create a user account."""
    service = UserService(db)
    existing_user = await service.get_by_email(payload.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    return await service.create(payload)


@router.post("/login", response_model=Token)
async def login(
    settings: SettingsDep,
    db: DbSessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """OAuth2-compatible login endpoint for Swagger and clients."""
    user = await UserService(db).authenticate(
        email=form_data.username,
        password=form_data.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(subject=str(user.id), settings=settings),
        token_type="bearer",
    )


@router.post("/login/json", response_model=Token)
async def login_json(
    payload: LoginRequest,
    settings: SettingsDep,
    db: DbSessionDep,
) -> Token:
    """JSON login endpoint used by the frontend."""
    user = await UserService(db).authenticate(
        email=payload.email,
        password=payload.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    return Token(
        access_token=create_access_token(subject=str(user.id), settings=settings),
        token_type="bearer",
    )


@router.get("/me", response_model=UserRead)
async def read_me(current_user: CurrentUserDep) -> UserRead:
    """Return the current authenticated user."""
    return current_user

