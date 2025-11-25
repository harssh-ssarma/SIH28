# NEP 2020 Compliant Timetable Architecture

## Problem Statement

Traditional timetable systems are **year-based** and **batch-based**:
- "1st Year Section A", "2nd Year Section B", etc.
- Assumes students in Year 1 only take Year 1 courses
- Rigid structure incompatible with NEP 2020

## NEP 2020 Reality

### Student-Centric Enrollment
- **No fixed batches**: Students enroll in individual courses
- **Cross-year enrollment**: 4th year student can take 1st year course (if prerequisite met)
- **Interdisciplinary**: CS student can take Mechanical Engineering elective
- **Flexible credits**: Students choose their own course combinations

### Example Scenario
```
Course: CS101 - Introduction to Programming
Semester: Odd 2024-2025
Enrolled Students:
  - S001 (1st year, CS)
  - S045 (2nd year, CS - failed last year, retaking)
  - S123 (3rd year, ME - taking as elective)
  - S234 (4th year, EE - interdisciplinary credit)
```

## New Architecture: Course-Centric Timetabling

### 1. Data Model Changes

#### Old Model (Batch-Centric)
```typescript
interface Timetable {
  batch_id: string  // "2024-CS-A"
  year: number      // 1, 2, 3, 4
  section: string   // "A", "B", "C"
}
```

#### New Model (Course-Centric)
```typescript
interface TimetableEntry {
  course_id: string           // "CS101"
  course_name: string         // "Introduction to Programming"
  faculty_id: string          // "F001"
  faculty_name: string        // "Dr. Smith"
  
  // Time-space
  day: string                 // "Monday"
  time_slot: string           // "09:00-10:00"
  room_id: string             // "301"
  
  // Student enrollment (NEP 2020 critical)
  enrolled_students: string[] // ["S001", "S045", "S123", "S234"]
  enrollment_count: number    // 45
  
  // Metadata
  is_elective: boolean
  is_interdisciplinary: boolean
  department_id: string       // Primary department offering course
}
```

### 2. View Architecture

#### A. Department View (HOD/Admin)
**Shows**: All courses offered by department in a semester

```
Computer Science Department - Odd Semester 2024-2025

Monday 09:00-10:00:
├─ CS101 (Section A) - Dr. Smith - Room 301 - 45 students
├─ CS101 (Section B) - Dr. Jones - Room 302 - 48 students
├─ CS201 (Lab) - Dr. Brown - Lab 1 - 30 students
└─ CS301 - Dr. White - Room 401 - 35 students

Total: 4 parallel sessions, 158 students
```

**Key Features**:
- Consolidated view: "CS101 (3 sections)" expandable to show details
- No year/batch filtering - shows ALL courses
- Parallel sessions clearly visible
- Student count per session

#### B. Faculty View
**Shows**: Only courses assigned to that faculty

```
Dr. Alice Smith's Schedule

Monday:
  09:00-10:00: CS101 Section A (45 students) - Room 301
  11:00-12:00: CS301 (35 students) - Room 401

Tuesday:
  09:00-10:00: CS101 Section A (45 students) - Room 301
  14:00-15:00: CS401 (28 students) - Lab 2

Total: 4 courses, 12 hours/week
```

#### C. Student View (Most Important for NEP 2020)
**Shows**: Only courses student is enrolled in

```
Student S001's Personal Timetable

Monday:
  09:00-10:00: CS101 - Dr. Smith - Room 301
  11:00-12:00: MA101 - Dr. Kumar - Room 201
  14:00-15:00: PH101 - Dr. Sharma - Lab 3

Tuesday:
  09:00-10:00: CS101 - Dr. Smith - Room 301
  10:00-11:00: EE201 (Elective) - Dr. Patel - Room 501

Courses: 5 (3 core, 2 electives)
Credits: 18
Departments: CS (primary), MA, PH, EE (interdisciplinary)
```

**Key Features**:
- Personalized to student's enrollment
- Shows courses from multiple departments
- Highlights electives and interdisciplinary courses
- No conflicts (guaranteed by optimizer)

### 3. Frontend Implementation

#### Updated Timetables Page (`/admin/timetables`)

**Before** (Year-based):
```
Tabs: [All Years] [1st Year] [2nd Year] [3rd Year] [4th Year]
```

**After** (Semester-based):
```
Grouped by: Academic Year + Semester
- 2024-2025 Odd Semester
  ├─ Computer Science (127 courses)
  ├─ Mechanical Engineering (98 courses)
  └─ Electrical Engineering (112 courses)

- 2024-2025 Even Semester
  └─ (Not generated yet)
```

**View Modes**:
1. **Grid View**: Card-based layout showing all departments
2. **List View**: Detailed table with filters

#### Key Changes Made:
```typescript
// Removed year-based filtering
- const [activeYear, setActiveYear] = useState('all')
- const navItems = [
-   { id: '1', label: '1st Year' },
-   { id: '2', label: '2nd Year' },
- ]

// Added semester-based grouping
+ const getGroupedBySemester = () => {
+   const grouped: { [key: string]: TimetableListItem[] } = {}
+   timetables.forEach(timetable => {
+     const key = `${timetable.academic_year}-${timetable.semester}`
+     grouped[key].push(timetable)
+   })
+   return grouped
+ }
```

### 4. Backend API Structure

#### Endpoint: Get Department Timetable
```typescript
GET /api/timetable/department/{dept_id}
Query params:
  - academic_year: "2024-2025"
  - semester: "odd"
  - view_mode: "consolidated" | "detailed"

Response:
{
  "department_id": "CS",
  "academic_year": "2024-2025",
  "semester": "odd",
  "total_courses": 127,
  "total_sessions": 245,
  "schedule": {
    "Monday": {
      "09:00-10:00": [
        {
          "course_id": "CS101",
          "section": "A",
          "faculty": "Dr. Smith",
          "room": "301",
          "enrolled_students": ["S001", "S002", ...],
          "enrollment_count": 45
        },
        {
          "course_id": "CS101",
          "section": "B",
          "faculty": "Dr. Jones",
          "room": "302",
          "enrolled_students": ["S050", "S051", ...],
          "enrollment_count": 48
        }
      ]
    }
  }
}
```

#### Endpoint: Get Student Timetable
```typescript
GET /api/timetable/student/{student_id}
Query params:
  - academic_year: "2024-2025"
  - semester: "odd"

Response:
{
  "student_id": "S001",
  "student_name": "John Doe",
  "program": "B.Tech Computer Science",
  "year": 1,
  "schedule": {
    "Monday": {
      "09:00-10:00": {
        "course_id": "CS101",
        "course_name": "Introduction to Programming",
        "faculty": "Dr. Smith",
        "room": "301",
        "is_elective": false
      },
      "11:00-12:00": {
        "course_id": "MA101",
        "course_name": "Calculus I",
        "faculty": "Dr. Kumar",
        "room": "201",
        "is_elective": false
      }
    }
  },
  "analytics": {
    "total_courses": 5,
    "total_credits": 18,
    "core_courses": 3,
    "elective_courses": 2,
    "departments": ["CS", "MA", "PH", "EE"],
    "interdisciplinary_credits": 3
  }
}
```

### 5. Conflict Detection (NEP 2020 Aware)

#### Student Conflict Check
```python
def check_student_conflicts(student_id, timetable_entries):
    """
    Check if student has time conflicts in their enrolled courses
    """
    student_schedule = {}
    conflicts = []
    
    for entry in timetable_entries:
        if student_id in entry.enrolled_students:
            time_key = (entry.day, entry.time_slot)
            
            if time_key in student_schedule:
                # Conflict detected
                conflicts.append({
                    'student_id': student_id,
                    'time': time_key,
                    'course1': student_schedule[time_key],
                    'course2': entry.course_id,
                    'severity': 'CRITICAL'
                })
            else:
                student_schedule[time_key] = entry.course_id
    
    return conflicts
```

#### Faculty Conflict Check
```python
def check_faculty_conflicts(faculty_id, timetable_entries):
    """
    Check if faculty is assigned to multiple courses at same time
    """
    faculty_schedule = {}
    conflicts = []
    
    for entry in timetable_entries:
        if entry.faculty_id == faculty_id:
            time_key = (entry.day, entry.time_slot)
            
            if time_key in faculty_schedule:
                conflicts.append({
                    'faculty_id': faculty_id,
                    'time': time_key,
                    'course1': faculty_schedule[time_key],
                    'course2': entry.course_id,
                    'severity': 'CRITICAL'
                })
            else:
                faculty_schedule[time_key] = entry.course_id
    
    return conflicts
```

### 6. UI/UX Improvements

#### Consolidated View (HOD)
```
┌─────────────────────────────────────────────┐
│ Monday 09:00-10:00                          │
│                                             │
│ CS101: Introduction to Programming          │
│ ├─ Section A │ Dr. Smith │ Room 301 │ 45   │
│ ├─ Section B │ Dr. Jones │ Room 302 │ 48   │
│ └─ Section C │ Dr. Brown │ Lab 1    │ 42   │
│                                             │
│ Total: 3 sections, 135 students             │
│ [Expand Details] [Check Conflicts]          │
└─────────────────────────────────────────────┘
```

#### Student View (Personalized)
```
┌─────────────────────────────────────────────┐
│ Your Schedule - Odd Semester 2024-2025      │
│                                             │
│ Monday                                      │
│ 09:00 │ CS101 │ Dr. Smith │ Room 301       │
│ 11:00 │ MA101 │ Dr. Kumar │ Room 201       │
│ 14:00 │ PH101 │ Dr. Sharma│ Lab 3          │
│                                             │
│ Tuesday                                     │
│ 09:00 │ CS101 │ Dr. Smith │ Room 301       │
│ 10:00 │ EE201 │ Dr. Patel │ Room 501 🌟    │
│       │ (Interdisciplinary Elective)        │
│                                             │
│ 📊 18 credits │ 5 courses │ 4 departments   │
└─────────────────────────────────────────────┘
```

## Benefits of Course-Centric Architecture

### 1. NEP 2020 Compliance
✅ Students can enroll in any course (subject to prerequisites)
✅ Interdisciplinary learning supported
✅ Flexible credit system
✅ No artificial year/batch constraints

### 2. Scalability
✅ Handles 1820 courses across 127 departments
✅ Supports multiple sections per course
✅ Efficient conflict detection

### 3. User Experience
✅ HOD sees department-wide schedule
✅ Faculty sees only their classes
✅ Students see personalized schedule
✅ No confusion from parallel sections

### 4. Data Integrity
✅ Single source of truth (course enrollments)
✅ Real-time conflict detection
✅ Automatic schedule generation per user

## Migration Path

### Phase 1: Backend (Completed)
- ✅ Course-centric data model
- ✅ Student enrollment tracking
- ✅ Conflict detection algorithms

### Phase 2: Frontend (Current)
- ✅ Remove year-based tabs
- ✅ Add semester-based grouping
- ✅ Course-centric display
- ⏳ Add student enrollment view
- ⏳ Add consolidated HOD view with expand/collapse

### Phase 3: Advanced Features (Future)
- ⏳ Real-time enrollment updates
- ⏳ Student self-service enrollment
- ⏳ Prerequisite checking
- ⏳ Credit limit enforcement
- ⏳ Waitlist management

## Conclusion

The new course-centric architecture aligns with NEP 2020's vision of flexible, student-centric education. By removing artificial year/batch constraints and focusing on individual course enrollments, the system can handle complex scenarios like:

- 4th year students retaking 1st year courses
- 1st year students taking advanced electives
- Cross-department interdisciplinary courses
- Multiple sections of same course running simultaneously

This provides a solid foundation for modern, flexible timetable management.
