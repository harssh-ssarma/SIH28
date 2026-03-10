// Unit tests (Vitest) for src/lib/exportUtils.ts
//
// Module under test: frontend/src/lib/exportUtils.ts
//
// Responsibility of source module:
//   Provides exportTimetableAsPdf() and exportTimetableAsExcel() that
//   render the timetable data into downloadable jsPDF and xlsx files.
//
// What these tests verify:
//   - exportTimetableAsExcel() calls xlsx.writeFile with a non-empty workbook
//   - exportTimetableAsExcel() creates one worksheet per department
//   - exportTimetableAsExcel() raises ExportError for empty timetable data
//   - exportTimetableAsPdf() calls jsPDF.save() with the provided filename
//   - filename defaults to "timetable_{date}.pdf" when not specified
//
// Test data strategy:
//   Mock xlsx.writeFile and jsPDF constructor via vi.mock().
//   Build a minimal TimetableData fixture with 2 departments, 4 slots.
//
// Dependencies to mock:
//   xlsx   — vi.mock("xlsx")
//   jspdf  — vi.mock("jspdf")
