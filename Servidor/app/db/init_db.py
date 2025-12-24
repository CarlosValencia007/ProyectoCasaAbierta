"""
Smart Classroom AI - Database Initialization Script
SQL scripts to setup PostgreSQL + pgvector schema
"""

# SQL script to create tables and functions
INIT_SQL = """
-- ==============================================================================
-- Smart Classroom AI - Database Setup Script
-- PostgreSQL + pgvector Extension
-- ==============================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ==============================================================================
-- TABLE: students
-- ==============================================================================
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    face_embedding vector(128) NOT NULL,
    enrolled_at TIMESTAMP DEFAULT NOW() NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    extra_data TEXT,
    
    CONSTRAINT students_student_id_key UNIQUE (student_id)
);

-- Create index for vector similarity search (IVFFlat)
CREATE INDEX IF NOT EXISTS ix_students_face_embedding 
ON students USING ivfflat (face_embedding vector_l2_ops)
WITH (lists = 100);

-- Regular indexes
CREATE INDEX IF NOT EXISTS ix_students_student_id ON students(student_id);
CREATE INDEX IF NOT EXISTS ix_students_is_active ON students(is_active);

-- ==============================================================================
-- TABLE: attendance
-- ==============================================================================
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    class_id VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'present',
    timestamp TIMESTAMP DEFAULT NOW() NOT NULL,
    confidence FLOAT,
    match_distance FLOAT,
    
    CONSTRAINT attendance_status_check CHECK (status IN ('present', 'absent', 'late', 'excused'))
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS ix_attendance_student_id ON attendance(student_id);
CREATE INDEX IF NOT EXISTS ix_attendance_class_id ON attendance(class_id);
CREATE INDEX IF NOT EXISTS ix_attendance_timestamp ON attendance(timestamp);
CREATE INDEX IF NOT EXISTS ix_attendance_class_timestamp ON attendance(class_id, timestamp);
CREATE INDEX IF NOT EXISTS ix_attendance_student_class ON attendance(student_id, class_id);

-- ==============================================================================
-- TABLE: emotion_events
-- ==============================================================================
CREATE TABLE IF NOT EXISTS emotion_events (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    class_id VARCHAR(100) NOT NULL,
    dominant_emotion VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    emotion_scores TEXT,
    detected_at TIMESTAMP DEFAULT NOW() NOT NULL,
    
    CONSTRAINT emotion_type_check CHECK (
        dominant_emotion IN ('happy', 'sad', 'angry', 'fear', 'surprise', 'neutral', 'disgust', 'bored', 'sleepy', 'attentive')
    )
);

-- Indexes
CREATE INDEX IF NOT EXISTS ix_emotion_student_id ON emotion_events(student_id);
CREATE INDEX IF NOT EXISTS ix_emotion_class_id ON emotion_events(class_id);
CREATE INDEX IF NOT EXISTS ix_emotion_detected_at ON emotion_events(detected_at);
CREATE INDEX IF NOT EXISTS ix_emotion_class_timestamp ON emotion_events(class_id, detected_at);
CREATE INDEX IF NOT EXISTS ix_emotion_student_class ON emotion_events(student_id, class_id);

-- ==============================================================================
-- TABLE: class_sessions
-- ==============================================================================
CREATE TABLE IF NOT EXISTS class_sessions (
    id SERIAL PRIMARY KEY,
    class_id VARCHAR(100) UNIQUE NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    instructor VARCHAR(100),
    room VARCHAR(50),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_students INTEGER DEFAULT 0,
    present_count INTEGER DEFAULT 0,
    attendance_rate FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    extra_data TEXT
);

CREATE INDEX IF NOT EXISTS ix_class_sessions_class_id ON class_sessions(class_id);
CREATE INDEX IF NOT EXISTS ix_class_sessions_start_time ON class_sessions(start_time);

-- ==============================================================================
-- RPC FUNCTION: match_students_by_embedding
-- Vector similarity search using pgvector
-- ==============================================================================
CREATE OR REPLACE FUNCTION match_students_by_embedding(
    query_embedding vector(128),
    match_threshold float DEFAULT 0.6,
    match_count int DEFAULT 1
)
RETURNS TABLE (
    student jsonb,
    distance float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        to_jsonb(s.*) - 'face_embedding' as student,
        (s.face_embedding <-> query_embedding)::float as distance
    FROM students s
    WHERE 
        s.is_active = TRUE
        AND (s.face_embedding <-> query_embedding) < match_threshold
    ORDER BY s.face_embedding <-> query_embedding
    LIMIT match_count;
END;
$$;

-- ==============================================================================
-- RPC FUNCTION: get_class_attendance_summary
-- Get attendance statistics for a class
-- ==============================================================================
CREATE OR REPLACE FUNCTION get_class_attendance_summary(
    p_class_id VARCHAR(100)
)
RETURNS TABLE (
    class_id VARCHAR(100),
    total_records BIGINT,
    present_count BIGINT,
    late_count BIGINT,
    absent_count BIGINT,
    attendance_rate FLOAT,
    avg_confidence FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p_class_id as class_id,
        COUNT(*)::BIGINT as total_records,
        COUNT(*) FILTER (WHERE status = 'present')::BIGINT as present_count,
        COUNT(*) FILTER (WHERE status = 'late')::BIGINT as late_count,
        COUNT(*) FILTER (WHERE status = 'absent')::BIGINT as absent_count,
        (COUNT(*) FILTER (WHERE status = 'present')::FLOAT / NULLIF(COUNT(*), 0) * 100) as attendance_rate,
        AVG(confidence) as avg_confidence
    FROM attendance
    WHERE attendance.class_id = p_class_id;
END;
$$;

-- ==============================================================================
-- RPC FUNCTION: get_class_emotion_summary
-- Get emotion distribution for a class
-- ==============================================================================
CREATE OR REPLACE FUNCTION get_class_emotion_summary(
    p_class_id VARCHAR(100)
)
RETURNS TABLE (
    emotion VARCHAR(20),
    count BIGINT,
    percentage FLOAT,
    avg_confidence FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dominant_emotion as emotion,
        COUNT(*)::BIGINT as count,
        (COUNT(*)::FLOAT / (SELECT COUNT(*) FROM emotion_events WHERE class_id = p_class_id) * 100) as percentage,
        AVG(confidence) as avg_confidence
    FROM emotion_events
    WHERE class_id = p_class_id
    GROUP BY dominant_emotion
    ORDER BY count DESC;
END;
$$;

-- ==============================================================================
-- SAMPLE DATA (Optional - Comment out for production)
-- ==============================================================================
-- INSERT INTO students (student_id, name, email, face_embedding) VALUES
-- ('TEST001', 'Test Student', 'test@example.com', array_fill(0.0, ARRAY[128])::vector(128));

-- ==============================================================================
-- GRANTS (Adjust based on your security model)
-- ==============================================================================
-- GRANT SELECT, INSERT, UPDATE ON students TO anon, authenticated;
-- GRANT SELECT, INSERT ON attendance TO anon, authenticated;
-- GRANT SELECT, INSERT ON emotion_events TO anon, authenticated;
-- GRANT EXECUTE ON FUNCTION match_students_by_embedding TO anon, authenticated;

-- ==============================================================================
-- VERIFICATION QUERIES
-- ==============================================================================
-- Check if tables exist:
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Check if pgvector extension is enabled:
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- Test vector similarity search:
-- SELECT * FROM match_students_by_embedding(array_fill(0.0, ARRAY[128])::vector(128), 0.6, 5);

"""

def print_sql():
    """Print the SQL script for manual execution"""
    print("="*80)
    print("SMART CLASSROOM AI - DATABASE SETUP SCRIPT")
    print("="*80)
    print("\nCopy and execute the following SQL in your Supabase SQL Editor:\n")
    print(INIT_SQL)
    print("\n" + "="*80)
    print("SETUP COMPLETE")
    print("="*80)

if __name__ == "__main__":
    print_sql()
