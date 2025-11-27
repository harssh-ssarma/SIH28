# Conflict Detection Dashboard - Implementation Complete

## Overview
Minimal conflict detection system with severity indicators, alerts, and resolution suggestions.

## Features

### 1. Conflict Detection
- **Faculty Conflicts**: Faculty assigned to multiple classes simultaneously
- **Room Conflicts**: Room double-booked with multiple classes
- **Student Conflicts**: Students enrolled in overlapping classes (future)
- **Capacity Violations**: Room capacity exceeded (future)

### 2. Severity Levels
- **Critical** (Red): Hard constraint violations (faculty/room conflicts)
- **High** (Orange): Major scheduling issues
- **Medium** (Yellow): Minor scheduling issues
- **Low** (Blue): Optimization opportunities

### 3. Resolution Suggestions
- Automatic suggestions for each conflict type
- Context-aware recommendations
- Multiple resolution options

## Implementation Files

### Backend

#### 1. Conflict Detection Service
**File**: `backend/django/academics/conflict_service.py`
- `ConflictDetectionService`: Main detection logic
- `detect_conflicts()`: Detects all conflicts in timetable
- `categorize_conflicts()`: Groups by type and severity
- `get_resolution_suggestions()`: Generates suggestions

#### 2. Conflict API Views
**File**: `backend/django/academics/conflict_views.py`
- `ConflictViewSet`: REST API endpoints
- `detect()`: Detect conflicts for job/variant
- `summary()`: Get conflict summary for all variants
- `suggest()`: Get resolution suggestions

#### 3. URL Configuration
**File**: `backend/django/academics/urls.py`
- Added conflict routes to router

### Frontend

#### 1. Conflict Dashboard Page
**File**: `frontend/src/app/admin/timetables/[timetableId]/conflicts/page.tsx`
- Summary cards with counts by severity
- Filter buttons (All, Critical, High, Medium, Low)
- Conflict cards with details and suggestions
- Responsive design

## API Endpoints

### 1. Detect Conflicts
```
GET /api/conflicts/detect/?job_id={job_id}&variant_id={variant_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "variant_id": 0,
  "conflicts": [
    {
      "type": "faculty_conflict",
      "severity": "critical",
      "day": "Monday",
      "time_slot": "09:00-10:00",
      "faculty": "Dr. Smith",
      "courses": ["CS101", "CS102"],
      "rooms": ["A101", "A102"],
      "message": "Dr. Smith assigned to 2 classes simultaneously",
      "suggestion": "Reschedule CS101 to different time slot"
    }
  ],
  "summary": {
    "total": 10,
    "critical": 5,
    "high": 3,
    "medium": 2,
    "low": 0
  }
}
```

### 2. Get Summary
```
GET /api/conflicts/summary/?job_id={job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "variants": [
    {
      "variant_id": 0,
      "total_conflicts": 10,
      "critical": 5,
      "high": 3,
      "medium": 2,
      "low": 0
    }
  ]
}
```

### 3. Get Suggestions
```
POST /api/conflicts/suggest/
Body: { "conflict": {...} }
```

**Response:**
```json
{
  "conflict": {...},
  "suggestions": [
    "Reschedule CS101 to different time slot",
    "Assign substitute faculty for CS102",
    "Swap time slots with another class"
  ]
}
```

## Usage

### 1. Access Dashboard
Navigate to: `/admin/timetables/{timetableId}/conflicts`

### 2. View Summary
- Total conflicts displayed at top
- Breakdown by severity (Critical, High, Medium, Low)

### 3. Filter Conflicts
- Click severity buttons to filter
- "All" shows all conflicts

### 4. Review Conflicts
Each conflict card shows:
- Severity badge (color-coded)
- Conflict type badge
- Day and time slot
- Affected resources (faculty, room, courses)
- Suggested resolution

### 5. Resolve Conflicts
- Read suggested resolution
- Manually adjust timetable
- Re-generate to verify fix

## Conflict Types

### Faculty Conflict
**Detected When**: Faculty assigned to 2+ classes at same time
**Severity**: Critical
**Suggestions**:
- Reschedule one class to different time slot
- Assign substitute faculty
- Swap time slots with another class

### Room Conflict
**Detected When**: Room booked for 2+ classes at same time
**Severity**: Critical
**Suggestions**:
- Move one class to available room
- Use online/hybrid mode
- Split class into smaller sections

### Student Conflict (Future)
**Detected When**: Student enrolled in 2+ classes at same time
**Severity**: High
**Suggestions**:
- Offer course in different semester
- Create additional section
- Allow student to take course later

## Color Coding

| Severity | Color | Border | Badge |
|----------|-------|--------|-------|
| Critical | Red | `border-red-500` | `bg-red-500` |
| High | Orange | `border-orange-500` | `bg-orange-500` |
| Medium | Yellow | `border-yellow-500` | `bg-yellow-500` |
| Low | Blue | `border-blue-500` | `bg-blue-500` |

## Performance

- **Caching**: 10-minute cache for conflict detection
- **Limit**: Max 100 conflicts returned per request
- **Fast Detection**: O(n) time complexity
- **Lazy Loading**: Conflicts loaded on-demand

## Testing

### Test Conflict Detection
```bash
curl -X GET "http://localhost:8000/api/conflicts/detect/?job_id=123&variant_id=0" \
  -H "Authorization: Bearer <token>"
```

### Test Summary
```bash
curl -X GET "http://localhost:8000/api/conflicts/summary/?job_id=123" \
  -H "Authorization: Bearer <token>"
```

### Test Suggestions
```bash
curl -X POST "http://localhost:8000/api/conflicts/suggest/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"conflict": {"type": "faculty_conflict", "severity": "critical"}}'
```

## Future Enhancements

1. **Auto-Resolution**: Automatically resolve conflicts using AI
2. **Conflict Prevention**: Detect conflicts during generation
3. **Batch Resolution**: Resolve multiple conflicts at once
4. **Conflict History**: Track resolved conflicts
5. **Email Alerts**: Notify stakeholders of critical conflicts
6. **Export Reports**: PDF/Excel export of conflicts
7. **Student Conflicts**: Detect student enrollment conflicts
8. **Capacity Violations**: Check room capacity vs enrollment

## Integration

### Add Conflict Link to Review Page
```tsx
<Link href={`/admin/timetables/${timetableId}/conflicts`}>
  <button className="px-4 py-2 bg-red-600 text-white rounded">
    View Conflicts ({conflictCount})
  </button>
</Link>
```

### Show Conflict Badge
```tsx
{conflictCount > 0 && (
  <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full">
    {conflictCount} conflicts
  </span>
)}
```

## Status
✅ **IMPLEMENTED** - Conflict detection dashboard with severity indicators and resolution suggestions
