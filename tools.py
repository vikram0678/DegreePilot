import os
from typing import List, Dict, Any
import requests
from langchain_core.tools import tool

COURSE_CATALOG = {
    "CS301": {
        "course_code": "CS301",
        "title": "Introduction to Artificial Intelligence",
        "credits": 3,
        "schedule": [("Mon", "10:00", "11:30"), ("Wed", "10:00", "11:30")],
        "prerequisites": ["CS102", "MATH202"],
        "semesters_offered": ["Fall 2025", "Spring 2026"]
    },
    "CS302": {
        "course_code": "CS302",
        "title": "Machine Learning",
        "credits": 3,
        "schedule": [("Tue", "13:00", "14:30"), ("Thu", "13:00", "14:30")],
        "prerequisites": ["CS301", "MATH301"],
        "semesters_offered": ["Spring 2026", "Fall 2026"]
    },
    "CS303": {
        "course_code": "CS303",
        "title": "Deep Learning & Neural Networks",
        "credits": 3,
        "schedule": [("Mon", "14:00", "15:30"), ("Wed", "14:00", "15:30")],
        "prerequisites": ["CS302"],
        "semesters_offered": ["Fall 2026", "Spring 2027"]
    },
    "CS304": {
        "course_code": "CS304",
        "title": "Natural Language Processing",
        "credits": 3,
        "schedule": [("Tue", "10:00", "11:30"), ("Thu", "10:00", "11:30")],
        "prerequisites": ["CS301"],
        "semesters_offered": ["Fall 2025", "Spring 2026"]
    },
    "CS305": {
        "course_code": "CS305",
        "title": "Computer Vision",
        "credits": 3,
        "schedule": [("Mon", "10:30", "12:00"), ("Wed", "10:30", "12:00")],
        "prerequisites": ["CS301"],
        "semesters_offered": ["Fall 2025", "Spring 2026"]
    },
    "MATH302": {
        "course_code": "MATH302",
        "title": "Numerical Optimization",
        "credits": 3,
        "schedule": [("Tue", "15:00", "16:30"), ("Thu", "15:00", "16:30")],
        "prerequisites": ["MATH202"],
        "semesters_offered": ["Fall 2025", "Spring 2026"]
    },
    "CS310": {
        "course_code": "CS310",
        "title": "Ethics in Artificial Intelligence",
        "credits": 3,
        "schedule": [("Fri", "13:00", "16:00")],
        "prerequisites": ["CS101"],
        "semesters_offered": ["Fall 2025", "Spring 2026"]
    }
}

MINOR_REQUIREMENTS = {
    "Artificial Intelligence": {
        "required_credits": 15,
        "core_courses": ["CS301", "CS302", "CS310"],
        "electives": ["CS303", "CS304", "CS305", "MATH302"],
        "min_elective_credits": 6
    },
    "AI minor": {
        "required_credits": 15,
        "core_courses": ["CS301", "CS302", "CS310"],
        "electives": ["CS303", "CS304", "CS305", "MATH302"],
        "min_elective_credits": 6
    }
}


@tool
def search_courses(query: str, semester: str) -> List[Dict[str, Any]]:
    """Searches the university catalog for courses matching a query in a specific semester.

    Args:
        query: The search query (e.g., 'Artificial Intelligence' or 'CS301').
        semester: The semester to search in (e.g., 'Fall 2025').

    Returns:
        A list of courses matching the search criteria.
    """
    mcp_url = os.getenv("MCP_SERVER_URL")
    if mcp_url and not mcp_url.startswith("http://mock"):
        try:
            resp = requests.get(f"{mcp_url}/courses", params={"query": query, "semester": semester}, timeout=2)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

    q = query.lower().strip()
    results = []
    for code, info in COURSE_CATALOG.items():
        if q in code.lower() or q in info["title"].lower() or q in "ai minor" or q == "all":
            if not semester or semester in info.get("semesters_offered", []):
                results.append({
                    "course_code": info["course_code"],
                    "title": info["title"],
                    "credits": info["credits"],
                    "schedule": info["schedule"]
                })
    return results


@tool
def get_course_details(course_code: str) -> Dict[str, Any]:
    """Gets detailed course information including title, credits, schedule, and prerequisites."""
    code = course_code.replace(" ", "").upper()
    if code in COURSE_CATALOG:
        return COURSE_CATALOG[code]
    return {"error": f"Course {course_code} not found"}


@tool
def get_prerequisites(course_code: str) -> List[str]:
    """Returns the prerequisite course codes required for a given course."""
    code = course_code.replace(" ", "").upper()
    if code in COURSE_CATALOG:
        return COURSE_CATALOG[code].get("prerequisites", [])
    return []


@tool
def get_degree_requirements(program_name: str) -> Dict[str, Any]:
    """Returns core courses and electives needed for a degree or minor."""
    for key, reqs in MINOR_REQUIREMENTS.items():
        if key.lower() in program_name.lower() or program_name.lower() in key.lower():
            return reqs
    return MINOR_REQUIREMENTS["Artificial Intelligence"]


ALL_TOOLS = [search_courses, get_course_details, get_prerequisites, get_degree_requirements]
