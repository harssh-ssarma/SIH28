"""Django Backend Integration - Fetch data from Django API"""
import httpx
import logging
from typing import List, Dict, Optional
from models.timetable_models import Course, Faculty, Room, TimeSlot, Student, Batch, GenerationRequest
from config import settings

logger = logging.getLogger(__name__)


class DjangoAPIClient:
    """Client for communicating with Django backend"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.DJANGO_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def fetch_courses(
        self,
        department_id: str,
        batch_ids: List[str],
        semester: int,
        include_electives: bool = True
    ) -> List[Course]:
        """Fetch courses with NEP 2020 individual student enrollments"""
        try:
            # Fetch courses with actual student enrollments (NEP 2020 critical)
            response = await self.client.get(
                f"{self.base_url}/students/enrollments/",
                params={
                    "department_id": department_id,
                    "batch_ids": ",".join(batch_ids),
                    "semester": semester,
                    "include_electives": include_electives,
                    "group_by_course": True  # NEP 2020: Group by course with student lists
                }
            )
            response.raise_for_status()

            data = response.json()
            courses = []

            for course_data in data["results"]:
                # NEP 2020: Each course contains actual enrolled student IDs
                course = Course(
                    course_id=course_data["course_id"],
                    course_code=course_data["course_code"],
                    course_name=course_data["course_name"],
                    faculty_id=course_data["faculty_id"],
                    credits=course_data["credits"],
                    duration=course_data["duration"],
                    subject_type=course_data["subject_type"],
                    required_features=course_data.get("required_features", []),
                    student_ids=course_data["enrolled_student_ids"],  # NEP 2020: Individual students
                    batch_ids=course_data.get("batch_ids", [])  # For display grouping only
                )
                courses.append(course)

            logger.info(f"Fetched {len(courses)} courses with NEP 2020 student enrollments")
            return courses

        except Exception as e:
            logger.error(f"Failed to fetch courses with enrollments: {e}")
            raise

    async def fetch_faculty(self, department_id: str) -> Dict[str, Faculty]:
        """Fetch faculty from Django API"""
        try:
            response = await self.client.get(
                f"{self.base_url}/academics/faculty/",
                params={"department_id": department_id}
            )
            response.raise_for_status()

            data = response.json()
            faculty_dict = {
                f["faculty_id"]: Faculty(**f)
                for f in data["results"]
            }

            logger.info(f"Fetched {len(faculty_dict)} faculty from Django")
            return faculty_dict

        except Exception as e:
            logger.error(f"Failed to fetch faculty: {e}")
            raise

    async def fetch_rooms(self, campus_id: Optional[str] = None) -> List[Room]:
        """Fetch rooms from Django API"""
        try:
            params = {}
            if campus_id:
                params["campus_id"] = campus_id

            response = await self.client.get(
                f"{self.base_url}/academics/rooms/",
                params=params
            )
            response.raise_for_status()

            data = response.json()
            rooms = [Room(**room_data) for room_data in data["results"]]

            logger.info(f"Fetched {len(rooms)} rooms from Django")
            return rooms

        except Exception as e:
            logger.error(f"Failed to fetch rooms: {e}")
            raise

    async def fetch_time_slots(self) -> List[TimeSlot]:
        """Fetch time slots from Django API"""
        try:
            response = await self.client.get(f"{self.base_url}/academics/time-slots/")
            response.raise_for_status()

            data = response.json()
            time_slots = [TimeSlot(**ts_data) for ts_data in data["results"]]

            logger.info(f"Fetched {len(time_slots)} time slots from Django")
            return time_slots

        except Exception as e:
            logger.error(f"Failed to fetch time slots: {e}")
            raise

    async def fetch_students(self, batch_ids: List[str]) -> Dict[str, Student]:
        """Fetch students from Django API"""
        try:
            response = await self.client.get(
                f"{self.base_url}/academics/students/",
                params={"batch_ids": ",".join(batch_ids)}
            )
            response.raise_for_status()

            data = response.json()
            students_dict = {
                s["student_id"]: Student(**s)
                for s in data["results"]
            }

            logger.info(f"Fetched {len(students_dict)} students from Django")
            return students_dict

        except Exception as e:
            logger.error(f"Failed to fetch students: {e}")
            raise

    async def fetch_batches(self, batch_ids: List[str]) -> Dict[str, Batch]:
        """Fetch batches from Django API"""
        try:
            response = await self.client.get(
                f"{self.base_url}/academics/batches/",
                params={"batch_ids": ",".join(batch_ids)}
            )
            response.raise_for_status()

            data = response.json()
            batches_dict = {
                b["batch_id"]: Batch(**b)
                for b in data["results"]
            }

            logger.info(f"Fetched {len(batches_dict)} batches from Django")
            return batches_dict

        except Exception as e:
            logger.error(f"Failed to fetch batches: {e}")
            raise

    async def save_timetable(self, job_id: str, timetable_data: Dict):
        """Save generated timetable back to Django"""
        try:
            response = await self.client.post(
                f"{self.base_url}/academics/timetables/",
                json=timetable_data
            )
            response.raise_for_status()

            logger.info(f"Saved timetable {job_id} to Django")
            return response.json()

        except Exception as e:
            logger.error(f"Failed to save timetable: {e}")
            raise
