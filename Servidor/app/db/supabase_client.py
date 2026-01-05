"""
Smart Classroom AI - Supabase Client
Wrapper for Supabase connection and operations
"""
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import DatabaseConnectionException


# ============================================================================
# VALIDACIÓN DE CREDENCIALES (Ejecuta al importar el módulo)
# ============================================================================

# Validamos que las URLs existan para evitar errores silenciosos
if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    raise ValueError("❌ Faltan las variables SUPABASE_URL o SUPABASE_KEY en el archivo .env")

logger.info(f"✅ Variables de Supabase detectadas: {settings.SUPABASE_URL}")


# ============================================================================
# CLIENTE SINGLETON
# ============================================================================

class SupabaseClient:
    """Singleton Supabase client wrapper"""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            try:
                # Use service_role key for admin operations (Storage, etc.)
                # Falls back to regular key if service key not available
                api_key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
                
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=api_key
                )
                logger.info("✅ Conexión a Supabase inicializada correctamente")
            except Exception as e:
                logger.error(f"❌ Error al inicializar cliente Supabase: {str(e)}")
                raise DatabaseConnectionException(f"Supabase connection failed: {str(e)}")
        
        return cls._instance
    
    @classmethod
    async def test_connection(cls) -> bool:
        """Test database connection"""
        try:
            client = cls.get_client()
            # Simple query to test connection (usando el esquema correcto)
            response = client.table("students").select("id").limit(1).execute()
            logger.info("✅ Test de conexión a Supabase exitoso")
            return True
        except Exception as e:
            logger.error(f"❌ Test de conexión a Supabase falló: {str(e)}")
            return False


# ============================================================================
# FUNCIÓN DE CONVENIENCIA (Instancia única global)
# ============================================================================

def get_supabase() -> Client:
    """
    Get Supabase client instance (Singleton)
    
    Esta es la función que debes usar en tus endpoints:
    
    Example:
        from app.db.supabase_client import get_supabase
        
        supabase = get_supabase()
        response = supabase.table("students").insert(data).execute()
    """
    return SupabaseClient.get_client()


# ============================================================================
# INSTANCIA GLOBAL (Opcional - para importación directa)
# ============================================================================

# Creamos la instancia única del cliente al importar el módulo
# Esto asegura que el cliente esté listo desde el inicio
supabase: Client = SupabaseClient.get_client()

logger.info(f"✅ Cliente Supabase global inicializado y listo para usar")