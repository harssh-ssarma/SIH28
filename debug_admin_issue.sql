-- Debug admin user visibility issue

-- Check all users with admin roles
SELECT id, username, email, first_name, last_name, role, organization_id, is_active, is_staff, is_superuser
FROM users
WHERE role IN ('admin', 'org_admin', 'super_admin');

-- Check if harsh user exists but with wrong role
SELECT id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE username ILIKE '%harsh%' OR first_name ILIKE '%harsh%';

-- Check organization assignment
SELECT u.id, u.username, u.role, u.organization_id, o.org_code, o.org_name
FROM users u
LEFT JOIN organizations o ON u.organization_id = o.org_id
WHERE u.role IN ('admin', 'org_admin', 'super_admin');

-- Fix: Update harsh user to admin role
UPDATE users
SET role = 'org_admin',
    is_active = true,
    is_staff = true
WHERE username ILIKE '%harsh%' OR first_name ILIKE '%harsh%';

-- Verify fix
SELECT id, username, email, role, organization_id, is_active
FROM users
WHERE role IN ('admin', 'org_admin', 'super_admin');
