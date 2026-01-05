from app.db.supabase_client import get_supabase

supabase = get_supabase()

print("\n=== VERIFICANDO ESTUDIANTES EN BASE DE DATOS ===\n")

students = supabase.table('students').select('student_id, name, enrolled_at').order('enrolled_at', desc=True).limit(10).execute()

print(f"Total estudiantes (últimos 10): {len(students.data)}\n")

for s in students.data:
    print(f"  ✅ ID: {s['student_id']}, Nombre: {s['name']}, Registrado: {s['enrolled_at'][:19]}")

print("")
