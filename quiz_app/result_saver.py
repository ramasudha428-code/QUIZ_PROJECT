import os

def save_result(name, score, percentage, grade=None):
    """Save the quiz result summary to a local text file inside 'result/' directory."""
    os.makedirs("result", exist_ok=True)
    
    file_path = os.path.join("result", "result.txt")
    with open(file_path, "a", encoding="utf-8") as file:
        file.write("=====================================\n")
        file.write(f"Candidate Name : {name}\n")
        file.write(f"Score          : {score}\n")
        file.write(f"Percentage     : {percentage}%\n")
        if grade:
            file.write(f"Grade          : {grade}\n")
        file.write("-------------------------------------\n")
