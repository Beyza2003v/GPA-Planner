def normalize_code(code: str) -> str:
    return code.replace(" ", "").strip().upper()

def assign_courses_to_curriculum(student_courses, curriculum):
    assignments = {slot: [] for slot in curriculum}
    unassigned = []

    for course in student_courses:
        course_code = normalize_code(course["code"])
        assigned = False

        for slot_code, rule in curriculum.items():

            # elective slotlar otomatik dolmaz
            if rule.get("type") == "elective_slot":
                continue

            options = rule.get("options")

            # 1️⃣ OPTION'LI SLOT (Programming gibi)
            if options:
                normalized_opts = [normalize_code(o) for o in options]
                if course_code in normalized_opts:
                    course["assigned_slot"] = slot_code
                    assignments[slot_code].append(course)
                    assigned = True
                    break

            # 2️⃣ OPTION'SIZ ZORUNLU SLOT
            else:
                # slot_code ders kodu ile aynıysa
                if course_code == normalize_code(slot_code):
                    course["assigned_slot"] = slot_code
                    assignments[slot_code].append(course)
                    assigned = True
                    break

        if not assigned:
            course["assigned_slot"] = None
            unassigned.append(course)

    return assignments, unassigned
