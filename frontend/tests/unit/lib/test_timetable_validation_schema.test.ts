// Unit tests (Vitest) for src/lib/validations/timetable.ts
//
// Module under test: frontend/src/lib/validations/timetable.ts
//
// Responsibility of source module:
//   Zod schema for the timetable generation form: department, semester,
//   constraint weights, and slot configuration — validated before submission.
//
// What these tests verify:
//   - timetableGenerationSchema accepts a fully-populated valid payload
//   - missing department_id raises "Department is required"
//   - constraint_weights object must have all required keys
//   - constraint_weights values must sum to 1.0 (cross-field validator)
//   - max_solve_time_seconds must be between 30 and 3600
//   - slot_duration_minutes must be one of the allowed values [45, 50, 60, 90]
//
// Test data strategy:
//   schema.safeParse() with constructed objects.
//   test.each for boundary values of numeric fields.
