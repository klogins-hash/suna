# Database Alternatives to Supabase

While Suna currently uses Supabase, you can replace it with other database solutions. Here are your options:

## Option 1: Railway PostgreSQL (Recommended Alternative)

**Pros:**
- Managed PostgreSQL service
- Integrated with Railway platform
- Similar features to Supabase
- Automatic backups and scaling

**Setup:**
1. Add PostgreSQL service in Railway dashboard
2. Update environment variables to use Railway's PostgreSQL
3. Modify database connection code (see code changes below)

**Environment Variables:**
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
```

## Option 2: SQLite (Simplest)

**Pros:**
- No external service needed
- File-based, simple setup
- Good for single-instance deployments

**Cons:**
- Not suitable for multi-instance scaling
- No built-in authentication features

**Setup:**
```bash
DATABASE_URL=sqlite:///app/data/suna.db
```

## Option 3: Other PostgreSQL Providers

**Options:**
- Neon (serverless PostgreSQL)
- PlanetScale (MySQL-compatible)
- AWS RDS
- Google Cloud SQL
- Any PostgreSQL service

## Required Code Changes

To switch from Supabase, you'll need to modify these files:

### 1. Replace Supabase Client (`backend/services/supabase.py`)

**Current (Supabase):**
```python
from supabase import create_async_client, AsyncClient

class DBConnection:
    async def initialize(self):
        self._client = await create_async_client(
            config.SUPABASE_URL,
            config.SUPABASE_SERVICE_ROLE_KEY
        )
```

**New (PostgreSQL with asyncpg):**
```python
import asyncpg
from typing import Optional

class DBConnection:
    async def initialize(self):
        self._pool = await asyncpg.create_pool(
            config.DATABASE_URL,
            min_size=1,
            max_size=10
        )
```

### 2. Update Dependencies (`backend/pyproject.toml`)

**Remove:**
```toml
"supabase==2.17.0",
```

**Add:**
```toml
"asyncpg==0.29.0",
"sqlalchemy[asyncio]==2.0.23",
"alembic==1.13.1",  # for migrations
```

### 3. Authentication Changes

Supabase provides built-in authentication. For alternatives, you'll need to:

**Option A: Implement custom JWT auth**
```python
# Add to dependencies
"python-jose[cryptography]==3.3.0",
"passlib[bcrypt]==1.7.4",
```

**Option B: Use FastAPI-Users**
```python
# Add to dependencies  
"fastapi-users[sqlalchemy]==13.0.0",
```

**Option C: Remove authentication (development only)**
- Comment out auth middleware in `api.py`
- Skip user verification in endpoints

## Migration Steps

### For Railway PostgreSQL:

1. **Add PostgreSQL service in Railway**
2. **Install new dependencies:**
   ```bash
   cd backend
   uv add asyncpg sqlalchemy[asyncio] alembic
   uv remove supabase
   ```

3. **Create database adapter:**
   ```python
   # backend/services/database.py
   import asyncpg
   from utils.config import config
   
   class DatabaseConnection:
       def __init__(self):
           self._pool = None
       
       async def initialize(self):
           self._pool = await asyncpg.create_pool(config.DATABASE_URL)
       
       async def execute(self, query: str, *args):
           async with self._pool.acquire() as conn:
               return await conn.execute(query, *args)
       
       async def fetch(self, query: str, *args):
           async with self._pool.acquire() as conn:
               return await conn.fetch(query, *args)
   ```

4. **Update all Supabase calls** to use new database adapter

5. **Create database schema** using SQL migrations

### For SQLite:

1. **Install dependencies:**
   ```bash
   uv add aiosqlite sqlalchemy[asyncio]
   ```

2. **Update DATABASE_URL:**
   ```bash
   DATABASE_URL=sqlite+aiosqlite:///app/data/suna.db
   ```

3. **Use SQLAlchemy with async SQLite driver**

## Authentication Alternatives

Since Supabase provides authentication, you'll need an alternative:

### 1. FastAPI-Users (Recommended)
- Full-featured authentication system
- Supports multiple databases
- JWT tokens, OAuth, etc.

### 2. Custom JWT Implementation
- More control, less features
- Implement login/register endpoints
- Handle password hashing and JWT tokens

### 3. External Auth Services
- Auth0, Firebase Auth, AWS Cognito
- Keep authentication separate from database

## Recommendation

For Railway deployment, I recommend:

1. **Start with Railway PostgreSQL** - easiest migration path
2. **Use FastAPI-Users for authentication** - feature-complete
3. **Keep Redis for caching** - works well with any database

This gives you a fully managed solution without external dependencies like Supabase.

## Need Help?

The migration requires significant code changes. Consider:
1. Starting with SQLite for development/testing
2. Hiring a developer familiar with FastAPI and PostgreSQL
3. Using the existing Supabase setup initially and migrating later
