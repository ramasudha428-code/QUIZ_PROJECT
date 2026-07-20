# quiz_app/chatbot.py
# ─────────────────────────────────────────────────────────────────────────────
#  Enhanced Chatbot Engine — PyBot AI Tutor
#  Handles both quiz-end feedback AND real-time chat API requests.
# ─────────────────────────────────────────────────────────────────────────────

import re
import random

# ── Knowledge Base ────────────────────────────────────────────────────────────

PYTHON_TIPS = [
    "Use `enumerate()` instead of `range(len(list))` for cleaner iteration!",
    "List comprehensions are not only shorter but also faster than `for` loops!",
    "The walrus operator `:=` (Python 3.8+) lets you assign and test simultaneously.",
    "Use `dict.get(key, default)` to avoid `KeyError` exceptions safely.",
    "f-strings (Python 3.6+) are the fastest and most readable way to format strings.",
    "Context managers (`with` statement) guarantee resources like files are always closed.",
    "Use `*args` for positional and `**kwargs` for keyword variable arguments in functions.",
    "`zip()` elegantly pairs elements from multiple iterables together.",
    "The `collections.defaultdict` eliminates KeyError for missing keys.",
    "Use `__slots__` in classes to reduce memory usage for large object counts.",
]

CONCEPT_EXPLANATIONS = {
    "list": "**Lists** are ordered, mutable collections. Key methods: append(), extend(), pop(), insert(), remove(), sort().",
    "dict": "**Dictionaries** store key-value pairs. Access values with dict[key] or dict.get(key, default) to avoid errors.",
    "loop": "**Loops**: `for` iterates over sequences; `while` runs while a condition is True. Use break/continue to control flow.",
    "function": "**Functions** (def) encapsulate reusable code. They take parameters and return values. Use *args/**kwargs for flexible signatures.",
    "class": "**Classes** define blueprints for objects. `__init__` initialises attributes. Inheritance enables code reuse.",
    "exception": "**Exception handling** with try/except/finally prevents crashes. Always catch specific exceptions, not bare `except:`.",
    "string": "**Strings** are immutable sequences. Key methods: split(), join(), upper(), lower(), strip(), replace(), format().",
    "lambda": "**Lambda** creates anonymous functions: `lambda x: x*2`. Best for short operations with map(), filter(), sorted().",
}

ENCOURAGEMENT_BY_GRADE = {
    "A+": [
        "🌟 Spectacular! You're in the top tier. Your Python knowledge is rock-solid!",
        "🏆 Perfect performance! You've mastered the material — time to tackle advanced Python!",
    ],
    "A": [
        "✨ Excellent work! You clearly understand Python well. A little more practice and you'll be unstoppable!",
        "🎯 Great score! You're close to perfection — review your weak areas and you'll nail the next one!",
    ],
    "B": [
        "👍 Good job! Solid foundation. Focus on the weak topics listed and you'll jump to an A next time!",
        "📈 Well done! You're progressing nicely. Keep reviewing and practicing daily!",
    ],
    "C": [
        "💪 Keep going! A C means you're getting there. Focus on your weak topics and retake the quiz!",
        "📚 Not bad for a start! Review the flagged areas and try again — you'll surprise yourself!",
    ],
    "F": [
        "🌱 Every expert started as a beginner. Review the basics, use the tips, and retake the quiz — you've got this!",
        "💡 Don't be discouraged! Focus on one topic at a time. Progress is progress, no matter how small!",
    ],
}

TOPIC_STUDY_LINKS = {
    "Variables": "Python variables, data types, and type casting",
    "Lists": "list methods, slicing, list comprehensions",
    "Dictionaries": "dict creation, access, methods, and nested dicts",
    "Functions": "def, return, scope, closures, decorators",
    "OOP": "classes, __init__, inheritance, polymorphism",
    "File I/O": "open(), read/write modes, context managers",
    "Exceptions": "try/except/finally, custom exceptions, raise",
    "Loops": "for/while, break/continue, enumerate, zip",
    "Strings": "string methods, f-strings, formatting, slicing",
    "Modules": "import, from…import, __name__, pip packages",
}

# ── Score-based Feedback Generator ───────────────────────────────────────────

def chatbot_feedback(percentage: float, weak_topics: list = None) -> str:
    """
    Generate rich, personalised AI feedback based on quiz score and weak topics.
    Returns a multi-sentence encouraging message with specific study suggestions.
    """
    # Determine grade
    if percentage >= 90:
        grade = "A+"
        opening = "🌟 **Outstanding Performance!** You have an exceptional grasp of Python core concepts."
        next_step = "Challenge yourself further with advanced topics like decorators, generators, and async programming!"
    elif percentage >= 75:
        grade = "A"
        opening = "✨ **Excellent Work!** You have a strong command of Python with just a few gaps to fill."
        next_step = "Keep reviewing and you'll hit the top tier on your next attempt!"
    elif percentage >= 60:
        grade = "B"
        opening = "👍 **Good Job!** You have a solid Python foundation that you can build on."
        next_step = "Focused study on your weak areas will make a big difference in your next quiz!"
    elif percentage >= 40:
        grade = "C"
        opening = "📚 **Keep Going!** You've got the basics, but there's clear room to grow."
        next_step = "Start with one weak topic per day and retake the quiz when ready!"
    else:
        grade = "F"
        opening = "💪 **Don't Give Up!** Everyone starts somewhere — the key is to keep learning."
        next_step = "Go back to Python fundamentals and use the chatbot to ask questions anytime!"

    # Build the message
    parts = [opening]

    # Weak topics with study suggestions
    if weak_topics:
        unique_weak = list(dict.fromkeys(weak_topics))  # preserve order, deduplicate
        if unique_weak:
            topic_list = ", ".join(f"**{t}**" for t in unique_weak[:5])  # cap at 5
            parts.append(
                f"\n\n🔍 **Areas to Review:** {topic_list}."
            )
            # Add a random helpful tip
            tip = random.choice(PYTHON_TIPS)
            parts.append(f"\n\n💡 **Quick Tip:** {tip}")
    else:
        parts.append("\n\n🎉 No weak areas detected — impressive!")

    parts.append(f"\n\n🚀 **Next Step:** {next_step}")

    return "".join(parts)


# ── Real-time Chat API Handler ────────────────────────────────────────────────

def process_chat_message(user_message: str, context: dict = None) -> str:
    """
    Process a real-time chat message from the user and return a smart response.
    `context` can include: score, grade, weak_topics, candidate_name
    """
    text = user_message.lower().strip()
    ctx = context or {}
    name = ctx.get("candidate_name", "")
    score = ctx.get("score")
    grade = ctx.get("grade")
    weak_topics = ctx.get("weak_topics", [])

    # Greeting
    if re.search(r'\b(hi|hey|hello|greetings|howdy)\b', text):
        greeting = f"Hey {name}! " if name else "Hey! "
        return f"👋 {greeting}I'm PyBot, your AI Python tutor. How can I help you today?"

    # Thank you
    if re.search(r'\b(thanks|thank you|thx|ty)\b', text):
        return "😊 You're very welcome! Happy to help. Keep learning and you'll go far! 🚀"

    # Tips
    if re.search(r'\b(tip|trick|advice|shortcut|hint|help me learn)\b', text):
        return f"💡 **Python Tip:**\n\n{random.choice(PYTHON_TIPS)}"

    # Score inquiry
    if re.search(r'\b(my score|how did i do|my result|my grade)\b', text) and score is not None:
        return (
            f"📊 You scored **{score}** — Grade **{grade}**! "
            f"{random.choice(ENCOURAGEMENT_BY_GRADE.get(grade, ENCOURAGEMENT_BY_GRADE['C']))}"
        )

    # Weak topics
    if re.search(r'\b(weak|improve|study|review|work on)\b', text) and weak_topics:
        unique = list(dict.fromkeys(weak_topics))
        topics_str = ", ".join(f"**{t}**" for t in unique)
        return (
            f"📚 Based on your quiz, focus on: {topics_str}.\n\n"
            f"💡 Tip: {random.choice(PYTHON_TIPS)}"
        )

    # Concept explanations
    for keyword, explanation in CONCEPT_EXPLANATIONS.items():
        if re.search(rf'\b{keyword}\b', text):
            return f"🐍 {explanation}\n\n💡 Bonus Tip: {random.choice(PYTHON_TIPS)}"

    # Encouragement
    if re.search(r'\b(sad|fail|bad|terrible|awful|gave up|depressed|can\'t do)\b', text):
        return (
            "💪 Don't be discouraged! Every Python master failed many times first. "
            "What matters is you keep trying.\n\n"
            f"💡 Remember: {random.choice(PYTHON_TIPS)}"
        )

    # Fallback
    return (
        "🤔 I'm not sure about that, but I'm always learning! "
        "Try asking me about Python concepts (lists, functions, classes), "
        "tips, your score, or areas to improve!"
    )
