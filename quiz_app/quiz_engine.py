def start_quiz(questions):
    score = 0
    weak_topics = []

    print("\n===================================")
    print("        PYTHON QUIZ STARTED")
    print("===================================")

    for index, q in enumerate(questions, start=1):
        print(f"\nQuestion {index}")
        print("-----------------------------------")
        print(q["question"])
        print("\nOptions:")

        # Dynamically map options to letters A, B, C, D
        option_letters = ["A", "B", "C", "D"]
        options_map = {}
        for idx, option in enumerate(q["options"]):
            letter = option_letters[idx] if idx < len(option_letters) else str(idx + 1)
            options_map[letter.lower()] = option.lower()
            print(f"{letter}. {option}")

        correct_answer_str = q["answer"]
        # Find which letter corresponds to the correct answer string
        correct_letter = None
        for letter, option_val in options_map.items():
            if option_val == correct_answer_str.lower():
                correct_letter = letter.upper()
                break

        # Prompt candidate for answer
        user_answer = input("\nEnter Your Answer (A/B/C/D): ").strip()

        is_correct = False
        # Match case-insensitively:
        # 1. The literal correct answer (e.g. "def")
        # 2. The letter associated with it (e.g. "c")
        if user_answer.lower() == correct_answer_str.lower():
            is_correct = True
        elif user_answer.lower() in options_map and options_map[user_answer.lower()] == correct_answer_str.lower():
            is_correct = True

        if is_correct:
            print("\n[Correct] Correct Answer!")
            score += 1
        else:
            print("\n[Wrong] Wrong Answer!")
            display_ans = f"{correct_letter}. {correct_answer_str}" if correct_letter else correct_answer_str
            print("Correct Answer is:", display_ans)
            
            # Track weak topics for the candidate
            topic = q.get("topic", "General")
            weak_topics.append(topic)

    return score, weak_topics
