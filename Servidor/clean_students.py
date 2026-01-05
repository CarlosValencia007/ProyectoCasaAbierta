"""
Delete all students and restart fresh
"""
import asyncio
from app.db.supabase_client import get_supabase

async def clean_students():
    """Delete all students"""
    try:
        client = get_supabase()
        
        # Delete all students
        result = client.table('students').delete().neq('id', 0).execute()
        
        print(f"Se eliminaron los estudiantes existentes")
        print("Ahora puedes registrar nuevos estudiantes con embeddings correctos")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(clean_students())
