# gpa_calculator.py

GRADE_POINTS = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "F": 0.0,
    "S": None  # GPA dışı
}

def calculate_gpa(courses, curriculum=None):
    total_points = 0.0
    total_credits = 0.0

    for course in courses:
        grade = course.get("grade")
        credits = course.get("credits", 0)

        # geçersiz / GPA dışı notlar
        if grade not in GRADE_POINTS:
            continue

        if GRADE_POINTS[grade] is None:
            continue

        total_points += GRADE_POINTS[grade] * credits
        total_credits += credits

    if total_credits == 0:
        return 0.0

    return total_points / total_credits