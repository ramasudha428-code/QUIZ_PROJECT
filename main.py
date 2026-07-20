from quiz_app.quiz_loader import load_questions
from quiz_app.quiz_engine import start_quiz
from quiz_app.score_manager import calculate_percentage
from quiz_app.score_manager import generate_grade
from quiz_app.chatbot import chatbot_feedback
from quiz_app.result_saver import save_result as save_text_result
from database.queries import save_result as save_db_result

print("======================================")
print("      AI PYTHON QUIZ SYSTEM")
print("======================================")

# User Name
name = input("\nEnter Your Name: ")

# Load Questions
questions = load_questions()

# Total Questions
total_questions = len(questions)

# Start Quiz
score, weak_topics = start_quiz(questions)

# Calculate Percentage
percentage = calculate_percentage(score, total_questions)

# Generate Grade
grade = generate_grade(percentage)

# Chatbot Feedback
feedback = chatbot_feedback(percentage)

# Result Section
print("\n======================================")
print("          QUIZ RESULT")
print("======================================")

print(f"\nCandidate Name : {name}")
print(f"Total Questions: {total_questions}")
print(f"Correct Answers: {score}")
print(f"Wrong Answers  : {total_questions - score}")

print(f"\nScore Percentage: {percentage}%")
print(f"Grade           : {grade}")

# Weak Topics
print("\n======================================")
print("         WEAK TOPICS")
print("======================================")

if weak_topics:

    for topic in set(weak_topics):
        print(" ->", topic)

else:
    print("No weak topics detected.")

# AI Feedback
print("\n======================================")
print("       AI CHATBOT FEEDBACK")
print("======================================")

print(feedback)

# Save Result to the database and persisted text file
save_db_result(
    name=name,
    score=score,
    percentage=percentage,
    grade=grade,
    weak_topics=weak_topics,
    feedback=feedback
)
save_text_result(name, score, percentage, grade)

print("\nResult Saved Successfully to the database and local result file!")