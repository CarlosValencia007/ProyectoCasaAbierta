"""
Test script to verify Supabase Storage integration
"""
import base64
import uuid
from app.db.supabase_client import get_supabase
from app.core.config import settings

def test_storage_upload():
    """Test uploading a simple text file to Storage"""
    try:
        client = get_supabase()
        bucket = settings.SUPABASE_STORAGE_BUCKET
        
        print(f"✅ Connected to Supabase")
        print(f"📦 Bucket: {bucket}")
        
        # Create a test image (1x1 red pixel PNG in base64)
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
        image_data = base64.b64decode(test_image_base64)
        
        # Generate filename
        filename = f"test_{uuid.uuid4().hex[:8]}.png"
        file_path = f"students/{filename}"
        
        print(f"📤 Uploading to: {file_path}")
        
        # Upload
        response = client.storage.from_(bucket).upload(
            path=file_path,
            file=image_data,
            file_options={"content-type": "image/png"}
        )
        
        print(f"✅ Upload response: {response}")
        
        # Get public URL
        public_url = client.storage.from_(bucket).get_public_url(file_path)
        print(f"🌐 Public URL: {public_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Supabase Storage Integration\n")
    success = test_storage_upload()
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
