// Vitest unit tests for src/lib/api/timetable.ts
//
// Module under test: frontend/src/lib/api/timetable.ts
//
// Responsibility of source module:
//   Typed API functions for timetable resources: submitting generation jobs,
//   polling job status, fetching timetable variants, and publishing a variant.
//
// What these tests verify:
//   - submitGenerationJob() calls POST /api/timetables/generate with correct body
//   - submitGenerationJob() returns the job_id from the response
//   - getJobStatus(jobId) calls GET /api/timetables/{jobId}/status
//   - getJobStatus() returns a typed JobStatus object
//   - getTimetableVariants(jobId) calls GET /api/timetables/{jobId}/variants
//   - publishVariant(jobId, variantId) calls PATCH with the correct body
//   - each function throws ApiError on non-2xx response
//
// Key functions to test:
//   submitGenerationJob(payload) -> Promise<{ job_id: string }>
//   getJobStatus(jobId) -> Promise<JobStatus>
//   getTimetableVariants(jobId) -> Promise<TimetableVariant[]>
//   publishVariant(jobId, variantId) -> Promise<void>
//
// Test data strategy:
//   Use MSW (Mock Service Worker) with vitest — intercept fetch at the
//   network level to test the full serialisation/deserialisation path.
//
// Dependencies to mock:
//   global fetch — MSW server (setupServer from msw/node)
