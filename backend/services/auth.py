"""
FastAPI-Users authentication system for PostgreSQL.
Replaces Supabase authentication.
"""

import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTAuthentication,
)
from fastapi_users.db import SQLAlchemyAdapter
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from datetime import datetime

from utils.config import config
from utils.logger import logger

# Database setup
engine = create_async_engine(config.DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyAdapter(session, User)

class UserManager(BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = config.API_KEY_SECRET
    verification_token_secret = config.API_KEY_SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# Authentication setup
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

jwt_authentication = JWTAuthentication(
    secret=config.API_KEY_SECRET,
    lifetime_seconds=3600,
    tokenUrl="auth/jwt/login",
)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=lambda: jwt_authentication,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

# Compatibility functions for existing Supabase code
async def get_current_user(request: Request) -> Optional[User]:
    """Get current user from request. Returns None if not authenticated."""
    try:
        user = await current_active_user(request)
        return user
    except Exception:
        return None

async def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify JWT token and return user data."""
    try:
        # This is a simplified version - in production you'd want proper JWT verification
        from jose import jwt
        payload = jwt.decode(token, config.API_KEY_SECRET, algorithms=["HS256"])
        return payload
    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        return None

# Database initialization
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
