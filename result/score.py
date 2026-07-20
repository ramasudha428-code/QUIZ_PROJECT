def save_result(name, score, total_questions):

    percentage = (score / total_questions) * 100

    with open("results/scores.txt", "a") as file:

        file.write("\n====================================\n")

        file.write(f"Candidate Name : {name}\n")

        file.write(f"Total Questions: {total_questions}\n")

        file.write(f"Correct Answers: {score}\n")

        file.write(f"Wrong Answers  : {total_questions - score}\n")

        file.write(f"Percentage     : {percentage}%\n")

        file.write("====================================\n")
