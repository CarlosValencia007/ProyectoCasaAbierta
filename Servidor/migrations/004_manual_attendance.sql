-- Migration: Add period and verification_method columns to attendance table
-- For manual attendance registration with support for multiple class periods

-- Add period column (defaults to 1 for existing records)
ALTER TABLE attendance 
ADD COLUMN IF NOT EXISTS period INTEGER DEFAULT 1;

-- Add verification_method column to track how attendance was taken
ALTER TABLE attendance 
ADD COLUMN IF NOT EXISTS verification_method VARCHAR(20) DEFAULT 'facial';

-- Add updated_at column for tracking manual updates
ALTER TABLE attendance 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

-- Create index for faster period-based queries
CREATE INDEX IF NOT EXISTS ix_attendance_period ON attendance(period);

-- Create unique constraint to prevent duplicate attendance for same student/class/period
-- Note: This may fail if duplicates already exist. Run cleanup first if needed.
-- CREATE UNIQUE INDEX IF NOT EXISTS ix_attendance_unique ON attendance(student_id, class_id, period);

-- Comment: verification_method values: 'facial', 'qr', 'manual'
