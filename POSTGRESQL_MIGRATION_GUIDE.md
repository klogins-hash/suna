# PostgreSQL Migration Guide

Your Suna project has been successfully configured to use Railway PostgreSQL instead of Supabase. Here's what was implemented and what you need to do next.

## ✅ What's Been Done

### 1. Railway Configuration Updated
- **`railway.toml`**: Added PostgreSQL service configuration
- **`.env.railway`**: Updated environment variables for PostgreSQL
- **`railway.json`**: Updated for single-service deployment

### 2. Database Layer Replaced
- **`backend/services/database.py`**: New PostgreSQL adapter with Supabase-compatible interface
- **`backend/pyproject.toml`**: Updated dependencies (removed Supabase, added asyncpg, SQLAlchemy, Alembic)
- **`backend/utils/config.py`**: Added PostgreSQL configuration variables

### 3. Authentication System
- **`backend/services/auth.py`**: FastAPI-Users implementation with JWT authentication
- **`backend/services/postgresql_migration.py`**: Migration helper and patterns

### 4. Database Migrations
- **`backend/alembic.ini`**: Alembic configuration for database migrations
- **`backend/migrations/env.py`**: Migration environment setup
- **`backend/migrations/script.py.mako`**: Migration script template

## 🚀 Next Steps

### 1. Deploy to Railway

1. **Create Railway Project**:
   ```bash
   # Connect your GitHub repo to Railway
   # Add PostgreSQL service in Railway dashboard
   # Add Redis service in Railway dashboard
   ```

2. **Set Environment Variables** in Railway dashboard:
   ```bash
   ENV_MODE=production
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_HOST=${{Redis.RAILWAY_PRIVATE_DOMAIN}}
   REDIS_PORT=${{Redis.RAILWAY_TCP_PROXY_PORT}}
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   API_KEY_SECRET=your_random_secret_here
   # ... other variables from .env.railway
   ```

### 2. Update Existing Code

The current codebase still has Supabase imports that need to be replaced:

**Replace these imports:**
```python
# OLD
from services.supabase import DBConnection
from supabase import create_async_client

# NEW  
from services.database import db
from services.auth import current_active_user, fastapi_users
```

**Update database calls:**
```python
# OLD
result = await supabase.table("users").select("*").execute()

# NEW
result = await db.fetch("SELECT * FROM users")
# OR using the compatibility layer:
result = await db.table("users").select("*").execute()
```

### 3. Run Migrations

After deployment, run database migrations:
```bash
cd backend
uv run alembic upgrade head
```

### 4. Update API Routes

Add authentication routes to your main API:
```python
# In backend/api.py
from services.postgresql_migration import auth_router

app.include_router(auth_router)
```

## 🔧 Key Changes Summary

### Dependencies
- ❌ Removed: `supabase==2.17.0`
- ✅ Added: `asyncpg==0.29.0`, `sqlalchemy[asyncio]==2.0.23`, `alembic==1.13.1`
- ✅ Added: `fastapi-users[sqlalchemy]==13.0.0`, `python-jose[cryptography]==3.3.0`

### Database Connection
- **Before**: Supabase client with built-in auth
- **After**: PostgreSQL with asyncpg + FastAPI-Users for auth

### Authentication
- **Before**: Supabase Auth (automatic)
- **After**: FastAPI-Users with JWT tokens

### Environment Variables
- **Before**: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- **After**: `DATABASE_URL` (Railway provides this automatically)

## 🛠️ Migration Commands

### Install New Dependencies
```bash
cd backend
uv sync
```

### Initialize Database
```bash
uv run alembic init migrations  # Already done
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head
```

### Test Database Connection
```python
# Test script
from services.database import db
import asyncio

async def test_connection():
    await db.initialize()
    result = await db.fetch("SELECT 1 as test")
    print(f"Database connected: {result}")

asyncio.run(test_connection())
```

## 🔍 Compatibility Layer

The new `database.py` provides a compatibility layer that mimics Supabase's interface:

```python
# This still works with the new system:
result = await db.table("users").select("*").eq("email", "user@example.com").execute()

# But you can also use raw SQL for better performance:
result = await db.fetch("SELECT * FROM users WHERE email = $1", "user@example.com")
```

## 🚨 Important Notes

1. **Authentication Changes**: Users will need to re-register as the auth system changed
2. **Data Migration**: If you have existing Supabase data, you'll need to export and import it
3. **File Storage**: Supabase Storage is not replaced - you may need AWS S3 or similar
4. **Real-time Features**: PostgreSQL doesn't have built-in real-time like Supabase

## 📞 Support

If you encounter issues:
1. Check Railway logs for deployment errors
2. Verify all environment variables are set
3. Test database connection locally first
4. Review the migration patterns in `postgresql_migration.py`

Your Suna project is now ready for Railway deployment with PostgreSQL! 🎉
