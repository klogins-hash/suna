"""
PostgreSQL database connection management for Suna using asyncpg.
Replaces Supabase with Railway PostgreSQL.
"""

import asyncpg
import asyncio
from typing import Optional, Dict, Any, List
from utils.logger import logger
from utils.config import config
import threading
import json
from datetime import datetime
import uuid

class DatabaseConnection:
    """Thread-safe singleton database connection manager using PostgreSQL."""
    
    _instance: Optional['DatabaseConnection'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
                    cls._instance._pool = None
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            self._pool = None
            self._initialized = True

    async def initialize(self):
        """Initialize the database connection pool."""
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(
                    config.DATABASE_URL,
                    min_size=1,
                    max_size=20,
                    command_timeout=60
                )
                logger.info("Database connection pool initialized")
                
                # Run initial setup
                await self._ensure_tables_exist()
                
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                raise

    async def _ensure_tables_exist(self):
        """Create basic tables if they don't exist."""
        async with self._pool.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE,
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            ''')
            
            # Threads table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS threads (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(500),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            ''')
            
            # Messages table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    thread_id UUID REFERENCES threads(id) ON DELETE CASCADE,
                    role VARCHAR(50) NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            ''')
            
            # Agent configurations table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS agent_configs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    config JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

    async def execute(self, query: str, *args) -> str:
        """Execute a query and return the result."""
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch multiple rows."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch a single row."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value."""
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    # Compatibility methods to match Supabase interface
    async def table(self, table_name: str):
        """Return a table interface for compatibility."""
        return PostgreSQLTable(self, table_name)

    async def close(self):
        """Close the database connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

class PostgreSQLTable:
    """Table interface to maintain compatibility with Supabase-style queries."""
    
    def __init__(self, db: DatabaseConnection, table_name: str):
        self.db = db
        self.table_name = table_name
        self._select_columns = "*"
        self._where_conditions = []
        self._order_by = None
        self._limit_count = None

    def select(self, columns: str = "*"):
        """Select specific columns."""
        self._select_columns = columns
        return self

    def eq(self, column: str, value: Any):
        """Add equality condition."""
        self._where_conditions.append(f"{column} = ${len(self._where_conditions) + 1}")
        self._values = getattr(self, '_values', [])
        self._values.append(value)
        return self

    def order(self, column: str, desc: bool = False):
        """Add order by clause."""
        direction = "DESC" if desc else "ASC"
        self._order_by = f"ORDER BY {column} {direction}"
        return self

    def limit(self, count: int):
        """Add limit clause."""
        self._limit_count = count
        return self

    async def execute(self):
        """Execute the built query."""
        query_parts = [f"SELECT {self._select_columns} FROM {self.table_name}"]
        
        if self._where_conditions:
            query_parts.append(f"WHERE {' AND '.join(self._where_conditions)}")
        
        if self._order_by:
            query_parts.append(self._order_by)
            
        if self._limit_count:
            query_parts.append(f"LIMIT {self._limit_count}")
        
        query = " ".join(query_parts)
        values = getattr(self, '_values', [])
        
        result = await self.db.fetch(query, *values)
        return {"data": result, "error": None}

    async def insert(self, data: Dict[str, Any]):
        """Insert data into the table."""
        columns = list(data.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        values = list(data.values())
        
        query = f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """
        
        try:
            result = await self.db.fetchrow(query, *values)
            return {"data": result, "error": None}
        except Exception as e:
            logger.error(f"Insert error: {e}")
            return {"data": None, "error": str(e)}

    async def update(self, data: Dict[str, Any]):
        """Update data in the table."""
        if not self._where_conditions:
            return {"data": None, "error": "Update requires WHERE conditions"}
        
        set_clauses = []
        values = []
        
        for i, (column, value) in enumerate(data.items()):
            set_clauses.append(f"{column} = ${len(values) + 1}")
            values.append(value)
        
        # Add WHERE condition values
        where_values = getattr(self, '_values', [])
        values.extend(where_values)
        
        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE {' AND '.join(self._where_conditions)}
            RETURNING *
        """
        
        try:
            result = await self.db.fetchrow(query, *values)
            return {"data": result, "error": None}
        except Exception as e:
            logger.error(f"Update error: {e}")
            return {"data": None, "error": str(e)}

    async def delete(self):
        """Delete data from the table."""
        if not self._where_conditions:
            return {"data": None, "error": "Delete requires WHERE conditions"}
        
        values = getattr(self, '_values', [])
        query = f"""
            DELETE FROM {self.table_name}
            WHERE {' AND '.join(self._where_conditions)}
            RETURNING *
        """
        
        try:
            result = await self.db.fetch(query, *values)
            return {"data": result, "error": None}
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return {"data": None, "error": str(e)}

# Global database instance
db = DatabaseConnection()
