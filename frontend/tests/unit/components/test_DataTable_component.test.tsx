// Unit tests (Vitest + React Testing Library) for components/shared/DataTable.tsx
//
// Component under test: frontend/src/components/shared/DataTable.tsx
//
// Responsibility of source component:
//   Generic data table with column definitions, search filter, column visibility
//   toggle, pagination, and row selection — used by every admin resource page.
//
// What these tests verify:
//   - renders the correct number of data rows from the provided data prop
//   - renders column headers matching the columns prop definition
//   - filtering by search input hides non-matching rows
//   - clicking a column header triggers onSortChange with correct field
//   - pagination controls are hidden when total rows <= pageSize
//   - pagination Next button advances the page and shows new rows
//   - row click triggers onRowClick callback with the correct row data
//   - empty data state renders the "No results" placeholder
//
// Test data strategy:
//   Build a simple data fixture: 15 rows of { id, name, status }.
//   Use screen.getByRole and userEvent from @testing-library/user-event.
//
// Dependencies to mock:
//   None — pure component with injected data.
