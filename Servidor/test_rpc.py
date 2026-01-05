from app.db.supabase_client import get_supabase
import numpy as np

supabase = get_supabase()

print("\n=== PROBANDO FUNCIÓN RPC match_students_by_embedding ===\n")

# Obtener el estudiante registrado
students = supabase.table('students').select('student_id, name, face_embedding').limit(1).execute()

if not students.data:
    print("❌ No hay estudiantes en la BD")
    exit(1)

student = students.data[0]
print(f"Estudiante encontrado: {student['student_id']} - {student['name']}")
print(f"Embedding dimension: {len(student['face_embedding'])}")
print("")

# Usar el MISMO embedding para buscar (debería encontrarse a sí mismo con distance=0)
print("Probando RPC con el MISMO embedding del estudiante...")
try:
    result = supabase.rpc(
        'match_students_by_embedding',
        {
            'query_embedding': student['face_embedding'],
            'match_threshold': 0.9,
            'match_count': 5
        }
    ).execute()
    
    print(f"✅ RPC ejecutado exitosamente")
    print(f"Resultados: {len(result.data)}")
    print("")
    
    for i, item in enumerate(result.data):
        print(f"  Match #{i+1}:")
        print(f"    Student ID: {item.get('student', {}).get('student_id', 'N/A')}")
        print(f"    Distance: {item.get('distance', 'N/A')}")
        print("")
        
except Exception as e:
    print(f"❌ ERROR ejecutando RPC: {str(e)}")
    print("")
