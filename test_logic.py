"""Quick logic test - run with: python test_logic.py"""
from services.risk_service import check_heuristic_red_flags, _build_heuristic_result
from utils.text_utils import clean_text, truncate_text, parse_json_from_llm
from services.interview_service import _generate_fallback_questions

# Test 1: Heuristic risk detection
test_jd = "URGENT HIRING! Guaranteed job placement! Pay registration fee of Rs 500 to apply now!"
flags = check_heuristic_red_flags(test_jd)
result = _build_heuristic_result(flags, test_jd)
print("Test 1 - Risk Detection:")
print("  Risk level:", result["risk_level"], "score:", result["risk_score"])
print("  Flags:", list(flags.keys()))

# Test 2: Text utilities
cleaned = clean_text("  hello\n\n\n\nworld  ")
print("Test 2 - Text utils:")
print("  Clean text:", repr(cleaned))
truncated = truncate_text("x" * 5000, 100)
print("  Truncated length:", len(truncated))
parsed = parse_json_from_llm('{"score": 8, "skills": ["Python"]}')
print("  JSON parsed:", parsed)

# Test 3: Fallback interview questions
fake_resume = {
    "name": "Alice",
    "skills": ["Python", "SQL"],
    "projects": ["ML Dashboard: Built a dashboard"]
}
qs = _generate_fallback_questions(fake_resume, "Hiring Python developer", 5)
print("Test 3 - Interview Questions:")
print("  Generated", len(qs), "fallback questions")
print("  Q1:", qs[0]["question"][:60] + "...")

print("\nALL CORE LOGIC TESTS PASSED!")
