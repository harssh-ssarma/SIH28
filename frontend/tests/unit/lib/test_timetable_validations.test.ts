// Vitest unit tests for src/lib/validations/timetable.ts
//
// Module under test: frontend/src/lib/validations/timetable.ts
//
// Responsibility of source module:
//   Zod schemas for timetable generation form validation:
//   TimetableGenerationFormSchema, ConstraintWeightsSchema —
//   used by react-hook-form to validate the admin generation wizard.
//
// What these tests verify:
//   - valid TimetableGenerationFormSchema payload passes .parse() without error
//   - missing department_id field fails with a path=["department_id"] error
//   - semester must be one of the allowed enum values
//   - max_solve_time_seconds must be a positive integer
//   - constraint_weights must sum to exactly 1.0 (cross-field refinement)
//   - constraint_weights with negative values fail validation
//
// Key schemas to test:
//   TimetableGenerationFormSchema
//   ConstraintWeightsSchema
//
// Test data strategy:
//   Build valid base objects; mutate one field per test.
//   Use schema.safeParse() to get structured ZodError output.
//
// Dependencies to mock:
//   None — pure Zod schema validation.
