-- ============================================================================
-- Add photo_url column to students table
-- ============================================================================

-- Add column to store photo URL from Supabase Storage
ALTER TABLE public.students 
ADD COLUMN IF NOT EXISTS photo_url TEXT;

-- Add comment for documentation
COMMENT ON COLUMN public.students.photo_url IS 'Public URL of student photo stored in Supabase Storage';

-- Create index for faster queries (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_students_photo_url ON public.students(photo_url);
