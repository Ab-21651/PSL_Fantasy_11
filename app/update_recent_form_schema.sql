-- Add missing columns to recent_form table
-- Run this in Supabase SQL Editor

ALTER TABLE recent_form
ADD COLUMN IF NOT EXISTS balls_faced INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS fours INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS sixes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS overs_bowled FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS runs_given INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS maidens INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS catches INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS stumpings INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS run_outs INTEGER DEFAULT 0;

-- Verify the changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'recent_form'
ORDER BY ordinal_position;
