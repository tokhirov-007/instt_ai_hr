-- Add columns to store candidate details snapshot per session
ALTER TABLE interview_sessions ADD COLUMN candidate_name VARCHAR;
ALTER TABLE interview_sessions ADD COLUMN candidate_phone VARCHAR;
ALTER TABLE interview_sessions ADD COLUMN candidate_email VARCHAR;

-- Update existing records to copy current candidate details from candidates table
UPDATE interview_sessions
SET 
    candidate_name = (SELECT name FROM candidates WHERE candidates.id = interview_sessions.candidate_id),
    candidate_phone = (SELECT phone FROM candidates WHERE candidates.id = interview_sessions.candidate_id),
    candidate_email = (SELECT email FROM candidates WHERE candidates.id = interview_sessions.candidate_id);
