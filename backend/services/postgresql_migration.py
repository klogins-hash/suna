"""
Migration helper to replace Supabase calls with PostgreSQL equivalents.
"""

from services.database import db
from services.auth import fastapi_users, auth_backend
from fastapi import APIRouter, Depends
from utils.logger import logger

# Create auth router
auth_router = APIRouter()

# Add FastAPI-Users routes
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
auth_router.include_router(
    fastapi_users.get_register_router(), prefix="/auth", tags=["auth"]
)
auth_router.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)
auth_router.include_router(
    fastapi_users.get_verify_router(), prefix="/auth", tags=["auth"]
)
auth_router.include_router(
    fastapi_users.get_users_router(), prefix="/users", tags=["users"]
)

class SupabaseMigrationHelper:
    """Helper class to migrate from Supabase to PostgreSQL calls."""
    
    @staticmethod
    async def migrate_table_calls():
        """Replace Supabase table calls with PostgreSQL equivalents."""
        
        # Example migration patterns:
        
        # OLD: result = await supabase.table("users").select("*").execute()
        # NEW: result = await db.fetch("SELECT * FROM users")
        
        # OLD: result = await supabase.table("users").insert(data).execute()
        # NEW: result = await db.table("users").insert(data)
        
        # OLD: result = await supabase.table("users").update(data).eq("id", user_id).execute()
        # NEW: result = await db.table("users").eq("id", user_id).update(data)
        
        logger.info("Supabase to PostgreSQL migration patterns ready")
        
    @staticmethod
    def get_migration_patterns():
        """Return common migration patterns."""
        return {
            "select_all": {
                "old": "await supabase.table('table_name').select('*').execute()",
                "new": "await db.fetch('SELECT * FROM table_name')"
            },
            "select_with_filter": {
                "old": "await supabase.table('table_name').select('*').eq('column', value).execute()",
                "new": "await db.table('table_name').eq('column', value).execute()"
            },
            "insert": {
                "old": "await supabase.table('table_name').insert(data).execute()",
                "new": "await db.table('table_name').insert(data)"
            },
            "update": {
                "old": "await supabase.table('table_name').update(data).eq('id', id).execute()",
                "new": "await db.table('table_name').eq('id', id).update(data)"
            },
            "delete": {
                "old": "await supabase.table('table_name').delete().eq('id', id).execute()",
                "new": "await db.table('table_name').eq('id', id).delete()"
            }
        }
