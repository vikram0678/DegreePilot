import pytest
from pydantic import ValidationError
from models import Course, Semester, DegreePlan, _check_time_overlap


def test_time_overlap():
    assert _check_time_overlap(("Mon", "10:00", "11:30"), ("Mon", "11:00", "12:30")) is True
    assert _check_time_overlap(("Mon", "10:00", "11:30"), ("Mon", "11:30", "13:00")) is False
    assert _check_time_overlap(("Mon", "10:00", "11:30"), ("Tue", "10:00", "11:30")) is False


def test_credit_limit_validation():
    courses = [
        Course(course_code=f"CS10{i}", title=f"Course {i}", credits=4, schedule=[])
        for i in range(1, 6)
    ]
    with pytest.raises(ValidationError):
        Semester(semester_name="Fall 2024", courses=courses, max_credits=18)

    valid_sem = Semester(semester_name="Fall 2024", courses=courses[:4], max_credits=18)
    assert len(valid_sem.courses) == 4


def test_schedule_conflict_validation():
    c1 = Course(
        course_code="CS301",
        title="AI",
        credits=3,
        schedule=[("Mon", "10:00", "11:30"), ("Wed", "10:00", "11:30")]
    )
    c2 = Course(
        course_code="MATH302",
        title="Optimization",
        credits=3,
        schedule=[("Mon", "11:00", "12:30")]
    )

    with pytest.raises(ValidationError) as excinfo:
        Semester(semester_name="Fall 2025", courses=[c1, c2])
    assert "Schedule conflict between CS301 and MATH302" in str(excinfo.value)


def test_degree_plan_model():
    c1 = Course(course_code="CS101", title="Intro", credits=4, schedule=[])
    c2 = Course(course_code="CS301", title="AI", credits=3, schedule=[("Mon", "10:00", "11:30")])
    sem = Semester(semester_name="Fall 2025", courses=[c2])
    plan = DegreePlan(student_id="STU-12345", completed_courses=[c1], planned_semesters=[sem])

    data = plan.model_dump() if hasattr(plan, "model_dump") else plan.dict()
    assert data["student_id"] == "STU-12345"
    assert len(data["completed_courses"]) == 1
    assert len(data["planned_semesters"]) == 1
