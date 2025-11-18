"""
PostgreSQL Row-Level Security (RLS) Setup
ENTERPRISE PATTERN: Multi-Tenant Data Isolation

This module provides SQL migrations and management commands to enable
Row-Level Security for multi-tenant isolation in PostgreSQL.

USAGE:
1. Run: python manage.py enable_rls
2. All queries automatically scoped to current organization
3. Organizations cannot see each other's data
"""

RLS_MIGRATION_SQL = """
-- ============================================================================
-- ENABLE ROW-LEVEL SECURITY FOR MULTI-TENANT TABLES
-- ============================================================================

-- Step 1: Enable RLS on all tenant-scoped tables
ALTER TABLE academics_department ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_batch ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_course ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_faculty ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_room ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_timeslot ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_timetableworkflow ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_generationjob ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_timetablevariant ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_timetableentry ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_approvalstep ENABLE ROW LEVEL SECURITY;
ALTER TABLE academics_conflictlog ENABLE ROW LEVEL SECURITY;

-- Step 2: Create policies for SELECT (read operations)
CREATE POLICY tenant_isolation_select ON academics_department
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_batch
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_course
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_faculty
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_room
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_timeslot
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_timetableworkflow
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_generationjob
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_timetablevariant
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_timetableentry
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_approvalstep
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_select ON academics_conflictlog
    FOR SELECT
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

-- Step 3: Create policies for INSERT (create operations)
CREATE POLICY tenant_isolation_insert ON academics_department
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_batch
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_course
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_faculty
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_room
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_timeslot
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_timetableworkflow
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_generationjob
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_timetablevariant
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_timetableentry
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_approvalstep
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_insert ON academics_conflictlog
    FOR INSERT
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

-- Step 4: Create policies for UPDATE (modify operations)
CREATE POLICY tenant_isolation_update ON academics_department
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_batch
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_course
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_faculty
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_room
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_timeslot
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_timetableworkflow
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_generationjob
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_timetablevariant
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_timetableentry
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_approvalstep
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_update ON academics_conflictlog
    FOR UPDATE
    USING (organization_id = current_setting('app.current_organization_id')::UUID)
    WITH CHECK (organization_id = current_setting('app.current_organization_id')::UUID);

-- Step 5: Create policies for DELETE (remove operations)
CREATE POLICY tenant_isolation_delete ON academics_department
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_batch
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_course
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_faculty
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_room
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_timeslot
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_timetableworkflow
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_generationjob
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_timetablevariant
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_timetableentry
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_approvalstep
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY tenant_isolation_delete ON academics_conflictlog
    FOR DELETE
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

-- ============================================================================
-- BYPASS RLS FOR SUPERUSERS (admin access)
-- ============================================================================

-- Allow Django admin to see all data (bypass RLS)
ALTER TABLE academics_department FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_batch FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_course FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_faculty FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_room FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_timeslot FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_timetableworkflow FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_generationjob FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_timetablevariant FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_timetableentry FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_approvalstep FORCE ROW LEVEL SECURITY;
ALTER TABLE academics_conflictlog FORCE ROW LEVEL SECURITY;

COMMENT ON TABLE academics_department IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_batch IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_course IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_faculty IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_room IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_timeslot IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_timetableworkflow IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_generationjob IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_timetablevariant IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_timetableentry IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_approvalstep IS 'RLS enabled for multi-tenant isolation';
COMMENT ON TABLE academics_conflictlog IS 'RLS enabled for multi-tenant isolation';
"""


RLS_DISABLE_SQL = """
-- Disable Row-Level Security (for rollback)
ALTER TABLE academics_department DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_batch DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_course DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_faculty DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_room DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_timeslot DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_timetableworkflow DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_generationjob DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_timetablevariant DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_timetableentry DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_approvalstep DISABLE ROW LEVEL SECURITY;
ALTER TABLE academics_conflictlog DISABLE ROW LEVEL SECURITY;

-- Drop all policies
DROP POLICY IF EXISTS tenant_isolation_select ON academics_department;
DROP POLICY IF EXISTS tenant_isolation_insert ON academics_department;
DROP POLICY IF EXISTS tenant_isolation_update ON academics_department;
DROP POLICY IF EXISTS tenant_isolation_delete ON academics_department;

-- (Repeat for all tables...)
"""
