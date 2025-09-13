from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import time

class TimeSlot(BaseModel):
    start_time: time
    end_time: time
    day: str

class Course(BaseModel):
    id: int
    name: str
    code: str
    credits: int
    duration_hours: int

class Classroom(BaseModel):
    id: int
    name: str
    capacity: int
    type: str
    equipment: List[str] = []

class Faculty(BaseModel):
    id: int
    name: str
    department: str
    available_slots: List[TimeSlot]
    max_hours_per_week: int

class OptimizationRequest(BaseModel):
    courses: List[Course]
    classrooms: List[Classroom]
    faculty: List[Faculty]
    time_slots: List[TimeSlot]
    constraints: Dict[str, Any] = {}

class TimetableEntry(BaseModel):
    course_id: int
    faculty_id: int
    classroom_id: int
    time_slot: TimeSlot
    day: str

class OptimizationResponse(BaseModel):
    success: bool
    timetable: List[TimetableEntry]
    conflicts: List[str] = []
    optimization_score: float
    message: str