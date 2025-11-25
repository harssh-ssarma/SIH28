# Frontend Updates - Timetable Pages

## Changes Made

### 1. Timetable Generation Page (`/admin/timetables/new`)

**File**: `frontend/src/app/admin/timetables/new/page.tsx`

#### New Features:
- **Configuration Loading**: Automatically loads last used configuration from backend on page load
- **Configuration Saving**: Saves user preferences to database before generating timetable
- **Comprehensive Form**: Added multiple configuration sections:

##### Basic Settings
- Academic Year (dropdown)
- Semester (dropdown)

##### Time Configuration
- Working Days (5-7 days)
- Slots Per Day (6-12 slots)
- Start Time (time picker)
- End Time (time picker)
- Lunch Break Toggle with start/end times

##### Constraints
- Max Classes Per Day (4-8)
- Faculty Max Continuous Classes (2-5)

##### Optimization
- Priority (Balanced, Minimize Conflicts, Maximize Utilization)
- Number of Variants (1-10)
- Timeout in seconds (15-60)
- Minimize Faculty Travel checkbox

#### Technical Changes:
- Added `useEffect` to load configuration on mount
- Added `loadLastConfig()` function to fetch from `/api/academics/timetable-configs/last_used/`
- Updated `handleSubmit()` to save configuration before generation
- Added loading state while fetching configuration
- Organized form into collapsible card sections

---

### 2. Timetables Listing Page (`/admin/timetables`)

**File**: `frontend/src/app/admin/timetables/page.tsx`

#### Layout Changes:
- **Two-Column Layout**: 
  - Left column (2/3 width): Timetables list with tabs and cards
  - Right column (1/3 width): Faculty availability sidebar
- **Sticky Sidebar**: Faculty list stays visible while scrolling timetables
- **No More Scrolling**: Both sections visible simultaneously on desktop

#### Faculty Sidebar Features:
- Compact card design with smaller toggles
- Scrollable list with max-height
- Shows available count in header
- Hover effects on faculty items
- Initials in circular avatars (2 letters max)

#### Responsive Design:
- Desktop (lg+): Side-by-side layout
- Mobile/Tablet: Stacked layout (faculty below timetables)

---

### 3. API Service Updates

**File**: `frontend/src/lib/api/timetable.ts`

#### New Functions:
```typescript
// Fetch last used configuration
fetchLastTimetableConfig(): Promise<any>

// Save new configuration
saveTimetableConfig(config: any): Promise<any>
```

#### Endpoints:
- `GET /api/academics/timetable-configs/last_used/` - Get last used config
- `POST /api/academics/timetable-configs/` - Save new config

---

## Backend Requirements

### Already Implemented:
✅ `TimetableConfiguration` model
✅ `TimetableConfigurationSerializer`
✅ `TimetableConfigurationViewSet` with `last_used()` action
✅ URL routing for `/api/academics/timetable-configs/`

### Required Migration:
```bash
cd backend/django
python manage.py makemigrations academics
python manage.py migrate academics
```

---

## User Experience Improvements

### Before:
- Simple form with only academic year and semester
- Faculty availability required scrolling down
- No configuration persistence
- Manual settings each time

### After:
- Comprehensive configuration form with all options
- Side-by-side layout - no scrolling needed
- Configuration auto-loads from last use
- Settings saved to database
- Better organization with card sections
- Sticky faculty sidebar on desktop

---

## Testing Checklist

- [ ] Load `/admin/timetables/new` - should load last config
- [ ] Change settings and submit - should save config
- [ ] Reload page - should show previously saved settings
- [ ] View `/admin/timetables` - should show side-by-side layout
- [ ] Toggle faculty availability - should update immediately
- [ ] Scroll timetables - faculty sidebar should stay visible
- [ ] Test on mobile - should stack vertically
- [ ] Verify all form validations work
- [ ] Check time picker inputs
- [ ] Test checkbox toggles

---

## Configuration Fields

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| working_days | number | 6 | 5-7 | Number of working days per week |
| slots_per_day | number | 9 | 6-12 | Time slots per day |
| start_time | time | 08:00 | - | Day start time |
| end_time | time | 17:00 | - | Day end time |
| lunch_break_enabled | boolean | true | - | Enable lunch break |
| lunch_break_start | time | 12:00 | - | Lunch break start |
| lunch_break_end | time | 13:00 | - | Lunch break end |
| max_classes_per_day | number | 6 | 4-8 | Max classes per student per day |
| faculty_max_continuous | number | 3 | 2-5 | Max continuous classes for faculty |
| optimization_priority | string | balanced | - | Optimization strategy |
| minimize_travel | boolean | true | - | Minimize faculty building travel |
| number_of_variants | number | 5 | 1-10 | Number of timetable variants |
| timeout_seconds | number | 30 | 15-60 | Generation timeout |

---

## Next Steps

1. Run migrations to create `TimetableConfiguration` table
2. Test the new generation form
3. Verify configuration persistence
4. Test responsive layout on different screen sizes
5. Consider adding configuration presets (e.g., "Quick", "Balanced", "Thorough")
6. Add tooltips to explain each configuration option
7. Consider adding a "Reset to Defaults" button
