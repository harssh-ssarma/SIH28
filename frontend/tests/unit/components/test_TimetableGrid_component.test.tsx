// Unit tests (Vitest + React Testing Library) for components/shared/TimetableGrid.tsx
//
// Component under test: frontend/src/components/shared/TimetableGrid.tsx
//
// Responsibility of source component:
//   Renders a weekly timetable as an HTML grid where columns are days (Mon–Sat)
//   and rows are time slots — each cell shows the course code, room, and faculty.
//
// What these tests verify:
//   - renders 6 day column headers (Monday through Saturday)
//   - renders the correct number of time slot rows
//   - a populated slot cell shows course code, room number, and faculty name
//   - an empty slot cell renders an empty cell (no error)
//   - clicking a cell triggers onSlotClick with the slot data
//   - component renders without errors for an all-empty timetable
//   - accessibility: grid role is "grid", cells have role="gridcell"
//
// Test data strategy:
//   Build a TimetableData fixture with 3 populated slots and 2 empty slots.
//   Use screen.getByRole("gridcell") assertions.
//
// Dependencies to mock:
//   None.
