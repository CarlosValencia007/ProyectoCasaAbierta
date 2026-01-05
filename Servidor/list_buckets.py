"""
List all available Storage buckets in Supabase
"""
from app.db.supabase_client import get_supabase

def list_buckets():
    """List all storage buckets"""
    try:
        client = get_supabase()
        
        print("📦 Listando buckets disponibles en Supabase Storage:\n")
        
        # List all buckets
        buckets = client.storage.list_buckets()
        
        if not buckets:
            print("⚠️  No se encontraron buckets")
            print("\n💡 Debes crear el bucket 'face-pictures' en Supabase Dashboard:")
            print("   1. Ve a Storage en el menú lateral")
            print("   2. Click en 'New bucket'")
            print("   3. Nombre: face-pictures")
            print("   4. Public: ✅ (marcado)")
            print("   5. Click 'Create bucket'")
            return
        
        print(f"Total de buckets: {len(buckets)}\n")
        
        for bucket in buckets:
            print(f"📦 Bucket ID: {bucket.id}")
            print(f"   Nombre: {bucket.name}")
            print(f"   Público: {'✅ Sí' if bucket.public else '❌ No'}")
            print(f"   Creado: {bucket.created_at}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_buckets()
