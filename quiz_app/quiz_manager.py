def calculate_percentage(score, total):
    if total == 0:
        return 0.0
    return (score / total) * 100


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
