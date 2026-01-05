"""
Check registered students in database
"""
import asyncio
from app.db.crud import StudentCRUD

async def check_students():
    """List all registered students"""
    try:
        crud = StudentCRUD()
        
        # Get all students
        students = await crud.list_all()
        
        print(f"Total de estudiantes registrados: {len(students)}\n")
        
        if not students:
            print("NO HAY ESTUDIANTES REGISTRADOS")
            print("\nDebes registrar al menos un estudiante primero:")
            print("   1. Ve a http://localhost:5500/test_frontend.html")
            print("   2. Seccion 1: Enrollment")
            print("   3. Registra un estudiante con foto")
            return
        
        print("Lista de estudiantes:")
        print("=" * 80)
        for student in students:
            print(f"ID: {student['student_id']}")
            print(f"Nombre: {student['name']}")
            print(f"Email: {student.get('email', 'N/A')}")
            print(f"Embedding dimension: {len(student['face_embedding']) if student.get('face_embedding') else 0}")
            print(f"Photo URL: {student.get('photo_url', 'N/A')}")
            print(f"Enrolled: {student.get('enrolled_at', 'N/A')}")
            print("-" * 80)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_students())
