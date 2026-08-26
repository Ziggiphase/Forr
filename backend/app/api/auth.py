from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.email import send_verification_email

router = APIRouter()

@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        nin=user_in.nin,
        dob=user_in.dob,
        nationality=user_in.nationality,
        gender=user_in.gender,
        state=user_in.state,
        address=user_in.address,
        phone_number=user_in.phone_number,
        password_hash=hashed_password,
        is_active=False, # Wait for email verification
        is_email_verified=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # We use a simple token for email verification. In production, this should be signed/encrypted.
    verify_token = str(new_user.id)
    await send_verification_email(new_user.email, verify_token)
    
    return new_user

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        user_id = uuid.UUID(token)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    if user.is_email_verified:
        return {"msg": "Email already verified"}

    user.is_email_verified = True
    user.is_active = True
    await db.commit()
    return {"msg": "Email verified successfully"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_email_verified:
        raise HTTPException(status_code=400, detail="Email not verified. Please check your inbox.")
        
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
