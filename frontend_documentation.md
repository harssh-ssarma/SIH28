# Frontend Documentation — Cadence Timetable Platform

> **Framework**: Next.js 14 (App Router) | **Language**: TypeScript | **Styling**: Tailwind CSS v3 + CSS Custom Properties | **State**: React Context + `useState` + `useRef` | **Auth**: HttpOnly Cookie JWT
>
> **Last Updated**: March 2026

---

## Table of Contents

1. [Project Structure Overview](#1-project-structure-overview)
2. [Technology Stack & Dependencies](#2-technology-stack--dependencies)
3. [Root & Config Files](#3-root--config-files)
4. [App Directory — `src/app/`](#4-app-directory--srcapp)
5. [Components Directory — `src/components/`](#5-components-directory--srccomponents)
6. [Context — `src/context/`](#6-context--srccontext)
7. [Hooks — `src/hooks/`](#7-hooks--srchooks)
8. [Lib — `src/lib/`](#8-lib--srclib)
9. [Types — `src/types/`](#9-types--srctypes)
10. [Rendering & Data-Flow Diagram](#10-rendering--data-flow-diagram)
11. [Authentication & Route-Guard Architecture](#11-authentication--route-guard-architecture)
12. [CSS Architecture](#12-css-architecture)

---

## 1. Project Structure Overview

```
frontend/
├── package.json                           # npm scripts + all dependencies
├── next.config.mjs                        # Next.js config (image domains, env)
├── tailwind.config.ts                     # Tailwind with content paths
├── tsconfig.json                          # TypeScript (@/ alias → ./src/)
├── postcss.config.js                      # PostCSS plugins
└── src/
    ├── app/                               # Next.js App Router route segments
    │   ├── globals.css                    ← 1 445 lines — design tokens, all CSS
    │   ├── layout.tsx                     ← 22 lines  — root HTML + Providers
    │   ├── robots.ts                      ← 15 lines  — robots.txt
    │   ├── (auth)/
    │   │   └── login/page.tsx             ← 396 lines — Google-style login
    │   ├── (marketing)/
    │   │   ├── layout.tsx                 ← 45 lines  — Nav + Footer wrapper
    │   │   ├── page.tsx                   ← 238 lines — Home page
    │   │   ├── sitemap.ts                 ← 84 lines  — XML sitemap
    │   │   ├── blog/page.tsx              ← 157 lines
    │   │   ├── company/page.tsx           ← 181 lines
    │   │   ├── contact/page.tsx           ← 116 lines
    │   │   ├── legal/privacy/page.tsx     ← 61 lines
    │   │   ├── legal/terms/page.tsx       ← 65 lines
    │   │   ├── pricing/page.tsx           ← 107 lines
    │   │   └── product/page.tsx           ← 206 lines
    │   ├── admin/
    │   │   ├── layout.tsx                 ← 41 lines  — auth guard + AppShell
    │   │   ├── dashboard/page.tsx         ← 657 lines — recharts dashboard
    │   │   ├── admins/page.tsx            ← 132 lines
    │   │   │   └── components/
    │   │   │       ├── AddEditUserModal.tsx    ← 165 lines
    │   │   │       └── UserDetailPanel.tsx     ← 127 lines
    │   │   ├── faculty/page.tsx           ← 140 lines
    │   │   │   └── components/
    │   │   │       ├── AddEditFacultyModal.tsx ← 218 lines
    │   │   │       └── FacultyDetailPanel.tsx  ← 149 lines
    │   │   ├── students/page.tsx          ← 126 lines
    │   │   │   └── components/
    │   │   │       ├── AddEditStudentModal.tsx ← 215 lines
    │   │   │       └── StudentDetailPanel.tsx  ← 176 lines
    │   │   ├── academic/
    │   │   │   ├── layout.tsx             ← 3 lines   — passthrough
    │   │   │   ├── page.tsx               ← 10 lines  — redirect to /schools
    │   │   │   ├── buildings/page.tsx     ← 98 lines
    │   │   │   │   └── components/AddEditBuildingModal.tsx ← 141 lines
    │   │   │   ├── courses/page.tsx       ← 165 lines
    │   │   │   ├── departments/page.tsx   ← 101 lines
    │   │   │   │   └── components/AddEditDepartmentModal.tsx ← 143 lines
    │   │   │   ├── programs/page.tsx      ← 98 lines
    │   │   │   │   └── components/AddEditProgramModal.tsx ← 161 lines
    │   │   │   ├── rooms/page.tsx         ← 195 lines
    │   │   │   └── schools/page.tsx       ← 100 lines
    │   │   │       └── components/AddEditSchoolModal.tsx ← 115 lines
    │   │   ├── timetables/
    │   │   │   ├── page.tsx               ← 622 lines — list + filter
    │   │   │   ├── loading.tsx            ← 1 line    — Suspense loader
    │   │   │   └── new/page.tsx           ← 218 lines — generation wizard
    │   │   ├── approvals/page.tsx         ← 455 lines — review queue
    │   │   └── logs/page.tsx              ← 191 lines — audit log viewer
    │   ├── faculty/
    │   │   ├── layout.tsx                 ← 33 lines
    │   │   ├── dashboard/page.tsx         ← 327 lines
    │   │   ├── preferences/page.tsx       ← 155 lines
    │   │   └── schedule/page.tsx          ← 220 lines
    │   ├── student/
    │   │   ├── layout.tsx                 ← 26 lines
    │   │   ├── dashboard/page.tsx         ← 850 lines (largest file)
    │   │   └── timetable/page.tsx         ← 250 lines
    │   └── unauthorized/page.tsx          ← 34 lines  — 403 page
    ├── components/
    │   ├── AuthRedirect.tsx               ← 46 lines
    │   ├── ErrorBoundary.tsx              ← 126 lines
    │   ├── FormFields.tsx                 ← 139 lines
    │   ├── LoadingSkeletons.tsx           ← 315 lines
    │   ├── Pagination.tsx                 ← 296 lines
    │   ├── Providers.tsx                  ← 21 lines — provider tree root
    │   ├── Toast.tsx                      ← 199 lines
    │   ├── marketing/                     # Public-site-specific components
    │   │   ├── AnimatedTimetable.tsx      ← 452 lines
    │   │   ├── DemoRequestForm.tsx        ← 209 lines
    │   │   ├── FeatureGrid.tsx            ← 207 lines
    │   │   ├── HeroSection.tsx            ← 138 lines
    │   │   ├── MarketingFooter.tsx        ← 140 lines
    │   │   ├── MarketingNav.tsx           ← 203 lines
    │   │   ├── PricingTable.tsx           ← 240 lines
    │   │   └── SocialProof.tsx            ← 99 lines
    │   ├── shared/                        # Cross-feature reusable components
    │   │   ├── Avatar.tsx                 ← 74 lines
    │   │   ├── ConfirmDeleteDialog.tsx    ← 83 lines
    │   │   ├── DataTable.tsx              ← 942 lines
    │   │   ├── ExportButton.tsx           ← 159 lines
    │   │   ├── PageHeader.tsx             ← 97 lines
    │   │   ├── SearchBar.tsx              ← 48 lines
    │   │   └── TimetableGrid.tsx          ← 273 lines
    │   ├── shell/                         # Application shell (header, sidebar)
    │   │   ├── AppShell.tsx               ← 753 lines
    │   │   ├── AppShellSkeleton.tsx       ← 95 lines
    │   │   ├── Breadcrumb.tsx             ← 204 lines
    │   │   └── ProfileDropdown.tsx        ← 204 lines
    │   ├── timetables/                    # Timetable feature UI
    │   │   ├── CompareGrid.tsx            ← 355 lines
    │   │   ├── DepartmentTree.tsx         ← 120 lines
    │   │   ├── ScoreBar.tsx               ← 66 lines
    │   │   ├── SlotDetailPanel.tsx        ← 150 lines
    │   │   ├── TimetableGridFiltered.tsx  ← 345 lines
    │   │   ├── VariantCard.tsx            ← 198 lines
    │   │   ├── VariantGrid.tsx            ← 196 lines
    │   │   └── VariantStatusBadge.tsx     ← 79 lines
    │   └── ui/                            # Generic atoms
    │       ├── GoogleSpinner.tsx          ← 83 lines
    │       └── NavigationProgress.tsx     ← 241 lines
    ├── context/
    │   └── AuthContext.tsx                ← 132 lines
    ├── hooks/
    │   ├── useProgress.ts                 ← 553 lines
    │   └── useScrollReveal.ts             ← 66 lines
    ├── lib/
    │   ├── api.ts                         ← 606 lines — ApiClient singleton
    │   ├── auth.ts                        ← 91 lines  — cookie token refresh
    │   ├── exportUtils.ts                 ← 299 lines — PDF/Excel/CSV/ICS
    │   ├── utils.ts                       ← 5 lines   — cn() helper
    │   ├── validations.ts                 ← 470 lines — Zod schemas
    │   └── api/
    │       ├── timetable.ts               ← 38 lines
    │       └── timetable-variants.ts      ← 108 lines
    └── types/
        ├── css.d.ts                       ← 12 lines
        ├── index.ts                       ← 13 lines — User interface
        └── timetable.ts                   ← 382 lines — all timetable types
```

---

## 2. Technology Stack & Dependencies

| Category | Package | Version | Purpose |
|---|---|---|---|
| Framework | `next` | 14.0.0 | App Router, SSR/SSG, file-based routing |
| Language | `typescript` | ^5 | Static typing everywhere |
| Styling | `tailwindcss` | ^3.3 | Utility classes + arbitrary value syntax |
| Theme | `next-themes` | ^0.2.1 | Dark/Light mode with `attribute="class"` |
| Forms | `react-hook-form` | ^7.66 | Controlled forms with minimal re-renders |
| Validation | `zod` | ^3.25 | Schema-first runtime + compile-time validation |
| Resolver | `@hookform/resolvers` | ^3.9 | Bridges zod ↔ react-hook-form |
| Icons | `lucide-react` | ^0.292 | Tree-shakeable SVG icon system |
| Radix UI | `@radix-ui/*` | various | Accessible headless: avatar, dropdown, label, select, switch, tabs |
| Charts | `recharts` | ^2.10 | Admin dashboard analytics |
| Real-time | `socket.io-client` | ^4.5 | WebSocket (available; SSE preferred for progress) |
| SWR | `swr` | ^2.2 | Data fetching with cache (installed, partially used) |
| State | `zustand` | ^4.4 | Global state (installed, available) |
| PDF Export | `jspdf` + `html2canvas` | — | DOM screenshot → PDF |
| Excel Export | `xlsx` | — | Workbook generation |
| File Save | `file-saver` | — | Browser file download trigger |
| Calendar Export | (custom ICS) | — | iCalendar format via exportUtils |
| Error Tracking | `@sentry/nextjs` | ^7.88 | Production error monitoring |
| HTTP | native `fetch` | — | `credentials:'include'` for HttpOnly cookies |

---

## 3. Root & Config Files

### `frontend/package.json` — 61 lines
- **Scripts**: `dev` (`next dev`), `build` (`next build`), `start` (`next start`), `lint` (`next lint`)
- Lists all production and dev dependencies listed in §2 above.

### `frontend/next.config.mjs`
- `images.domains` — allowed external image hosts
- Environment variable exposure via `env` config

### `frontend/tailwind.config.ts`
- `content`: `['./src/**/*.{ts,tsx}']`
- `darkMode: 'class'` — toggled by next-themes
- `theme.extend`: custom colors, radius, font sizes

### `frontend/tsconfig.json`
- `baseUrl: '.'`, `paths: { "@/*": ["./src/*"] }` — enables `@/components/…` imports
- `target: 'es5'`, `lib: ['dom', 'es2017']`

---

## 4. App Directory — `src/app/`

---

### 4.1 Root App Files

#### `src/app/layout.tsx` — 22 lines
| Attribute | Value |
|---|---|
| Type | Server Component (Root Layout) |
| Renders | `<html>` → `<body>` → `<Providers>` → `{children}` |

**Imports**: `next/font/google` (Inter), `./globals.css`, `@/components/Providers`

**Key Functionality**:
- Sets `<html lang="en" suppressHydrationWarning>` — prevents next-themes FOUC flicker
- Applies Inter variable font to `<body className={inter.className}>`
- Exports `metadata`: title "Cadence - Timetable Optimization Platform", description
- All pages implicitly wrapped in `<Providers>` (see §5.1)

**Rendered by**: Next.js App Router (root)  
**Renders**: `Providers`

---

#### `src/app/globals.css` — 1 445 lines
The single source of truth for all CSS. Full description in [§12 CSS Architecture](#12-css-architecture).

---

#### `src/app/robots.ts` — 15 lines
| Attribute | Value |
|---|---|
| Type | Route Handler (server) |
| Route | `/robots.txt` |

**Exports** a Next.js `MetadataRoute.Robots` object:
- Allows all bots on `/`, `/blog`, `/pricing`, `/product`, `/company`
- Disallows `/admin/`, `/faculty/`, `/student/`, `/api/`

---

### 4.2 Authentication Routes — `(auth)`

#### `src/app/(auth)/login/page.tsx` — 396 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` — Client Component |
| Route | `/login` |

**Imports**:
- `react-hook-form` — `useForm`
- `@hookform/resolvers/zod`, `zod`
- `next/navigation` — `useRouter`
- `next/image`
- `@/context/AuthContext` — `useAuth`
- `@/lib/validations` — `loginSchema`, `LoginFormData`

**Key Functions / Components**:

| Name | Type | Lines | Description |
|---|---|---|---|
| `crawlStep(w)` | helper | ~10 | Returns random crawl step: large near 0%, tiny near 90%. Mirrors Google progress bar deceleration |
| `useCardProgress()` | hook | ~40 | Imperative API: `{ start, finish, reset, BarElement }` — 4px blue progress bar inside the login card (different from `NavigationProgress`). Used while form submits |
| `EyeOpen` | component | ~8 | Inline SVG eye icon (password visible) |
| `EyeOff` | component | ~8 | Inline SVG eye-slash icon (password hidden) |
| `OutlinedInput` | `forwardRef` component | ~60 | Google Material 3 outlined input field. `forwardRef` so react-hook-form's register ref reaches `<input>`. Handles Chromium autofill via `onAnimationStart`. Label lifts on focus/value |
| `LoginPage` | default export | ~200 | Main page: `useForm(zodResolver(loginSchema))`, `isLoading`, `showPassword`, `loginError` state. On submit → `useAuth().login()` → `router.push(ROLE_DASHBOARD[role])` |

**Constants**: `ROLE_DASHBOARD = { admin: '/admin/dashboard', faculty: '/faculty/dashboard', student: '/student/dashboard' }`

**Key Functionality**:
- Google-style `#f0f4f9` background, `28px` radius white card
- 4px progress bar absolute-positioned at top of card (shows during login request)
- `useForm` with `mode:'onChange'` + `zodResolver(loginSchema)`
- If user already authenticated on mount → immediate redirect (no blank flash)
- `loginError` string shown as inline error below fields

**Rendered by**: Next.js App Router  
**Renders**: `OutlinedInput`, `EyeOpen`/`EyeOff` icons

---

### 4.3 Marketing Routes — `(marketing)`

#### `src/app/(marketing)/layout.tsx` — 45 lines
| Attribute | Value |
|---|---|
| Type | Server Layout |
| Route | Wraps all `/(marketing)/*` pages |

**Imports**: `MarketingNav`, `MarketingFooter`

**Key Functionality**:
- Exports full SEO `metadata` including OG tags, Twitter card, keywords for academic scheduling, `metadataBase: 'https://cadence.edu'`
- Renders: `<MarketingNav />` + `<main>{children}</main>` + `<MarketingFooter />`

**Renders**: `MarketingNav`, `MarketingFooter`

---

#### `src/app/(marketing)/page.tsx` — 238 lines (Home Page)
| Attribute | Value |
|---|---|
| Type | Server Component |
| Route | `/` |

**Imports**: `HeroSection`, `SocialProof`, `FeatureGrid`, `PricingTable`

**Sections** (top to bottom):
1. `<HeroSection />` — Hero with animated timetable + CTA
2. `<SocialProof />` — Institution logos
3. Problem/Solution comparison (`OLD_WAY` vs `CADENCE_WAY` arrays)
4. How-It-Works 3-step section (`STEPS` array)
5. `<FeatureGrid />` — Feature deep-dive cards
6. Customer testimonial quote block
7. `<PricingTable preview />` — Compact pricing preview
8. Final CTA section with "Get Started" + "Talk to Sales" buttons

**Renders**: `HeroSection`, `SocialProof`, `FeatureGrid`, `PricingTable`

---

#### Marketing Sub-pages

| File | Lines | Route | Key Components Used |
|---|---|---|---|
| `blog/page.tsx` | 157 | `/blog` | Blog post card grid |
| `company/page.tsx` | 181 | `/company` | Team cards, mission section |
| `contact/page.tsx` | 116 | `/contact` | `DemoRequestForm` |
| `legal/privacy/page.tsx` | 61 | `/legal/privacy` | Policy body text |
| `legal/terms/page.tsx` | 65 | `/legal/terms` | Terms body text |
| `pricing/page.tsx` | 107 | `/pricing` | `PricingTable` (full, not preview) |
| `product/page.tsx` | 206 | `/product` | `FeatureGrid` + feature detail rows |
| `sitemap.ts` | 84 | `/sitemap.xml` | Auto-generates XML sitemap (server) |

---

### 4.4 Admin Routes — `src/app/admin/`

#### `src/app/admin/layout.tsx` — 41 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` — Client Layout |
| Route | All `/admin/*` |

**Imports**: `AppShell`, `AppShellSkeleton`, `AuthContext`

**Route Guard Logic**:
```
isLoading=true   → render <AppShellSkeleton />
user=null        → router.push('/login')
role not in [admin, org_admin, super_admin] → router.push('/unauthorized')
else             → <AppShell>{children}</AppShell>
```

**Renders**: `AppShellSkeleton` | `AppShell`

---

#### `src/app/admin/dashboard/page.tsx` — 657 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Route | `/admin/dashboard` |

**Imports**: `recharts` (BarChart, PieChart, LineChart, XAxis, YAxis, Tooltip…), `@/lib/api`, `@/types/timetable`

**Sub-component imports**: `AnalyticsOverview`, `QuickActions`, `SystemHealthWidget`

**Key State**: `stats`, `timetables`, `recentActivity`, `systemHealth`, `chartData`, `isLoading`, `selectedPeriod`

**Key Functionality**:
- Stat tiles: Total Faculty, Total Students, Active Timetables, Pending Approvals
- Recharts: BarChart (faculty distribution), LineChart (utilization trend), PieChart (room allocation)
- Recent activity feed (last 10 events)
- Quick actions: shortcuts to new timetable, add faculty, add student
- Calls `apiClient.getFaculty()`, `apiClient.getStudents()`, `apiClient.getTimetables()` on mount

**Renders**: `AnalyticsOverview`, `QuickActions`, `SystemHealthWidget`

---

#### Dashboard Sub-components

| File | Lines | Description |
|---|---|---|
| `dashboard/components/AnalyticsOverview.tsx` | 32 | 4 stat cards (total faculty, students, timetables, pending approvals) — receives counts as props |
| `dashboard/components/QuickActions.tsx` | 36 | Action buttons grid: New Timetable, Add Faculty, Add Student, View Reports |
| `dashboard/components/SystemHealthWidget.tsx` | 18 | API / DB / Redis status badges (green/yellow/red) |

---

#### `src/app/admin/admins/page.tsx` — 132 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Route | `/admin/admins` |

**Imports**: `DataTable`, `PageHeader`, `SearchBar`, `Avatar`, `AddEditUserModal`, `UserDetailPanel`, `@/lib/api`

**Key State**: `users[]`, `isLoading`, `searchTerm`, `currentPage`, `totalCount`, `detailUser: User | null`

**Render pattern** (swap view):
```
detailUser !== null  →  <UserDetailPanel user={detailUser} onBack={() => setDetailUser(null)} />
detailUser === null  →  <PageHeader /> + <DataTable /> + <AddEditUserModal />
```

**DataTable columns**: Name + Avatar, Email, Role badge, Department, Status badge

**Key Functionality**:
- `avatarColumn` prop → Google Contacts avatar ↔ checkbox flip on hover
- `onRowClick` sets `detailUser` for detail panel
- Multi-select bulk delete via `onDelete(ids[])`
- Server-side search + pagination

**Renders**: `UserDetailPanel` | (`PageHeader` + `DataTable` + `AddEditUserModal`)

---

#### `src/app/admin/admins/components/UserDetailPanel.tsx` — 127 lines
| Attribute | Value |
|---|---|
| **Total Lines** | 127 |
| **Imports** | `@/components/shared/Avatar` |

**Props**: `user: User`, `onBack: () => void`

**Layout**:
- `flex flex-col min-h-full w-full` — fills AppShell content card fully
- Back arrow `←` button top-left → calls `onBack()`
- `Avatar size={162}` in horizontal header alongside name/email/role badge
- 2-column card grid (`grid-cols-1 md:grid-cols-2 gap-4`): Role & Access, Personal Info, Account Details, Activity History

**Renders**: `Avatar`  
**Rendered by**: `admins/page.tsx`

---

#### `src/app/admin/admins/components/AddEditUserModal.tsx` — 165 lines
| Attribute | Value |
|---|---|
| **Total Lines** | 165 |
| **Imports** | `react-hook-form`, `@hookform/resolvers/zod`, `@/lib/validations` (`userSchema`), `@/components/FormFields` |

**Form Fields**: Username, Email, Password (create only, hidden on edit), First Name, Last Name, Role (select), Department, Active (toggle)

**Validation**: `zodResolver(userSchema)` — email format, password 8+ chars with complexity rules  
**Calls**: `onSave(data)` on valid submit

---

#### `src/app/admin/faculty/page.tsx` — 140 lines
| Route | `/admin/faculty` |
|---|---|

**Same pattern as admins page**: swap render between `FacultyDetailPanel` and DataTable view.

**DataTable columns**: Name + Avatar, Faculty ID, Designation badge, Department, Specialization, Workload capacity

**Renders**: `FacultyDetailPanel` | (`PageHeader` + `DataTable` + `AddEditFacultyModal`)

---

#### `src/app/admin/faculty/components/FacultyDetailPanel.tsx` — 149 lines
**Props**: `faculty`, `onBack`, `onEdit`, `onDelete`  
**Layout**: `Avatar size={162}` + horizontal header + Edit/Delete buttons + 2-col card grid (Personal Details, Workload Limits, Specialization, History)  
**Renders**: `Avatar`

---

#### `src/app/admin/faculty/components/AddEditFacultyModal.tsx` — 218 lines
**Validation**: `simpleFacultySchema` (Zod)  
**Fields**: Faculty ID, First/Middle/Last Name, Designation (enum: Professor / Associate Professor / Assistant Professor / Lecturer / Senior Lecturer), Specialization, Max Weekly Workload, Email, Phone, Department (fetched from API), Status (active / inactive / on_leave)

---

#### `src/app/admin/students/page.tsx` — 126 lines
**Imports**: `DataTable`, `PageHeader`, `Avatar`, `AddEditStudentModal`, `StudentDetailPanel`  
**Same swap-render pattern** as faculty and admins pages.  
**Renders**: `StudentDetailPanel` | (`PageHeader` + `DataTable` + `AddEditStudentModal`)

---

#### `src/app/admin/students/components/StudentDetailPanel.tsx` — 176 lines
**Props**: `student`, `onBack`, `onEdit`, `onDelete`  
**Layout**: `Avatar size={162}` + header + 2-col card grid: Academic Details, Personal Details, Hostel & Finance (conditional), History  
**Renders**: `Avatar`

---

#### `src/app/admin/students/components/AddEditStudentModal.tsx` — 215 lines
**Validation**: `simpleStudentSchema`  
**Fields**: Student ID, First/Last Name, Email, Phone, Department (API dropdown), Course (API dropdown), Year, Semester, Electives, Faculty Advisor

---

#### Academic Sub-pages Pattern

All academic CRUD pages follow the same structure:
- `'use client'` + `useState` + `useCallback` + `useEffect`
- `DataTable<Entity>` + `PageHeader` + modal component
- Server-side pagination and search

| File | Lines | Route | Entity | Modal | API Calls |
|---|---|---|---|---|---|
| `academic/buildings/page.tsx` | 98 | `/admin/academic/buildings` | Building | `AddEditBuildingModal` (141 ln) | `getBuildings`, `createBuilding`, `updateBuilding`, `deleteBuilding` |
| `academic/courses/page.tsx` | 165 | `/admin/academic/courses` | Subject/Course | Inline form | `getCourses` |
| `academic/departments/page.tsx` | 101 | `/admin/academic/departments` | Department | `AddEditDepartmentModal` (143 ln) | `getDepartments`, `createDepartment`, `updateDepartment`, `deleteDepartment` |
| `academic/programs/page.tsx` | 98 | `/admin/academic/programs` | Program | `AddEditProgramModal` (161 ln) | `getPrograms`, CRUD |
| `academic/rooms/page.tsx` | 195 | `/admin/academic/rooms` | Room/Classroom | Inline form | `getRooms`, `createRoom`, `updateRoom`, `deleteRoom` |
| `academic/schools/page.tsx` | 100 | `/admin/academic/schools` | School | `AddEditSchoolModal` (115 ln) | `getSchools`, CRUD |

**`academic/layout.tsx`** (3 lines): passthrough — returns `{children}` only  
**`academic/page.tsx`** (10 lines): calls Next.js `redirect('/admin/academic/schools')`

---

#### `src/app/admin/timetables/page.tsx` — 622 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Route | `/admin/timetables` |

**Imports**: `@/lib/api`, `@/types/timetable` (`TimetableListItem`), `@/components/timetables/*`, `TimetableListSkeleton`

**Key State**: `timetables: TimetableListItem[]`, `isLoading`, `filterStatus` (all/approved/pending/draft/rejected), `searchTerm`, `viewMode` ('list' | 'grid'), `selectedVariantId`

**Key Functionality**:
- Filter bar: status tabs (All / Approved / Pending / Draft / Rejected)
- Search input (searches name, department, semester)
- List view: table with status badge, score bar, conflicts count, action buttons (View, Compare, Approve/Reject)
- Grid view: `VariantCard` tile grid
- Navigate to `/admin/timetables/:id/review` on row click
- `Link href="/admin/timetables/new"` for + New Timetable button

**Renders**: `TimetableListSkeleton` | (`PageHeader` + filter bar + `DataTable`/`VariantGrid`)

---

#### `src/app/admin/timetables/new/page.tsx` — 218 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Route | `/admin/timetables/new` |

**Imports**: `@/lib/api`, `@/lib/validations` (`timetableGenerationSchema`), `useProgress`, `useSmoothProgress`, `getStageDisplayName`, `formatETA`

**Form Steps**:
1. **Step 1** — Select: departments (multi), batches, semester, academic year
2. **Step 2** — Constraints: working days, max daily load, lab constraints, elective slots
3. **Step 3** — Confirm: summary before submit

**On Submit**:
1. `apiClient.generateTimetable(formData)` → receives `{ job_id }`
2. SSE subscription via `useProgress(job_id)` starts
3. `useSmoothProgress(actual)` animates the progress bar
4. Stage name shown via `getStageDisplayName(stage)`
5. ETA via `useSmoothedETA(eta_seconds)` → `formatETA()`
6. On complete → redirect to `/admin/timetables/status/{jobId}`

---

#### `src/app/admin/approvals/page.tsx` — 455 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Route | `/admin/approvals` |

**Imports**: `@/lib/api/timetable-variants` (`fetchWorkflows`, `approveWorkflow`), `@/types/timetable` (`WorkflowListItem`), Toast

**Sub-components (inline)**:
| Name | Description |
|---|---|
| `SkeletonRow()` | 5-column shimmer row for loading state |
| `EmptyState()` | "All caught up!" with check icon |

**Key Functions**:
| Function | Description |
|---|---|
| `formatDate(iso)` | Formats ISO date string with `en-IN` locale (DD/MM/YYYY format) |
| `handleApprove(id)` | `approveWorkflow(id, {action:'approve'})` → refreshes list |
| `handleReject(id)` | Opens reason input dialog → `approveWorkflow(id, {action:'reject', reason})` |

**Table columns**: Timetable Name, Department, Semester/Year, Submitted By, Submitted At, Status badge, Actions (Approve | Reject)

---

#### `src/app/admin/logs/page.tsx` — 191 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Route | `/admin/logs` |

**Key Functionality**:
- Renders audit activity log table
- **Currently uses static mock data** (hardcoded log array) — TODO connect to `GET /api/audit-logs/`
- Level badge color map: `INFO` → blue, `SUCCESS` → green, `WARNING` → yellow/amber, `ERROR` → red
- Filter bar: level-based filter tabs
- Columns: Timestamp, Level badge, Action, User (email), IP Address, Detail/Description

---

### 4.5 Faculty Routes — `src/app/faculty/`

#### `src/app/faculty/layout.tsx` — 33 lines
**Role guard**: allows `faculty` role only.  
**Same pattern as admin layout**: `AppShellSkeleton` while loading, `AppShell` when authenticated.

---

#### `src/app/faculty/dashboard/page.tsx` — 327 lines
| Route | `/faculty/dashboard` |
|---|---|

**Key Features**:
- Today's schedule card — upcoming class slots for the day (subject, room, batch, time)
- Weekly schedule mini-calendar
- Workload summary (hours this week vs limit)
- Quick actions: View Full Schedule, Set Preferences, Report Conflict
- Notification/announcements feed
- API: `apiClient.getFaculty()`, `apiClient.getTimetables()` filtered by faculty

---

#### `src/app/faculty/preferences/page.tsx` — 155 lines
| Route | `/faculty/preferences` |
|---|---|

**Key Features**:
- Day availability toggles (Monday–Saturday)
- Time-slot preference matrix: 'prefer' / 'neutral' / 'avoid' per slot
- Max classes per day stepper
- Saves via `apiClient.updateFaculty(id, preferences)`

---

#### `src/app/faculty/schedule/page.tsx` — 220 lines
| Route | `/faculty/schedule` |
|---|---|

**Key Features**:
- Full weekly timetable for the authenticated faculty member
- Uses `TimetableGrid` component (read/write mode)
- Week navigation (← prev week / next week →)
- Print and Export buttons (PDF via `exportUtils`)

**Renders**: `TimetableGrid`, `ExportButton`

---

### 4.6 Student Routes — `src/app/student/`

#### `src/app/student/layout.tsx` — 26 lines
**Role guard**: allows `student` role only. Same AppShell wrapping pattern.

---

#### `src/app/student/dashboard/page.tsx` — 850 lines (largest file)
| Route | `/student/dashboard` |
|---|---|

**Key Features**:
- Today's classes with full slot details (subject, faculty name, room, time)
- Attendance overview widget (present/absent/percentage per subject)
- GPA trend sparkline (Recharts LineChart)
- Upcoming exams/events countdown
- Quick links: Timetable, Leave Application, Library Portal
- Course progress cards (syllabus coverage %)
- API: `apiClient.getStudents()` (self), `apiClient.getTimetables()` (own batch)

---

#### `src/app/student/timetable/page.tsx` — 250 lines
| Route | `/student/timetable` |
|---|---|

**Key Features**:
- Full weekly timetable for the student's batch
- `TimetableGrid` in read-only mode
- Week navigation
- `ExportButton` (PDF / Excel / ICS)
- Subject colour coding

**Renders**: `TimetableGrid`, `ExportButton`

---

### 4.7 Other Routes

#### `src/app/unauthorized/page.tsx` — 34 lines
| Route | `/unauthorized` |
|---|---|
**Renders**: 403 "Access Denied" page with role info and "Go to Dashboard" link. Link destination determined by `user.role` from `useAuth()`.

---

## 5. Components Directory — `src/components/`

---

### 5.1 Root-level Components

#### `src/components/Providers.tsx` — 21 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` — Root Provider Composition |
| Rendered by | `app/layout.tsx` |

**Imports**: `ThemeProvider` (next-themes), `AuthProvider`, `ErrorBoundary`, `ToastProvider`, `NavigationProgress`

**Provider nesting** (outermost first):
```
ThemeProvider attribute="class" defaultTheme="system"
  NavigationProgress          ← persists across all routes, outside error boundary
  ErrorBoundary
    ToastProvider
      AuthProvider
        {children}
```

**Why this order**: `NavigationProgress` survives errors since it's outside `ErrorBoundary`. `AuthProvider` is innermost so every page component can access auth state immediately.

**Renders**: `NavigationProgress`, `ErrorBoundary`, `ToastProvider`, `AuthProvider`

---

#### `src/components/AuthRedirect.tsx` — 46 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Used on | Login page only |

**Imports**: `@/context/AuthContext`

**Key Functionality**:
- If `user !== null`: reads `user.role`, redirects to appropriate dashboard
- No-op when user is not logged in
- Does NOT redirect on marketing pages (not included in marketing layout)
- Role → route map: admin → `/admin/dashboard`, faculty → `/faculty/dashboard`, student → `/student/dashboard`

---

#### `src/components/ErrorBoundary.tsx` — 126 lines
| Attribute | Value |
|---|---|
| Type | Class Component (required for React error boundaries) |
| Rendered by | `Providers.tsx` |

**Key Methods**:
| Method | Description |
|---|---|
| `static getDerivedStateFromError(error)` | Sets `hasError: true, error` on state |
| `componentDidCatch(error, info)` | Logs to console (+ Sentry in production) |
| `reset()` | Clears error state for retry |

**Fallback UI**: "Something went wrong" heading, error message (dev-only detail), "Try Again" and "Go Home" buttons.

---

#### `src/components/FormFields.tsx` — 139 lines
| Attribute | Value |
|---|---|
| Type | Client utility components |
| Used by | All modals and form pages |

**Exported Components**:
| Component | Props | Description |
|---|---|---|
| `FormField` | `label`, `error?`, `required?`, `className?`, `children` | Label wrapper + inline error message |
| `InputField` | `label`, `error?`, `required?`, `...HTMLInputElement` | `<input>` + label + error. Forwards all native attrs |
| `SelectField` | `label`, `options: {value,label}[]`, `error?`, `...select` | Styled native `<select>` + label + error |
| `TextAreaField` | `label`, `rows?`, `error?`, `...textarea` | `<textarea>` + label + error |

---

#### `src/components/LoadingSkeletons.tsx` — 315 lines
| Attribute | Value |
|---|---|
| Type | Client utility components |
| Used by | All loading states across app |

**Exported Components**:
| Component | Props | Description |
|---|---|---|
| `Skeleton` | `className?`, `style?` | Base block — `animate-pulse bg-gray-200 dark:bg-[#333537] rounded-md` |
| `TableSkeleton` | `rows?=8`, `columns?=5` | Full `<table>` with header + body shimmers |
| `TableRowsSkeleton` | `rows?=5`, `columns?=4` | Just `<tr>` elements (for use inside existing `<tbody>`) |
| `MobileCardsSkeleton` | `cards?=3` | Card-style shimmer for mobile list views |
| `ListSkeleton` | `items?=5` | List item shimmers |
| `TimetableCardSkeleton` | — | Single timetable card shimmer |
| `TimetableListSkeleton` | `cards?=4` | N × `TimetableCardSkeleton` |
| `VariantCardSkeleton` | — | Variant comparison card shimmer |
| `TimetableGridSkeleton` | `days?=6`, `slots?=8` | Days × slots grid shimmer |

---

#### `src/components/Pagination.tsx` — 296 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Imported by | `DataTable`, various list pages |

**Props**:
| Prop | Type | Description |
|---|---|---|
| `currentPage` | number | 1-based current page |
| `totalPages` | number | Total page count |
| `totalCount` | number | Total record count |
| `itemsPerPage` | number | Current page size |
| `onPageChange` | `(page: number) => void` | Callback |
| `onItemsPerPageChange` | `(size: number) => void` | Callback |
| `showItemsPerPage` | boolean | Show per-page selector |

**Key Functions**:
| Function | Description |
|---|---|
| `getPageNumbers()` | Smart windowed pagination: always shows 1 and last page, ellipsis (`…`) between windows of 5, max 7 visible buttons |

**Key Functionality**:
- Keyboard navigation: `←`/`→` for prev/next, `Home`/`End` for first/last
- "Showing X–Y of Z results" text
- Items-per-page dropdown: 10 / 25 / 50 / 100
- Boundary pages: greyed + `cursor-not-allowed`
- Mobile: shows compact "N of M" format

---

#### `src/components/Toast.tsx` — 199 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Rendered by | `Providers.tsx` |

**Imports**: `react-hot-toast`

**Exports**:
| Export | Description |
|---|---|
| `ToastProvider` | Configures `<Toaster>` with custom position (top-right), duration (4000ms), and CSS styles |
| `useToast()` | Returns `{ showToast, showSuccessToast, showErrorToast, showWarningToast, showInfoToast }` |

**Toast types**: success (green icon), error (red icon), warning (yellow icon), info (blue icon). All auto-dismiss after 4 seconds.

---

### 5.2 Shell Components — `src/components/shell/`

#### `src/components/shell/AppShell.tsx` — 753 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` — Application Layout Shell |
| Rendered by | `admin/layout.tsx`, `faculty/layout.tsx`, `student/layout.tsx` |

**Imports**: `AuthContext`, `Avatar`, `ProfileDropdown`, `Breadcrumb`, `next-themes`, `next/image`, 30+ `lucide-react` icons, `next/navigation`

**Key Interfaces**:
```typescript
NavItem  = { label: string; href: string; icon: LucideIcon; badge?: boolean; activeBase?: string }
NavGroup = { label: string; icon: LucideIcon; base: string; children: NavItem[] }
NavEntry = NavItem | NavGroup
```

**Nav Definitions**:

`ADMIN_NAV` (9 entries):
- Dashboard (`/admin/dashboard`)
- Admins (`/admin/admins`)
- Faculty (`/admin/faculty`)
- Students (`/admin/students`)
- Academic *(NavGroup)* → Buildings, Courses, Departments, Programs, Rooms, Schools
- Timetables (`/admin/timetables`)
- Approvals (`/admin/approvals`) ← has pending badge dot
- Logs (`/admin/logs`)

`FACULTY_NAV` (4): Dashboard, My Schedule, Preferences, Notifications

`STUDENT_NAV` (2): Dashboard, My Timetable

**Key Sub-components**:
| Component | Description |
|---|---|
| `NavItemRow` | Single nav link with active highlight (`bg-[var(--color-nav-active)]`), optional badge dot, icon-only when collapsed (sr-only label preserves accessibility) |
| `NavGroupRow` | Collapsible nav section with chevron. Auto-expands if current path matches any child. In rail (collapsed) mode: icon-only link to first child |
| `QuickLink` | Small link row used in the `+ New` dropdown panel |

**Key State**:
| State | Default | Description |
|---|---|---|
| `sidebarOpen` | `true` | Desktop sidebar expanded (284px) vs rail (72px) |
| `mobileOpen` | `false` | Mobile overlay drawer open |
| `profileOpen` | `false` | `ProfileDropdown` visible |
| `showSignOut` | `false` | Sign-out confirmation dialog |
| `searchOpen` | `false` | Mobile search overlay |
| `newMenuOpen` | `false` | `+ New` admin dropdown panel |
| `mounted` | `false` | Hydration guard (SSR-safe class names) |

**Key Functions**:
| Function | Description |
|---|---|
| `resolveUser(u)` | Returns `{ full: string, initials: string }` — concatenates first/last or falls back to username |
| `handleHamburger()` | Viewport-aware: `< md` → toggles `mobileOpen`, `≥ md` → toggles `sidebarOpen` |
| `handleSignOut()` | Calls `logout()` → `router.push('/login')` |
| `isNavItem(e)` | Type guard: `boolean` — `'href' in e` |

**Layout Structure**:
```
<div min-h-screen bg-[--color-bg]>
  <header fixed z-[50] h-[56px] md:h-[64px]>
    ← Zone 1: w-[72px] md:w-[284px] — hamburger + logo text (hidden when collapsed)
    ← Zone 2: flex-1 max-w-[720px] — search input, rounded-full, 40px tall
    ← Zone 3: ml-auto flex items-center gap-2 — mobile search | + New (admin) | Bell | Avatar
  <aside fixed z-[45] w-[284px] (expanded) / w-[72px] (rail)
    [transition: width 200ms cubic-bezier(0.4,0,0.2,1)]
    <nav> list of NavItemRow / NavGroupRow entries
  <main ml-[72px] md:ml-[284px] / ml-[72px] pt-[56px] md:pt-[64px]>
    [transition: margin-left 200ms]
    <div white card rounded-2xl p-3 md:p-6 min-h-[calc(100vh-...)]>
      <Breadcrumb />
      {children}
```

**`+ New` dropdown** (admin only): slides down below `+ New` button — sections: Timetable, People (Admin/Faculty/Student), Academic (Building/Department etc.)

**Renders**: `ProfileDropdown`, `Breadcrumb`, `Avatar`, `NavItemRow`, `NavGroupRow`

---

#### `src/components/shell/ProfileDropdown.tsx` — 204 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Rendered by | `AppShell` (conditionally when `profileOpen=true`) |

**Imports**: `Avatar`, `next-themes` (`useTheme`), lucide-react (X, LogOut, UserIcon, ShieldCheck, Settings, Globe, HelpCircle, Sun, Moon)

**Props**:
| Prop | Type | Description |
|---|---|---|
| `user` | `User \| null` | Current user data |
| `displayName` | `string` | Full name string |
| `role` | `string` | Role string |
| `rolePill` | `string` | Display role (e.g. "Admin") |
| `mounted` | `boolean` | Hydration guard for theme |
| `onClose` | `() => void` | Close handler |
| `onSignOut` | `() => void` | Sign out handler |

**Positioning**: `position: fixed; top: 70px; right: 11px` — anchored top-right of viewport

**Dimensions**: `width: 420px`, `border-radius: 28px`, background `#eaf0f6` (light) / `#202124` (dark)

**Structure** (top → bottom):

| Section | Description |
|---|---|
| Loading bar (3px) | `#4285f4`, `animate-[profileLoad_1.4s_ease-in-out_infinite]` — shown when `user===null` |
| Email row (non-scroll) | Centered `user.email` + `×` close button, `height: 48px` |
| Avatar + greeting (non-scroll) | `Avatar size={72}` + "Hi, {firstName}!" + camera icon overlay |
| Scrollable section | `className="profile-scroll"` — `max-height: 280px; overflow-y: auto` |
| → Role badge | "Logged in as [ADMIN]" pill |
| → Profile / Sign Out | Split pill button row |
| → Settings + Theme toggle | `@radix-ui/react-switch` dark mode toggle + settings link |
| → Language / Help | Two side-by-side buttons |
| Footer row | "Manage accounts" link + org name |

**z-index**: `z-[991]`  
**Renders**: `Avatar`

---

#### `src/components/shell/AppShellSkeleton.tsx` — 95 lines
| Attribute | Value |
|---|---|
| Type | Client Component |
| Rendered by | Route layout files during auth guard check |

**Key Functionality**:
- Pixel-accurate shimmer matching AppShell visual structure
- `Shimmer` inline component: `animate-pulse rounded-md bg-gray-200 dark:bg-[#333537]`
- Structure: fixed header shimmer + fixed sidebar shimmer + content area (4 stat tiles + 5 text rows)
- Prevents cumulative layout shift (CLS) during auth resolution

---

#### `src/components/shell/Breadcrumb.tsx` — 204 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Rendered by | `AppShell.tsx` (always mounted inside content card) |
| Imports | `next/navigation` (`usePathname`), `next/link`, lucide-react (`ChevronRight`) |

**Key Constants**:
- `ROUTES`: array of 25 objects `{ pattern: RegExp, crumbs: BreadcrumbItem[] }` — maps pathname patterns to breadcrumb definitions for every route in the app
- `SUPPRESS_ROUTES`: 9 route prefixes where breadcrumb is hidden (pages use their own `PageHeader` instead, e.g. `/admin/timetables/new`, `/admin/faculty`)

**Rendering logic**:
- Single crumb → `<h1 className="page-title">` (no nav element)
- Multiple crumbs → `<nav aria-label="Breadcrumb">` with `ChevronRight` separator. Ancestor items = `<Link>`, current item = `<span aria-current="page">`
- Suppressed routes → return `null`

---

### 5.3 Shared Components — `src/components/shared/`

#### `src/components/shared/Avatar.tsx` — 74 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Used by | AppShell header, DataTable (avatarColumn), UserDetailPanel, FacultyDetailPanel, StudentDetailPanel, SlotDetailPanel, ProfileDropdown |

**Imports**: `react` (useRef, useEffect)

**Type**: `type AvatarSize = 'sm' | 'md' | 'lg'` where `sm=32px, md=36px, lg=40px`. Also accepts any `number` for custom sizes.

**Key Constants**:
| Constant | Value |
|---|---|
| `PALETTE` | 10 Material Design colours: `['#4285f4','#ea4335','#fbbc04','#34a853','#ff6d00','#46bdc6','#7c4dff','#e91e63','#00897b','#f06292']` |
| `SIZE_PX` | `{ sm: 32, md: 36, lg: 40 }` |

**Key Functions**:
| Function | Description |
|---|---|
| `seedColor(name)` | djb2-style hash: iterates chars, `hash = (hash << 5) - hash + charCode → hash % 10` → deterministic `PALETTE[index]` |
| `initial(name)` | `name[0].toUpperCase()` |

**Props**: `name: string`, `size?: AvatarSize | number`, `imageUrl?: string`, `className?: string`

**CSS Custom Properties** (set via `useEffect` on div ref):
| Property | Value |
|---|---|
| `--av-sz` | `${px}px` — width and height |
| `--av-fs` | `${Math.round(px * 0.42)}px` — Google's 0.42 ratio for initials font size |
| `--av-bg` | seeded hex color |

**Tailwind**: `[width:var(--av-sz)] [height:var(--av-sz)] [font-size:var(--av-fs)] [background:var(--av-bg)]` — all arbitrary value syntax, no inline styles

**`.avatar-font`**: CSS class applying `font-family: 'Google Sans', 'Product Sans', Roboto, sans-serif`

---

#### `src/components/shared/DataTable.tsx` — 942 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` — Generic component `DataTable<T>` |
| Used by | All CRUD list pages across admin section |

**Imports**: `Avatar`, `ConfirmDeleteDialog`, 15+ lucide-react icons, `next/navigation`

**Key Interfaces**:
```typescript
Column<T> = { key: keyof T | string; header: string; width?: number; render?: (row: T) => ReactNode }
EmptyStateConfig = { icon: LucideIcon; title: string; description?: string; action?: { label: string; onClick: () => void } }
Density = 'comfortable' | 'compact'
```

**Key Props**:
| Prop | Type | Description |
|---|---|---|
| `data` | `T[]` | Row data |
| `columns` | `Column<T>[]` | Column definitions |
| `avatarColumn` | `(row: T) => string \| null` | Enables Google Contacts avatar↔checkbox animation |
| `selectable` | boolean | Show checkbox column |
| `onRowClick` | `(row: T) => void` | Detail panel navigation |
| `onEdit` | `(row: T) => void` | Edit callback (shows pencil icon on hover) |
| `onDelete` | `(ids: string[]) => void` | Delete callback (single or bulk) |
| `emptyState` | `EmptyStateConfig` | Custom empty state |
| `isLoading` | boolean | Shows `SkeletonRows` |
| `currentPage` | number | For "showing X–Y of Z" |
| `totalCount` | number | |
| `itemsPerPage` | number | |
| `onPageChange` | `(p) => void` | |

**Inline Sub-components**:
| Component | Description |
|---|---|
| `SkeletonRows` | 8 rows of `loading-skeleton` shimmer cells |
| `EmptyState` | Icon + title + description + optional action button |
| `BulkToolbar` | Shown above table when items selected: count + Delete + Clear X |
| `DensityDialog` | Modal with comfortable/compact toggle + row height preview bar |
| `ColumnOrderDialog` | Modal with draggable column list (HTML5 drag-and-drop) |

**Key Functionality**:
- **Avatar ↔ Checkbox flip**: on hover, avatar fades out → checkbox fades in. Selected row: avatar hidden, checkbox checked.
- **Header checkbox**: Has caret dropdown with "All" / "None" / "Select this page" options
- **Blue selection mode**: selected rows use `var(--row-selected-bg)`, bulk toolbar replaces search area
- **Toolbar**: Print · Export CSV · ⋮ → Display Density / Column Order
- **Row hover**: Edit (Pencil) + Delete (Trash2) icons appear from `group-hover:opacity-100`
- **`handleExport()`**: Generates CSV from current columns, triggers browser download
- **`handlePrint()`**: `window.print()` (or custom callback)
- **Pagination**: Built-in prev/next with "Showing X–Y of Z" — or delegates to parent via props

---

#### `src/components/shared/ConfirmDeleteDialog.tsx` — 83 lines
| Props | `isOpen`, `title`, `message`, `entityName?`, `onConfirm`, `onCancel`, `isDeleting` |
|---|---|

Modal overlay with entity name highlighted in red, Confirm (red/danger) and Cancel buttons. `isDeleting` prop shows spinner on Confirm button.

---

#### `src/components/shared/ExportButton.tsx` — 159 lines
| Attribute | Value |
|---|---|
| Imports | `@/lib/exportUtils` |

**Props**: `slots: TimetableSlotDetailed[]`, `options: ExportOptions` (`{ filename, title, department, semester, academicYear }`)

**Key Functionality**:
- Dropdown button with 4 options: Export as PDF, Export as Excel, Export as CSV, Export as Calendar (.ics)
- Calls respective `exportUtils` functions
- Shows loading state per format while exporting

---

#### `src/components/shared/PageHeader.tsx` — 97 lines
| Attribute | Value |
|---|---|
| Imports | `next/link`, lucide-react (`ChevronRight`) |

**Props**:
| Prop | Description |
|---|---|
| `title` | Page title string |
| `count?` | Shows `title (N)` suffix |
| `loading?` | Hides count, shows blank while loading |
| `primaryAction?` | `{ label, onClick, icon? }` — renders `btn-primary` button |
| `secondaryActions?` | Array of secondary buttons |
| `parentLabel?` | Breadcrumb parent text |
| `parentHref?` | Makes parentLabel a `<Link>` |

**Rendered as**: `[parentLabel ChevronRight] title (count)`  
Row layout: title/breadcrumb left, action buttons right aligned.

---

#### `src/components/shared/SearchBar.tsx` — 48 lines
Controlled input with `Search` icon (lucide). Props: `value`, `onChange`, `placeholder`, `className`.  
Focus-within: border brightens via CSS `:focus-within` selector.

---

#### `src/components/shared/TimetableGrid.tsx` — 273 lines
| Attribute | Value |
|---|---|
| Imports | `@/types/timetable`, `@/components/timetables/SlotDetailPanel` |

**Props**: `slots: TimetableEntry[]`, `days?: string[]`, `timeSlots?: TimeSlot[]`, `onSlotClick?`, `readOnly?`

**Key Functionality**:
- CSS Grid: time slots × days matrix layout
- Slot card rendering: subject name, faculty name, room, batch
- Badge: `LAB` (purple pill) when `is_lab=true`, `ELECTIVE` (teal italic) when `is_elective=true`
- Click slot → opens `SlotDetailPanel` (unless `readOnly=true`)
- Color coding: each subject gets a consistent seeded color (same algorithm as Avatar)

**Renders**: `SlotDetailPanel`

---

### 5.4 UI Components — `src/components/ui/`

#### `src/components/ui/NavigationProgress.tsx` — 241 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` |
| Mounted by | `Providers.tsx` — stays mounted for entire session |
| Imports | `next/navigation` (`usePathname`), React |

**Configuration** (`CFG` object):
| Key | Value | Purpose |
|---|---|---|
| `CRAWL_CAP` | 90 | Max % before nav completes |
| `INITIAL_WIDTH` | 20 | Starting % on click |
| `TICK_MS` | 200 | Crawl timer interval |
| `FINISH_HOLD_MS` | 180 | ms at 100% before hiding |
| `FADE_MS` | 400 | Fade-out animation duration |

**Key Functions**:
| Function | Description |
|---|---|
| `crawlStep(w)` | Returns random step — large (5–20) near 0%, medium near 50%, near-zero (0.2–1.5) near 87%. Mirrors Google's deceleration. |
| `start()` | Reset to 0% → jump to `INITIAL_WIDTH` → begin `setInterval(TICK_MS)` crawl |
| `finish()` | Snap to 100% → hold `FINISH_HOLD_MS` → fade opacity to 0 → reset |
| `applyWidth(w)` | Direct DOM: `barRef.current.style.width = ${w}%` — zero React re-renders |
| `applyOpacity(op, ms)` | Direct DOM: wrapper opacity with `transition: opacity ${ms}ms` |
| `stopTick()` | Clears crawl interval |
| `stopHide()` | Clears finish timeout |

**Link interception**: `document.addEventListener('click', handler, true)` (capture phase)
- Traverses event target up through ancestors looking for `<a>` tag
- Skips: `_blank` target, external origins, `mailto:`/`tel:`, hash-only `#…`, same-page links

**Finish trigger**: `useEffect([pathname])` — detects when Next.js path changes after navigation, calls `finish()`

**Visual**: 3px fixed bar at `top:0; left:0; right:0; z-index:9999`, color `#1a73e8`, box-shadow glow tip at right end: `0 0 8px 2px rgba(26,115,232,0.6)`

---

#### `src/components/ui/GoogleSpinner.tsx` — 83 lines
**Exports**:
- `GoogleSpinner`: Circular SVG arc cycling through 4 Google colours (blue, red, yellow, green) with CSS animation
- `LoadingDots`: 3-dot bounce animation via `animation-delay` stagger

---

### 5.5 Timetable Components — `src/components/timetables/`

#### `src/components/timetables/SlotDetailPanel.tsx` — 150 lines
| Imports | `Avatar`, `@/types/timetable` |
|---|---|

**Props**: `slot: TimetableSlotDetailed`, `onClose: () => void`, `isOpen: boolean`

**Key Functionality**:
- Slide-in panel (CSS transform translate-x) from right edge
- Faculty `Avatar size={32}` with seeded colour
- Slot details: Subject (name, code, credits), Faculty (name, designation), Room, Batch/Section, Day + Time, Lab/Elective indicators
- Conflict warnings (if `slot.conflicts` array non-empty)

**Renders**: `Avatar`

---

#### `src/components/timetables/VariantCard.tsx` — 198 lines
| Imports | `ScoreBar`, `VariantStatusBadge`, `@/types/timetable` |
|---|---|

**Props**: `variant: TimetableVariant`, `onSelect`, `onView`, `onCompare`, `isSelected?`

**Key Functionality**:
- Card layout: Variant # header + `VariantStatusBadge`
- `ScoreBar` for overall score
- Metric row: Conflicts count, Room Utilization %, Faculty Balance %
- Action buttons: View, Select (blue when `isSelected`), Compare

---

#### `src/components/timetables/VariantGrid.tsx` — 196 lines
| Imports | `VariantCard`, `VariantCardSkeleton` |
|---|---|

**Props**: `variants: TimetableVariant[]`, `isLoading`, `selectedVariantId`, `comparisonIds`, `onSelect`, `onView`, `onCompare`

Renders responsive grid of `VariantCard` items.

---

#### `src/components/timetables/ScoreBar.tsx` — 66 lines
| Props | `score: number` (0–100), `label?: string`, `showPercent?: boolean` |
|---|---|

Animated fill bar. Color: `red` (`< 50`), `amber` (`50–75`), `green` (`> 75`). Fill transition `1s ease-out` on mount.

---

#### `src/components/timetables/VariantStatusBadge.tsx` — 79 lines
Maps `optimization_label` string → styled badge:
- `"Faculty Optimized"` → blue
- `"Room Optimized"` → green
- `"Student Experience"` → purple
- `"Recommended"` → gold
- fallback → grey

---

#### `src/components/timetables/CompareGrid.tsx` — 355 lines
| Imports | `@/lib/api/timetable-variants` (`compareVariants`), `@/types/timetable` |
|---|---|

**Props**: `variantId1: string`, `variantId2: string`

**Key Functionality**:
- Fetches comparison data via `compareVariants(id1, id2)` on mount
- Side-by-side timetable grid (days × time-slots pair)
- Cell diff highlighting: green border = improved, red = worse, yellow = changed but neutral
- Legend row at top
- `ComparisonResult` from types defines shared/changed/added/removed slot arrays

---

#### `src/components/timetables/TimetableGridFiltered.tsx` — 345 lines
| Imports | `TimetableGrid`, `DepartmentTree`, `@/lib/api` |
|---|---|

**Props**: `slots: TimetableEntry[]`, `departments: Department[]`, others pass-through

**Key Functionality**:
- Filter toolbar: Department (via `DepartmentTree`), Faculty (dropdown), Batch (dropdown), Room (dropdown)
- Active filter chips with × clear button per filter
- Filtered `slots` passed to `TimetableGrid`

**Renders**: `DepartmentTree`, `TimetableGrid`

---

#### `src/components/timetables/DepartmentTree.tsx` — 120 lines
| Props | `departments: Department[]`, `selectedIds: string[]`, `onChange: (ids: string[]) => void` |
|---|---|

Collapsible tree view: Department → Batches. Checkbox per node. Parent auto-checks when all children selected.

---

### 5.6 Marketing Components — `src/components/marketing/`

| File | Lines | Description | Key Props / Exports |
|---|---|---|---|
| `HeroSection.tsx` | 138 | Headline + animated timetable + CTA | `AnimatedTimetable` embedded |
| `SocialProof.tsx` | 99 | Institution logo row + stats ("50+ Institutions") | Static |
| `FeatureGrid.tsx` | 207 | 6-feature card grid (icon + title + body) | `FEATURES` array |
| `PricingTable.tsx` | 240 | 3-tier pricing cards (Starter / Professional / Enterprise) | `preview?: boolean` — compact mode for homepage |
| `AnimatedTimetable.tsx` | 452 | CSS-animated timetable demo — auto-plays slot fill sequence | `isPlaying?: boolean` |
| `DemoRequestForm.tsx` | 209 | Contact/demo request form | Email + name + org + message fields; `zod` validation |
| `MarketingNav.tsx` | 203 | Responsive top nav — logo, nav links, Login/Get Demo CTAs, mobile hamburger | `useScrolled` for shadow on scroll |
| `MarketingFooter.tsx` | 140 | 4-column footer (Product / Company / Legal / Contact) + copyright | Static |

---

## 6. Context — `src/context/`

#### `src/context/AuthContext.tsx` — 132 lines
| Attribute | Value |
|---|---|
| Type | `'use client'` — React Context Provider |
| Exported hooks | `useAuth()` — returns `AuthContextType` |
| Rendered by | `Providers.tsx` |

**Imports**: `@/types` (User), `@/lib/api` (apiClient)

**`AuthContextType` interface**:
```typescript
{
  user: User | null          // current authenticated user
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  isLoading: boolean         // true during initial session check
  error: string | null       // last auth error message
}
```

**Key Implementation Patterns**:

**1. Synchronous localStorage init** (prevents blank screen flash):
```typescript
const [user, setUser] = useState<User | null>(() => {
  const stored = localStorage.getItem('user')
  return stored ? JSON.parse(stored) : null
})
```
First render already has user data — layout guards can immediate render AppShell instead of skeleton.

**2. React 18 StrictMode double-probe prevention**:
```typescript
const authChecked = useRef(false)
useEffect(() => {
  if (authChecked.current) return
  authChecked.current = true
  checkAuth()
}, [])
```
Prevents React 18 dev-mode running effects twice, which would cause two simultaneous `/auth/me` calls.

**3. Background session verification** (`checkAuth`):
- Calls `apiClient.getCurrentUser({ noRedirectOn401: true })`
- On success: updates user in state + localStorage (picks up server-side changes to user data)
- On 401/error: clears user from state + localStorage

**`login(username, password)`**:
1. `setIsLoading(true)`
2. `apiClient.login({ username, password })`
3. Success → destructure response, store `userWithoutPassword` in state + `localStorage.setItem('user', ...)`
4. Error → `setError(message)`, re-throw for caller

**`logout()`**:
1. `apiClient.logout()` — POST `/auth/logout/`, backend blacklists refresh token
2. `setUser(null)`, `localStorage.removeItem('user')`
3. Does NOT redirect — calling components handle navigation

---

## 7. Hooks — `src/hooks/`

#### `src/hooks/useProgress.ts` — 553 lines

**Exports**:

---

**`useProgress(jobId, onComplete?, onError?)`**

Subscribes to SSE stream for timetable generation job progress.

**Returns**:
```typescript
{
  progress: number            // 0–100 overall
  stage: string               // current stage ID
  message: string             // human-readable status message
  eta: number | null          // estimated seconds remaining
  isConnected: boolean        // SSE connection active
  isComplete: boolean
  isError: boolean
  errorMessage: string | null
  details: ProgressDetails    // per-stage substats
}
```

**SSE URL**: `GET /api/timetable/jobs/{jobId}/progress/` with `EventSource({ withCredentials: true })`

**Events listened**:
| Event | Handler |
|---|---|
| `connected` | Sets `isConnected = true` |
| `progress` | Updates all state from `JSON.parse(event.data)` |
| `done` | Sets `isComplete = true`, calls `onComplete?.(result)` |
| `error` | Sets `isError = true`, calls `onError?.(message)` |

**Reconnect logic** (exponential backoff):
```
delay = Math.min(1_000 * 2^attempt, 10_000)
if attempt >= 5: give up, setIsError(true)
```
Uses `reconnectCountRef` (not state) to avoid stale closures in `onerror`.

---

**`fetchProgressSnapshot(jobId)`**

One-shot HTTP `GET /api/timetable/jobs/{jobId}/progress/` — returns `Progress` object without SSE subscription. Used on page reload/refresh.

---

**`useSmoothProgress(actualProgress, config?)`**

Physics-based smooth animation of the progress bar.

**Returns**: `smoothProgress: number` — 60 FPS animated value chasing `actualProgress`

**Physics model** (runs in `requestAnimationFrame`):
```
velocity += (target - current) * acceleration  // Hooke's law spring
velocity *= damping                            // 0.78 by default
current  += velocity
```

**Constraints**:
- Monotonic: `current` never decreases (even if `actualProgress` momentarily dips)
- Cap: `current ≤ target` (never exceeds backend-provided value)
- Completion easing: when `target = 100`, switches to `cubic-ease-out` over 600ms

**Default config**: `{ acceleration: 0.12, damping: 0.78 }`

---

**`useSmoothedETA(actualETA, alpha?)`**

Exponential smoothing for ETA display — prevents jumpy ETA numbers.

```
smoothedETA = alpha * actualETA + (1 - alpha) * previousSmoothedETA
```
Default `alpha = 0.15` (aggressive smoothing — small changes have little visible effect).

---

**`formatETA(seconds: number | null): string`**

| Input | Output |
|---|---|
| `null` | `"Calculating..."` |
| `< 60` | `"30s"` |
| `60–3599` | `"2m 30s"` |
| `>= 3600` | `"1h 5m"` |

---

**`getStageDisplayName(stage: string): string`**

| Internal stage | Display name |
|---|---|
| `initializing` | Preparing Schedule |
| `clustering` | Organizing Courses |
| `cpsat_solving` | Building Schedule |
| `ga_optimization` | Optimizing Schedule |
| `rl_refinement` | Finalizing Schedule |
| `variant_generation` | Generating Variants |
| `completed` | Schedule Ready |
| *(anything else)* | Capitalized + spaces for underscores |

---

#### `src/hooks/useScrollReveal.ts` — 66 lines

**`useScrollReveal(threshold?: number, once?: boolean)`**

Uses `IntersectionObserver` to trigger CSS reveal animations when elements enter the viewport.

**Returns**: `{ ref: RefObject<Element>, visible: boolean }`

**Parameters**:
- `threshold` (default `0.1`) — `0.0` = any pixel, `1.0` = fully visible
- `once` (default `true`) — if true, stops observing after first intersection

**Usage**:
```tsx
const { ref, visible } = useScrollReveal(0.2)
return <div ref={ref} className={visible ? 'fade-in' : 'opacity-0'}> ... </div>
```

---

**`useCountUp(target: number, duration?: number, trigger?: boolean)`**

Animates an integer counter from 0 to `target` using `requestAnimationFrame`.

**Returns**: `currentValue: number`

**Parameters**:
- `duration` (default `2000`) — animation duration in ms
- `trigger` (default `true`) — starts animation immediately; pass `visible` from `useScrollReveal` to delay start until in view

**Easing**: Cubic ease-out — fast start, slow finish. Formula: `easedT = 1 - (1-t)^3`

---

## 8. Lib — `src/lib/`

#### `src/lib/api.ts` — 606 lines

**`API_BASE_URL`**: `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'`

**Class `ApiClient`**:

**`request<T>(endpoint, options?)`** (private base method):
```typescript
options defaults:
  credentials: 'include'       // sends HttpOnly cookies
  headers: { 'Content-Type': 'application/json' }
  noRedirectOn401: false       // if true, returns null instead of redirecting
```

**401 handling**:
1. Call `refreshToken()` → POST `/auth/refresh/`
2. If refresh succeeds → retry original request once
3. If refresh fails → `window.location.href = '/login'`
4. If `noRedirectOn401=true` → skip redirect, return `null`

**Complete method reference**:

*Auth*
| Method | Endpoint | Description |
|---|---|---|
| `login(data)` | POST `/auth/login/` | Sets HttpOnly cookie; returns `{ user, … }` |
| `logout()` | POST `/auth/logout/` | Blacklists refresh token |
| `getCurrentUser(opts?)` | GET `/auth/user/` | Verifies session; accepts `noRedirectOn401` |

*Users / Admins*
| Method | Endpoint |
|---|---|
| `getUsers(page, search)` | GET `/users/` |
| `getUser(id)` | GET `/users/{id}/` |
| `createUser(data)` | POST `/users/` |
| `updateUser(id, data)` | PATCH `/users/{id}/` |
| `deleteUser(id)` | DELETE `/users/{id}/` |

*Departments*: `getDepartments`, `getDepartment(id)`, `createDepartment`, `updateDepartment`, `deleteDepartment`  
*Buildings*: `getBuildings`, `getBuilding(id)`, `createBuilding`, `updateBuilding`, `deleteBuilding`  
*Schools*: `getSchools`, `getSchool(id)`, `createSchool`, `updateSchool`, `deleteSchool`  
*Programs*: `getPrograms`, `getProgram(id)`, `createProgram`, `updateProgram`, `deleteProgram`  
*Courses*: `getCourses`, `getCourse(id)`, `createCourse`, `updateCourse`, `deleteCourse`  
*Subjects*: `getSubjects`, `getSubject(id)`, `createSubject`, `updateSubject`, `deleteSubject`  
*Faculty*: `getFaculty(page?, search?)`, `getFacultyMember(id)`, `createFaculty`, `updateFaculty`, `deleteFaculty`  
*Students*: `getStudents(page?, search?)`, `getStudent(id)`, `createStudent`, `updateStudent`, `deleteStudent`  
*Rooms*: `getRooms`, `getRoom(id)`, `createRoom`, `updateRoom`, `deleteRoom` + aliases `getClassrooms`, `createClassroom`, `updateClassroom`, `deleteClassroom`  
*Labs*: `getLabs`, `getLab(id)`, `createLab`, `updateLab`, `deleteLab`  

*Timetables*
| Method | Endpoint | Description |
|---|---|---|
| `getTimetables(filters?)` | GET `/timetable/workflows/` | List with optional status/dept filter |
| `getTimetable(id)` | GET `/timetable/workflows/{id}/` | |
| `getTimetableSlots(id)` | GET `/timetable/workflows/{id}/slots/` | |
| `generateTimetable(data)` | POST `/timetable/generate/` | Starts generation job; returns `{job_id}` |
| `getGenerationJobs()` | GET `/timetable/jobs/` | |
| `getGenerationJob(id)` | GET `/timetable/jobs/{id}/` | |

**Export**: `export default new ApiClient(API_BASE_URL)` — singleton `apiClient`

---

#### `src/lib/auth.ts` — 91 lines

**`authenticatedFetch(url, options)`**:
- Wrapper around `fetch` with `credentials: 'include'`
- On 401: calls `refreshAccessTokenViaCookie()` → retries once
- On second 401: throws error

**`refreshAccessTokenViaCookie()`** (internal singleton promise):
```typescript
// Prevents parallel refresh races via promise deduplication:
if (refreshPromise) return refreshPromise
refreshPromise = fetch('/api/auth/refresh/', { method:'POST', credentials:'include' })
  .finally(() => { refreshPromise = null })
```

**`storeTokens()`**: No-op stub — tokens live in HttpOnly cookies, not accessible to JS.

---

#### `src/lib/exportUtils.ts` — 299 lines

**Imports**: `jspdf`, `html2canvas`, `xlsx`, `file-saver`

| Function | Parameters | Description |
|---|---|---|
| `exportTimetableToPDF(elementId, slots, options)` | `elementId: string`, `slots: TimetableSlotDetailed[]`, `options: ExportOptions` | `html2canvas(document.getElementById(elementId))` → `new jsPDF('landscape', 'mm', 'a4')` → `.addImage()` → `.save(filename.pdf)` |
| `exportTimetableToExcel(slots, options)` | `slots`, `options` | `xlsx.utils.book_new()` + "Timetable" worksheet (rows: day/time/subject/faculty/room/batch) + "Information" worksheet (metadata: dept, semester, year) → `xlsx.writeFile()` |
| `exportTimetableToCSV(slots, options)` | `slots`, `options` | BOM `\uFEFF` prefix + comma-separated with quoted fields → `FileSaver.saveAs(new Blob([csv]), filename.csv)` |
| `exportTimetableToICS(slots, options)` | `slots`, `options` | Builds `VCALENDAR` string with `VEVENT` blocks containing `RRULE:FREQ=WEEKLY;BYDAY={day}` → `FileSaver.saveAs(blob, filename.ics)` |

---

#### `src/lib/validations.ts` — 470 lines

All schemas use Zod `z.object({…})`. Exported as schema + inferred type.

| Schema | Type | Key Rules |
|---|---|---|
| `loginSchema` | `LoginFormData` | `username` required, `password` required |
| `userSchema` | `UserFormData` | username 3–150 chars alphanum+`_`, email format, password ≥8 chars (upper+lower+digit), role enum, is_active boolean |
| `simpleFacultySchema` | `SimpleFacultyInput` | faculty_id uppercase alphanumeric, designation enum (5 values), max_workload 1–40, phone exactly 10 digits |
| `simpleStudentSchema` | `SimpleStudentInput` | student_id, year 1–5, semester 1–10 |
| `departmentSchema` | `DepartmentFormData` | dept_id, dept_name, building_name optional |
| `courseSchema` | `CourseFormData` | duration_years 1–6, level enum (UG/PG/PhD/Diploma) |
| `subjectSchema` | `SubjectFormData` | credits 1–10, lecture_hours 0–12, lab_hours 0–12 |
| `classroomSchema` | `ClassroomFormData` | capacity 1–500, room_type enum |
| `labSchema` | `LabFormData` | capacity 1–300, equipment text |
| `batchSchema` | `BatchFormData` | year 2020–2030, student_count 1–200 |
| `timetableGenerationSchema` | — | department_ids `string[]` non-empty, working_days `string[]`, constraints object with max_daily_load etc. |

---

#### `src/lib/utils.ts` — 5 lines
```typescript
import { clsx, ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)) }
```
`cn()` merges Tailwind classes, resolving conflicts (e.g. `cn('px-4', 'px-2')` → `'px-2'`).

---

#### `src/lib/api/timetable.ts` — 38 lines
Timetable-specific API calls supplementing `apiClient`:
- `getTimetableVariants(jobId)` → GET `/timetable/variants/?job_id={jobId}`
- `getTimetableEntries(variantId)` → GET `/timetable/variants/{id}/entries/`
- `selectVariant(variantId)` → POST `/timetable/variants/{id}/select/`
- `approveTimetable(workflowId, reviewData)` → POST `/timetable/workflows/{id}/review/`

---

#### `src/lib/api/timetable-variants.ts` — 108 lines

| Function | Endpoint | Description |
|---|---|---|
| `fetchVariants(jobId)` | GET `/timetable/variants/?job_id={jobId}` | All variants for a job |
| `fetchVariantEntries(variantId)` | GET `/timetable/variants/{id}/entries/` | All timetable entry slots |
| `selectVariant(variantId)` | POST `/timetable/variants/{id}/select/` | Mark as selected variant |
| `compareVariants(id1, id2)` | GET `/timetable/variants/compare/?v1={id1}&v2={id2}` | Returns `VariantComparisonData` |
| `fetchWorkflows(page, status?)` | GET `/timetable/workflows/` | Paginated workflow list |
| `approveWorkflow(id, data)` | POST `/timetable/workflows/{id}/review/` | `data: { action: 'approve'\|'reject', reason?: string }` |

---

## 9. Types — `src/types/`

#### `src/types/index.ts` — 13 lines

```typescript
export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'org_admin' | 'super_admin' | 'faculty' | 'student'
  first_name?: string
  last_name?: string
  organization?: string        // organization UUID/ID
  department?: string          // department UUID/ID
  organization_name?: string   // display name
  department_name?: string     // display name
}
```

---

#### `src/types/timetable.ts` — 382 lines

**Generation / Job**:
```typescript
GenerationJob        { id, status, progress, current_stage, message, eta_seconds, timetable_data, error }
GenerateTimetableRequest  { name, department_ids[], course_ids[], start_date, end_date, working_days[], constraints, fixed_slots? }
GenerateTimetableResponse { job_id, workflow_id, estimated_time_seconds, websocket_url }
```

**Workflow / Variant**:
```typescript
TimetableWorkflow    { id, name, status, created_by, created_at, variants[], ...review metadata }
TimetableVariant     { id, variant_number, overall_score, conflict_count, room_utilization, faculty_workload_balance, is_selected, entries[] }
```

**Timetable Entries**:
```typescript
TimetableEntry       { day: string, start_time, end_time, subject_name, faculty_name, batch_name, classroom_name, is_lab, is_elective }
BackendTimetableEntry { day: 0–5 (Mon–Sat), time_slot: "09:00-10:00", subject_id, faculty_id, classroom_id, batch_id }
```

**Reviews & Approval**:
```typescript
TimetableReview      { id, reviewer_name, review_type: 'approve'|'request_changes'|'reject', comments, created_at }
ApprovalRequest      { action: 'approve'|'reject', reason?: string }
WorkflowListItem     { id, name, department_name, semester, academic_year, status, submitted_by, submitted_at, conflict_count }
```

**Infrastructure**:
```typescript
FixedSlot    { day, time_slot, subject_id, faculty_id, classroom_id, batch_id }
Shift        { name, start_time, end_time, working_days: string[] }
```

**UI Types**:
```typescript
TimetableListItem      { id, name, year, batch, department_name, semester, status, score, conflicts, created_at }
VariantScoreCard       { overall_score, faculty_load_score, room_utilization_score, student_gap_score, labels }
TimetableSlotDetailed  { ...TimetableEntry, subject_code, credits, faculty_designation, room_capacity, enrolled_count, conflicts: ConflictItem[] }
```

**Conflict Detection**:
```typescript
ConflictItem         { type: string, severity: 'critical'|'high'|'medium'|'low', day, time_slot, message, suggestion }
ConflictDetectionResult { conflicts: ConflictItem[], critical_count, high_count, total_count, acknowledged_indices: number[] }
ComparisonResult     { shared_slots[], changed_slots[], added_slots[], removed_slots[], metrics }
VariantComparisonData { variants: TimetableVariant[], comparison_metrics: { best_score, score_range, avg_conflicts } }
```

**Legacy (backwards compat)**:
```typescript
Timetable     { id, name, status, department, semester, year, created_at, updated_at }
TimetableSlot { id, day, period, subject, faculty, room }
```

---

#### `src/types/css.d.ts` — 12 lines
CSS module type declarations:
```typescript
declare module '*.module.css' { const styles: Record<string, string>; export default styles }
declare module '*.module.scss' { ... }
```

---

## 10. Rendering & Data-Flow Diagram

```
Browser Request
      │
      ▼
Next.js App Router (SSR → hydration)
      │
      ├── / and /blog /pricing /product /company /contact /legal/* 
      │     └── (marketing)/layout.tsx → MarketingNav + {page} + MarketingFooter
      │
      ├── /login
      │     └── (auth)/login/page.tsx  [Client]
      │           └── useAuth().login()
      │                 └── apiClient.login() → POST /auth/login/
      │                       └── Django sets HttpOnly JWT cookies
      │                             └── router.push(ROLE_DASHBOARD[role])
      │
      ├── /admin/*  ──────────────────────────── admin/layout.tsx [Client]
      │     │             isLoading → AppShellSkeleton
      │     │             wrong role → /unauthorized
      │     │             correct → AppShell (role=admin|org_admin|super_admin)
      │     │
      │     ├── /admin/dashboard     → fetches /faculty/ /students/ /timetables/
      │     │                          renders recharts graphs + stat tiles
      │     ├── /admin/admins        → DataTable ↔ UserDetailPanel swap
      │     ├── /admin/faculty       → DataTable ↔ FacultyDetailPanel swap
      │     ├── /admin/students      → DataTable ↔ StudentDetailPanel swap
      │     ├── /admin/academic/*    → each page: DataTable + modal CRUD form
      │     ├── /admin/timetables    → list/grid → VariantCard/VariantGrid
      │     │   ├── /new             → multi-step wizard → POST /timetable/generate/
      │     │   │                      → job_id → SSE useProgress → smooth bar
      │     │   ├── /status/:jobId   → SSE progress display + stage name
      │     │   └── /:id/review      → CompareGrid + approve/reject
      │     ├── /admin/approvals     → WorkflowListItem table + approve/reject
      │     └── /admin/logs          → static mock audit log table
      │
      ├── /faculty/* ─────────────────────────── faculty/layout.tsx [Client]
      │     │             role check: 'faculty' only
      │     ├── /faculty/dashboard   → today's schedule + workload + notifications
      │     ├── /faculty/preferences → availability matrix form
      │     └── /faculty/schedule    → TimetableGrid (week view) + export
      │
      └── /student/* ─────────────────────────── student/layout.tsx [Client]
            │             role check: 'student' only
            ├── /student/dashboard   → attendance widgets + GPA chart + today's classes
            └── /student/timetable   → TimetableGrid (read-only) + export

═══════════════ State Flow ═══════════════════════════════════════════════════

Component
  └── useAuth()  [AuthContext]        ← user, isLoading
  └── apiClient.METHOD()             [lib/api.ts]
       └── fetch(url, credentials:'include')
            └── Django REST API :8000/api/
             ┌── 200 → parse JSON → update state
             └── 401 → apiClient.refreshToken() → POST /auth/refresh/
                    ├── Success → retry original request
                    └── Error   → window.location = '/login'

═══════════════ Real-time Progress Flow ══════════════════════════════════════

POST /timetable/generate/ → { job_id }
  └── useProgress(jobId)
       └── EventSource(GET /timetable/jobs/{jobId}/progress/, { withCredentials:true })
            ├── 'progress' event → { progress, stage, eta, message }
            │    └── useSmoothProgress(progress) → requestAnimationFrame physics
            │    └── useSmoothedETA(eta)          → exponential smoothing display
            └── 'done' event → onComplete(result) → router.push(nextStep)
```

---

## 11. Authentication & Route-Guard Architecture

```
┌─── src/components/Providers.tsx ────────────────────────────────────────┐
│                                                                          │
│  ThemeProvider (next-themes)                                             │
│    NavigationProgress (always mounted, not affected by auth errors)      │
│    ErrorBoundary                                                         │
│      ToastProvider                                                       │
│        AuthProvider (src/context/AuthContext.tsx)                        │
│          {children}                                                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─── AuthContext Init Sequence ────────────────────────────────────────────┐
│                                                                          │
│  1. useState initializer runs SYNCHRONOUSLY:                             │
│     → reads localStorage('user')                                         │
│     → if present: user = JSON.parse(stored)  (no blank flash!)          │
│     → if absent:  user = null                                            │
│                                                                          │
│  2. useEffect runs ONCE (React 18 StrictMode safe via ref guard):        │
│     → apiClient.getCurrentUser({ noRedirectOn401: true })                │
│     → On 200: setUser(serverUser) + update localStorage                  │
│     → On 401: setUser(null) + clear localStorage                         │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─── Route Guard (each layout file) ───────────────────────────────────────┐
│                                                                          │
│  const { user, isLoading } = useAuth()                                   │
│                                                                          │
│  if (isLoading)              → <AppShellSkeleton />                      │
│  if (!user)                  → redirect('/login')                        │
│  if (role not allowed)       → redirect('/unauthorized')                 │
│  else                        → <AppShell>{children}</AppShell>           │
│                                                                          │
│  Allowed roles:                                                          │
│    admin/layout.tsx   → admin | org_admin | super_admin                  │
│    faculty/layout.tsx → faculty                                          │
│    student/layout.tsx → student                                          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─── Token Architecture ───────────────────────────────────────────────────┐
│                                                                          │
│  Access Token  → HttpOnly cookie (not accessible to JS)                  │
│  Refresh Token → HttpOnly cookie (not accessible to JS)                  │
│                                                                          │
│  localStorage stores ONLY:                                               │
│    'user' → { id, username, email, role, first_name, ... }               │
│    (no tokens, no sensitive data)                                        │
│                                                                          │
│  On 401 from any API call:                                               │
│    apiClient.refreshToken() → POST /auth/refresh/                        │
│    Backend: validates refresh cookie → rotates access token cookie       │
│    If refresh fails → window.location.href = '/login'                    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 12. CSS Architecture

`src/app/globals.css` — 1 445 lines — is the single CSS source of truth for the entire app.

### Structure

| Section | Approx Lines | Description |
|---|---|---|
| Tailwind directives | 1–5 | `@tailwind base / components / utilities` |
| CSS Custom Properties — Light | 10–145 | All design tokens for light mode |
| CSS Custom Properties — Dark | 146–305 | `[data-theme="dark"]` overrides |
| Button components | 305–380 | `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-danger` |
| Form components | 380–450 | `.input-primary`, `.label`, `.form-error` |
| Badge components | 450–520 | `.badge`, `.badge-success`, `.badge-warning`, `.badge-error`, `.badge-info`, `.badge-purple` |
| Table styles | 520–640 | `.table-row`, `.table-cell`, `.bulk-toolbar` + CSS var overrides |
| Card & layout | 640–720 | `.card-hover`, `.section-card`, `.page-title` |
| Avatar system | 720–760 | `.avatar-font` CSS font-family declaration |
| Skeleton loader | 760–800 | `.loading-skeleton` + `@keyframes shimmer` |
| Scrollbar | 800–840 | `.profile-scroll` (6px thumb, `max-height:280px`), `.scrollbar-hide` |
| Keyframe animations | 840–1000 | `@keyframes progress-fill`, `progress-fill-breathe`, `profileLoad`, `progress-breathe`, `slide-in-right`, `slide-in-up`, `fade-in` |
| Marketing variables | 1000–1100 | `--cadence-*` color tokens, `.cadence-gradient` |
| Marketing components | 1100–1300 | `.mk-section`, `.mk-h2`, `.mk-h3`, `.mk-body`, `.mk-feature-card`, `.mk-cta-lift`, `.mk-nav` etc. |
| Responsive helpers | 1300–1445 | Media queries for marketing site breakpoints |

---

### Key Design Tokens (Light Mode)

| Token | Value | Usage |
|---|---|---|
| `--color-primary` | `#1a73e8` | Buttons, active nav, links, progress bar |
| `--color-primary-hover` | `#1557b0` | Button hover |
| `--color-bg` | `#f0f4f9` | App background (Google-style light blue-grey) |
| `--color-bg-surface` | `#ffffff` | Cards, table background |
| `--color-bg-surface-2` | `#f1f3f4` | Table headers, secondary panels |
| `--color-text-primary` | `#202124` | Main body text |
| `--color-text-secondary` | `#5f6368` | Labels, captions |
| `--color-text-placeholder` | `#9aa0a6` | Input placeholders |
| `--color-border` | `#dadce0` | Dividers, input borders |
| `--color-danger` | `#d93025` | Error, delete actions |
| `--color-success` | `#188038` | Success, approved status |
| `--color-warning` | `#f9ab00` | Warning, pending status |
| `--color-nav-active` | `#d3e3fd` | Active sidebar item background |
| `--radius-sm` | `8px` | Input fields, small buttons |
| `--radius-md` | `12px` | Modal sub-sections |
| `--radius-lg` | `16px` | Cards |
| `--radius-xl` | `20px` | Content cards (AppShell) |
| `--radius-pill` | `9999px` | Badges, status chips |
| `--row-height` | `52px` | DataTable comfortable row height |
| `--row-header-height` | `44px` | DataTable header row height |
| `--row-hover-bg` | `rgba(26,115,232,0.04)` | Row hover background |
| `--row-selected-bg` | `rgba(26,115,232,0.08)` | Selected row background |
| `--checkbox-color` | `#1a73e8` | DataTable checkbox accent |
| `--col-header-color` | `#5f6368` | Table header text color |
| `--col-header-size` | `11px` | Table header font size (uppercase label style) |

### Key Animation Keyframes

| Name | Description | Used by |
|---|---|---|
| `shimmer` | `translateX(-100% → 100%)` gradient sweep | `.loading-skeleton` for all skeleton loaders |
| `progress-fill` | `scaleX(0 → 1)` with cubic-bezier | Login card progress bar |
| `progress-fill-breathe` | `scaleX(0 → 0.8 → 0.9 → 0.8)` pulsing | Breathe mode for progress |
| `profileLoad` | `left:-30% → left:100%` indeterminate sweep | ProfileDropdown loading bar (while user=null) |
| `progress-breathe` | opacity + scale pulse | Progress bar "alive" indicator |
| `slide-in-right` | `translateX(100% → 0) + opacity` | SlotDetailPanel (slide-in panel) |
| `slide-in-up` | `translateY(20px → 0) + opacity` | Modal/card entrance |
| `fade-in` | `opacity 0 → 1` | Generic fade |

### CSS Component Classes

| Class | Description |
|---|---|
| `.btn-primary` | Blue filled button — `bg-[--color-primary] text-white hover:bg-[--color-primary-hover]` |
| `.btn-secondary` | Outlined — `border border-[--color-border] text-[--color-text-primary] hover:bg-[--color-bg-surface-2]` |
| `.btn-ghost` | No border — `text-[--color-primary] hover:bg-[--color-nav-active]` |
| `.btn-danger` | Red — `bg-[--color-danger] text-white` |
| `.input-primary` | Form input — `border border-[--color-border] rounded-[--radius-sm] focus:ring-2 focus:ring-[--color-primary]` |
| `.badge` | Base pill — `inline-flex rounded-full px-2 py-0.5 text-xs font-medium` |
| `.badge-success` | Green badge |
| `.badge-warning` | Yellow/amber badge |
| `.badge-error` | Red badge |
| `.badge-info` | Blue badge |
| `.loading-skeleton` | Shimmer block — `bg-gradient-to-r from-surface-2 via-white to-surface-2 animate-[shimmer_1.5s_infinite]` |
| `.profile-scroll` | ProfileDropdown scroll area — `max-height:280px; overflow-y:auto; scrollbar-width:thin` |
| `.avatar-font` | `font-family: 'Google Sans', 'Product Sans', Roboto, sans-serif` |
| `.scrollbar-hide` | `scrollbar-width:none; &::-webkit-scrollbar { display:none }` |
| `.table-row` | DataTable row base — height `var(--row-height)`, hover `var(--row-hover-bg)` |
| `.table-cell` | DataTable cell — padding, border-bottom, text size |
