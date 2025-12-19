"""
Smart Classroom AI - Supabase Client
Wrapper for Supabase connection and operations
"""
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import DatabaseConnectionException


class SupabaseClient:
    """Singleton Supabase client wrapper"""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            try:
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise DatabaseConnectionException(f"Supabase connection failed: {str(e)}")
        
        return cls._instance
    
    @classmethod
    async def test_connection(cls) -> bool:
        """Test database connection"""
        try:
            client = cls.get_client()
            # Simple query to test connection
            response = client.table("students").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False


# Convenience function
def get_supabase() -> Client:
    """Get Supabase client instance"""
    return SupabaseClient.get_client()
