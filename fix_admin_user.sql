-- Fix admin user issues

-- 1. Check current admin users
SELECT id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE role IN ('admin', 'org_admin', 'super_admin');

-- 2. Find harsh sharma user (any variation)
SELECT id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE username ILIKE '%harsh%' OR first_name ILIKE '%harsh%' OR email ILIKE '%harsh%';

-- 3. Create/Update admin user if needed
-- First, get the BHU organization ID
SELECT org_id FROM organizations WHERE org_code = 'BHU';

-- Update existing harsh user to admin (replace ORG_ID_HERE with actual org_id)
UPDATE users
SET role = 'org_admin',
    organization_id = (SELECT org_id FROM organizations WHERE org_code = 'BHU'),
    is_active = true,
    is_staff = true,
    is_superuser = true
WHERE username ILIKE '%harsh%' OR first_name ILIKE '%harsh%';

-- If no harsh user exists, create one
INSERT INTO users (username, email, first_name, last_name, role, organization_id, is_active, is_staff, is_superuser, password)
SELECT 'harshsharma', 'harshsharma@bhu.ac.in', 'Harsh', 'Sharma', 'org_admin',
       (SELECT org_id FROM organizations WHERE org_code = 'BHU'),
       true, true, true, 'pbkdf2_sha256$600000$defaultpassword'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username ILIKE '%harsh%'
);

-- Verify the fix
SELECT 'ADMIN USERS AFTER FIX' as info;
SELECT id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE role IN ('admin', 'org_admin', 'super_admin');
