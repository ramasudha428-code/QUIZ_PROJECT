def calculate_percentage(score, total_questions):
    if total_questions == 0:
        return 0.0
    return round((score / total_questions) * 100, 2)


def generate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    else:
        return "Fail"
