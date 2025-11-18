-- Debug admin user "harsh sharma" issue

-- Check if user exists with different variations
SELECT 'EXACT MATCH' as search_type, id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE username = 'harsh sharma'

UNION ALL

SELECT 'CASE INSENSITIVE' as search_type, id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE LOWER(username) = 'harsh sharma'

UNION ALL

SELECT 'FIRST NAME MATCH' as search_type, id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE LOWER(first_name) = 'harsh'

UNION ALL

SELECT 'FULL NAME MATCH' as search_type, id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE LOWER(first_name || ' ' || last_name) = 'harsh sharma'

UNION ALL

SELECT 'ADMIN ROLE USERS' as search_type, id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE role IN ('admin', 'org_admin', 'super_admin')

UNION ALL

SELECT 'USERNAME CONTAINS HARSH' as search_type, id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE username ILIKE '%harsh%'

UNION ALL

SELECT 'EMAIL CONTAINS HARSH' as search_type, id, username, email, first_name, last_name, role, organization_id, is_active
FROM users
WHERE email ILIKE '%harsh%';

-- Check organization context
SELECT 'ORGANIZATION CHECK' as info;
SELECT org_id, org_code, org_name FROM organizations;

-- Check if user has organization_id set
SELECT 'USERS WITHOUT ORGANIZATION' as info;
SELECT id, username, email, role, organization_id
FROM users
WHERE organization_id IS NULL
LIMIT 10;
