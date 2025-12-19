"""
Smart Classroom AI - Database Initialization Script
Creates tables with pgvector extension and similarity search function
"""

SQL_CREATE_TABLES = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Students table with facial embeddings
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    face_embedding vector(128) NOT NULL,  -- 128-dim for Facenet
    enrolled_at TIMESTAMP DEFAULT NOW() NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    metadata TEXT
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS ix_students_face_embedding 
ON students USING ivfflat (face_embedding vector_l2_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS ix_students_student_id ON students(student_id);

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    class_id VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'present' NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW() NOT NULL,
    confidence FLOAT,
    match_distance FLOAT
);

CREATE INDEX IF NOT EXISTS ix_attendance_class_timestamp ON attendance(class_id, timestamp);
CREATE INDEX IF NOT EXISTS ix_attendance_student_class ON attendance(student_id, class_id);

-- Emotion events table
CREATE TABLE IF NOT EXISTS emotion_events (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    class_id VARCHAR(100) NOT NULL,
    dominant_emotion VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    emotion_scores TEXT,
    detected_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_emotion_class_timestamp ON emotion_events(class_id, detected_at);
CREATE INDEX IF NOT EXISTS ix_emotion_student_class ON emotion_events(student_id, class_id);

-- Class sessions table
CREATE TABLE IF NOT EXISTS class_sessions (
    id SERIAL PRIMARY KEY,
    class_id VARCHAR(100) UNIQUE NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    instructor VARCHAR(100),
    room VARCHAR(50),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_students INT DEFAULT 0,
    present_count INT DEFAULT 0,
    attendance_rate FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS ix_class_sessions_class_id ON class_sessions(class_id);

-- RPC Function for vector similarity search
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
        to_jsonb(s.*) as student,
        (s.face_embedding <-> query_embedding)::float as distance
    FROM students s
    WHERE s.is_active = true
        AND (s.face_embedding <-> query_embedding) < match_threshold
    ORDER BY s.face_embedding <-> query_embedding
    LIMIT match_count;
END;
$$;

-- RPC Function for batch attendance analysis
CREATE OR REPLACE FUNCTION get_class_attendance_summary(
    p_class_id varchar(100)
)
RETURNS TABLE (
    total_records bigint,
    present_count bigint,
    late_count bigint,
    average_confidence float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_records,
        COUNT(*) FILTER (WHERE status = 'present') as present_count,
        COUNT(*) FILTER (WHERE status = 'late') as late_count,
        AVG(confidence)::float as average_confidence
    FROM attendance
    WHERE class_id = p_class_id;
END;
$$;

-- RPC Function for emotion analysis summary
CREATE OR REPLACE FUNCTION get_class_emotion_summary(
    p_class_id varchar(100)
)
RETURNS TABLE (
    emotion varchar(20),
    count bigint,
    avg_confidence float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dominant_emotion as emotion,
        COUNT(*) as count,
        AVG(confidence)::float as avg_confidence
    FROM emotion_events
    WHERE class_id = p_class_id
    GROUP BY dominant_emotion
    ORDER BY count DESC;
END;
$$;
"""

# Instructions for manual setup
SETUP_INSTRUCTIONS = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    SUPABASE DATABASE SETUP                               ║
╚══════════════════════════════════════════════════════════════════════════╝

1. Go to your Supabase Project Dashboard
2. Navigate to SQL Editor
3. Copy and paste the SQL_CREATE_TABLES script above
4. Execute the script

OR use Supabase CLI:

    supabase db push

This will create:
✓ pgvector extension
✓ Tables: students, attendance, emotion_events, class_sessions
✓ Indexes for vector similarity search
✓ RPC functions for efficient queries

IMPORTANT: Make sure pgvector extension is enabled in your Supabase project!
"""

if __name__ == "__main__":
    print(SETUP_INSTRUCTIONS)
    print("\n" + "="*80 + "\n")
    print("SQL Script to execute in Supabase SQL Editor:")
    print("="*80)
    print(SQL_CREATE_TABLES)
