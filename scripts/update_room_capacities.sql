-- ================================================================
-- Update Room Capacities for CP-SAT Optimization
-- ================================================================
-- Problem: All 1147 rooms with capacity=60 creates symmetry explosion
-- Solution: Diverse capacities (30-100) to enable constraint pruning
-- 
-- Distribution per 9 rooms per department:
--   - 2 small rooms (30, 40) - for seminars, labs
--   - 5 medium rooms (50, 55, 60, 60, 60) - standard classes
--   - 2 large rooms (80, 100) - big lectures
-- ================================================================

BEGIN;

-- Update room capacities based on room_number pattern
-- Note: room_number is VARCHAR, so we cast to INTEGER
-- If room_number contains non-numeric data, use hashtext() instead
UPDATE room
SET seating_capacity = CASE 
    -- Small rooms (22% of total) - for small classes/labs
    WHEN (CAST(room_number AS INTEGER) % 9) = 1 THEN 30
    WHEN (CAST(room_number AS INTEGER) % 9) = 2 THEN 40
    
    -- Medium rooms (56% of total) - standard classrooms
    WHEN (CAST(room_number AS INTEGER) % 9) = 3 THEN 50
    WHEN (CAST(room_number AS INTEGER) % 9) = 4 THEN 55
    WHEN (CAST(room_number AS INTEGER) % 9) = 5 THEN 60
    WHEN (CAST(room_number AS INTEGER) % 9) = 6 THEN 60
    WHEN (CAST(room_number AS INTEGER) % 9) = 7 THEN 60
    
    -- Large rooms (22% of total) - big lectures
    WHEN (CAST(room_number AS INTEGER) % 9) = 8 THEN 80
    WHEN (CAST(room_number AS INTEGER) % 9) = 0 THEN 100
    
    ELSE 60  -- Fallback (shouldn't happen)
END
WHERE room_number ~ '^[0-9]+$';  -- Only update if room_number is purely numeric

-- Alternative: For non-numeric room_numbers (e.g., 'A101', 'LAB-5'), use hash-based distribution
UPDATE room
SET seating_capacity = CASE 
    WHEN (hashtext(room_number) % 9) = 1 THEN 30
    WHEN (hashtext(room_number) % 9) = 2 THEN 40
    WHEN (hashtext(room_number) % 9) = 3 THEN 50
    WHEN (hashtext(room_number) % 9) = 4 THEN 55
    WHEN (hashtext(room_number) % 9) = 5 THEN 60
    WHEN (hashtext(room_number) % 9) = 6 THEN 60
    WHEN (hashtext(room_number) % 9) = 7 THEN 60
    WHEN (hashtext(room_number) % 9) = 8 THEN 80
    WHEN (hashtext(room_number) % 9) = 0 THEN 100
    ELSE 60
END
WHERE room_number !~ '^[0-9]+$';  -- Only update if room_number is NOT purely numeric

-- Optional: Make labs slightly smaller (realistic constraint)
UPDATE room
SET seating_capacity = seating_capacity - 10
WHERE room_type = 'LABORATORY' 
  AND seating_capacity > 30;

COMMIT;

-- ================================================================
-- Verification Query - Run this to check distribution
-- ================================================================
SELECT 
    seating_capacity,
    room_type,
    COUNT(*) as room_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
FROM room
GROUP BY seating_capacity, room_type
ORDER BY seating_capacity, room_type;

-- ================================================================
-- Expected Results (for ~1147 rooms):
-- Capacity | Type                | Count | Percentage
-- ---------|---------------------|-------|------------
--    20    | LABORATORY          |  ~60  |   5%
--    30    | STANDARD_CLASSROOM  | ~130  |  11%
--    30    | LABORATORY          |  ~60  |   5%
--    40    | STANDARD_CLASSROOM  | ~130  |  11%
--    40    | LABORATORY          |  ~60  |   5%
--    45    | LABORATORY          |  ~60  |   5%
--    50    | STANDARD_CLASSROOM  | ~130  |  11%
--    50    | LABORATORY          |  ~60  |   5%
--    55    | STANDARD_CLASSROOM  | ~130  |  11%
--    60    | STANDARD_CLASSROOM  | ~390  |  34%
--    70    | LABORATORY          |  ~60  |   5%
--    80    | STANDARD_CLASSROOM  | ~130  |  11%
--    90    | LABORATORY          |  ~60  |   5%
--   100    | STANDARD_CLASSROOM  | ~130  |  11%
-- ================================================================
