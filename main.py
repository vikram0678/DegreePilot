import os
import sys
import json
import argparse
from loguru import logger
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from models import DegreePlan
from parser import parse_transcript
from agent import build_degree_planner_graph
from data.create_sample_pdf import generate_sample_transcript


def setup_logger(log_file_path: str = "output/agent.log"):
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logger.remove()

    def json_sink(message):
        record = message.record
        event_name = record["extra"].get("event", record["message"])
        
        log_entry = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "event": event_name,
        }

        for key, value in record["extra"].items():
            if key != "event":
                log_entry[key] = value

        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    logger.add(json_sink, level="INFO")
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | {message}", level="INFO")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="DegreePilot: AI University Degree Planning Assistant")
    parser.add_argument("--transcript", type=str, default="./data/sample_transcript.pdf", help="Path to transcript PDF")
    parser.add_argument("--goal", type=str, default="Plan my next two semesters to finish the AI minor.", help="Academic planning goal")
    args = parser.parse_args()

    setup_logger("output/agent.log")
    os.makedirs("output", exist_ok=True)

    logger.info(f"Starting planning with goal: '{args.goal}'", event="Application started", goal=args.goal)

    if not os.path.exists(args.transcript):
        if "sample_transcript.pdf" in args.transcript:
            generate_sample_transcript(args.transcript)
        else:
            logger.error(f"Transcript file not found: {args.transcript}", event="Transcript error")
            sys.exit(1)

    logger.info(f"Parsing transcript: {args.transcript}", event="Parsing transcript", path=args.transcript)
    try:
        student_id, completed_courses = parse_transcript(args.transcript)
        logger.info(
            f"Parsed student {student_id} with {len(completed_courses)} completed courses",
            event="Transcript parsed",
            student_id=student_id,
            completed_count=len(completed_courses)
        )
    except Exception as e:
        logger.error(f"Failed to parse transcript: {e}", event="Parser exception", error=str(e))
        sys.exit(1)

    initial_plan = DegreePlan(
        student_id=student_id,
        completed_courses=completed_courses,
        planned_semesters=[]
    )

    completed_codes = [c.course_code for c in completed_courses]
    max_steps = int(os.getenv("AGENT_MAX_STEPS", "10"))

    system_prompt = (
        "You are an academic degree planning advisor. Plan future semesters based on student goal, "
        "prerequisites, credit limits, and time schedules."
    )
    user_prompt = f"Student ID: {student_id}\nCompleted Courses: {', '.join(completed_codes)}\nGoal: {args.goal}"

    initial_state = {
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ],
        "degree_plan": initial_plan,
        "student_id": student_id,
        "completed_codes": completed_codes,
        "user_goal": args.goal,
        "step_count": 0,
        "max_steps": max_steps,
        "status": "initialized"
    }

    logger.info("Starting LangGraph agent loop", event="Agent workflow initialized", max_steps=max_steps)
    app = build_degree_planner_graph()
    final_state = app.invoke(initial_state)

    final_plan = final_state.get("degree_plan", initial_plan)
    output_path = "output/degree_plan.json"
    plan_dict = final_plan.model_dump() if hasattr(final_plan, "model_dump") else final_plan.dict()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(plan_dict, f, indent=2)

    logger.info(f"Degree plan written to {output_path}", event="Degree plan generated", output_file=output_path)
    print(f"\nDegree plan generated successfully for student {student_id} -> {output_path}")


if __name__ == "__main__":
    main()
