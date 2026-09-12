from typing import List, Tuple
from pydantic import BaseModel, Field

try:
    from pydantic import field_validator, ValidationInfo
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import validator
    PYDANTIC_V2 = False


def _time_to_minutes(time_str: str) -> int:
    h, m = map(int, time_str.strip().split(":"))
    return h * 60 + m


def _check_time_overlap(slot1: Tuple[str, str, str], slot2: Tuple[str, str, str]) -> bool:
    day1, start1, end1 = slot1
    day2, start2, end2 = slot2

    if day1.strip().lower() != day2.strip().lower():
        return False

    s1, e1 = _time_to_minutes(start1), _time_to_minutes(end1)
    s2, e2 = _time_to_minutes(start2), _time_to_minutes(end2)

    return max(s1, s2) < min(e1, e2)


class Course(BaseModel):
    course_code: str = Field(..., description="The unique code for the course, e.g., 'CS101'.")
    title: str
    credits: int
    schedule: List[Tuple[str, str, str]] = []


class Semester(BaseModel):
    semester_name: str
    courses: List[Course] = []
    max_credits: int = 18

    if PYDANTIC_V2:
        @field_validator("courses")
        @classmethod
        def validate_courses(cls, v: List[Course], info: ValidationInfo) -> List[Course]:
            max_c = info.data.get("max_credits", 18) if info.data else 18
            total_credits = sum(c.credits for c in v)
            if total_credits > max_c:
                raise ValueError(f"Total credits ({total_credits}) exceed the limit of {max_c}.")

            for i in range(len(v)):
                for j in range(i + 1, len(v)):
                    c1, c2 = v[i], v[j]
                    for slot1 in c1.schedule:
                        for slot2 in c2.schedule:
                            if _check_time_overlap(slot1, slot2):
                                raise ValueError(
                                    f"Schedule conflict between {c1.course_code} and {c2.course_code} on {slot1[0]} "
                                    f"({slot1[1]}-{slot1[2]} overlaps with {slot2[1]}-{slot2[2]})."
                                )
            return v
    else:
        @validator("courses")
        def check_credit_limit(cls, v, values):
            max_c = values.get("max_credits", 18)
            total_credits = sum(c.credits for c in v)
            if total_credits > max_c:
                raise ValueError(f"Total credits ({total_credits}) exceed the limit of {max_c}.")
            return v

        @validator("courses")
        def check_schedule_conflicts(cls, v):
            for i in range(len(v)):
                for j in range(i + 1, len(v)):
                    c1, c2 = v[i], v[j]
                    for slot1 in c1.schedule:
                        for slot2 in c2.schedule:
                            if _check_time_overlap(slot1, slot2):
                                raise ValueError(
                                    f"Schedule conflict between {c1.course_code} and {c2.course_code} on {slot1[0]} "
                                    f"({slot1[1]}-{slot1[2]} overlaps with {slot2[1]}-{slot2[2]})."
                                )
            return v


class DegreePlan(BaseModel):
    student_id: str
    completed_courses: List[Course]
    planned_semesters: List[Semester] = []
