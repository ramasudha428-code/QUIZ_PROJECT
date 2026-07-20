/**
 * ═══════════════════════════════════════════════════════════════
 *  PyBot — Intelligent Quiz Assistant  |  chatbot.js
 *  Features:
 *    • Smart rule-based NLP with keyword matching
 *    • Contextual multi-turn conversation memory
 *    • Animated typing indicator with realistic delays
 *    • Emoji-rich, personality-driven responses
 *    • Quiz-aware tips and Python knowledge base
 *    • Mood detection (encouragement vs celebration)
 * ═══════════════════════════════════════════════════════════════
 */

/* ── State ─────────────────────────────────────────────────── */
let chatOpen = false;
let chatInitialised = false;
let conversationHistory = [];   // {role: 'bot'|'user', text: string}
let userMood = 'neutral';       // neutral | struggling | confident

/* ── Knowledge Base ────────────────────────────────────────── */
const KB = {
    greetings: [
        '👋 Hey there! I\'m **PyBot**, your AI Python companion! Ready to help you ace this quiz. What can I do for you?',
        '🤖 Hello! PyBot reporting for duty! Ask me anything about Python, the quiz, or study tips — I\'ve got you covered!',
        '✨ Hi! Great to see you here. I\'m your personal AI tutor. Let\'s make this quiz session amazing! 🚀'
    ],

    topics: `📚 **Quiz Topics Covered:**\n\n• 🔤 **Variables & Data Types** — int, float, str, bool, None\n• 📋 **Lists, Tuples & Dicts** — indexing, methods, mutations\n• 🔄 **Control Flow** — if/elif/else, loops, break/continue\n• 🧩 **Functions** — def, return, *args, **kwargs, scope\n• 🎯 **OOP** — classes, inheritance, __init__, self\n• 📁 **File Handling** — open(), read, write, context managers\n• ⚠️ **Exception Handling** — try/except/finally, raise\n• 🛠️ **Built-ins & Modules** — len, range, map, filter, os, sys`,

    grading: `🎓 **Grading System:**\n\n| Score | Grade | Badge |\n|-------|-------|-------|\n| 90–100% | A+ | 🌟 Exceptional |\n| 75–89% | A | ✨ Excellent |\n| 60–74% | B | 👍 Good |\n| 40–59% | C | 📚 Keep Going |\n| 0–39% | F | 💪 More Practice |\n\n*Your AI feedback is tailored to your exact score and weak areas!*`,

    start: `🚀 **Starting the Quiz:**\n\n1. Enter your full name in the text box\n2. Hit **"Start Evaluation"**\n3. Answer each question — you can go back!\n4. Click **"Submit Quiz"** at the end\n5. See your AI-powered results 🎉\n\n*Tip: You can change answers before submitting!*`,

    tips: [
        '💡 **Python Tip:** Use `enumerate()` instead of `range(len(list))` for cleaner loops!\n```python\nfor i, val in enumerate(my_list):\n    print(i, val)\n```',
        '💡 **Python Tip:** List comprehensions are faster than regular for-loops!\n```python\nsquares = [x**2 for x in range(10)]\n```',
        '💡 **Python Tip:** Use `zip()` to iterate multiple lists simultaneously!\n```python\nfor a, b in zip(list1, list2):\n    print(a, b)\n```',
        '💡 **Python Tip:** The walrus operator `:=` lets you assign and test in one expression (Python 3.8+)!\n```python\nif (n := len(data)) > 10:\n    print(f"Too long: {n}")\n```',
        '💡 **Python Tip:** Use `*` unpacking for elegant argument passing!\n```python\nargs = [3, 6]\nprint(range(*args))  # range(3, 6)\n```',
        '💡 **Python Tip:** `dict.get(key, default)` avoids KeyError exceptions safely!\n```python\nvalue = my_dict.get("key", "default_value")\n```',
        '💡 **Python Tip:** Use f-strings for fast, readable string formatting (Python 3.6+)!\n```python\nname = "Alice"\nprint(f"Hello, {name}!")\n```',
        '💡 **Python Tip:** Context managers ensure files are always closed properly!\n```python\nwith open("file.txt") as f:\n    data = f.read()\n```'
    ],

    python: {
        list: '📋 **Lists in Python:**\n\nLists are mutable, ordered collections.\n```python\nmy_list = [1, 2, 3]\nmy_list.append(4)    # [1, 2, 3, 4]\nmy_list.pop()        # removes last\nmy_list[0]           # index access\n```\n*Key methods:* `append`, `extend`, `pop`, `insert`, `remove`, `sort`, `reverse`',

        dict: '📖 **Dictionaries in Python:**\n\nDicts store key-value pairs (unordered, mutable).\n```python\nd = {"name": "Alice", "age": 25}\nprint(d["name"])      # Alice\nd["city"] = "NY"     # add key\nd.get("job", "N/A")  # safe access\n```\n*Key methods:* `keys()`, `values()`, `items()`, `get()`, `update()`',

        loop: '🔄 **Loops in Python:**\n\n```python\n# for loop\nfor i in range(5):\n    print(i)    # 0 1 2 3 4\n\n# while loop\nx = 10\nwhile x > 0:\n    x -= 3\n\n# Loop controls\nbreak     # exit loop\ncontinue  # skip iteration\npass      # placeholder\n```',

        function: '🧩 **Functions in Python:**\n\n```python\ndef greet(name, greeting="Hello"):\n    return f"{greeting}, {name}!"\n\n# Call it\ngreet("Alice")           # Hello, Alice!\ngreet("Bob", "Hi")       # Hi, Bob!\n\n# *args & **kwargs\ndef flex(*args, **kwargs):\n    print(args, kwargs)\n```',

        class: '🎯 **Classes & OOP:**\n\n```python\nclass Animal:\n    def __init__(self, name):\n        self.name = name\n\n    def speak(self):\n        return f"{self.name} makes a sound"\n\nclass Dog(Animal):\n    def speak(self):\n        return f"{self.name} says Woof!"\n\ndog = Dog("Rex")\nprint(dog.speak())  # Rex says Woof!\n```',

        exception: '⚠️ **Exception Handling:**\n\n```python\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError as e:\n    print(f"Error: {e}")\nexcept (TypeError, ValueError):\n    print("Type or Value error!")\nelse:\n    print("No error!")\nfinally:\n    print("Always runs")\n```',

        string: '🔤 **Strings in Python:**\n\nStrings are immutable sequences of characters.\n```python\ns = "Hello, World!"\ns.upper()        # HELLO, WORLD!\ns.lower()        # hello, world!\ns.split(", ")    # [\'Hello\', \'World!\']\ns.replace("o","0")  # Hell0, W0rld!\nlen(s)           # 13\ns[0:5]           # Hello\n```',

        lambda: '⚡ **Lambda Functions:**\n\nQuick anonymous functions for simple operations.\n```python\nsquare = lambda x: x ** 2\nprint(square(5))   # 25\n\n# With map/filter\nnums = [1, 2, 3, 4, 5]\nevens = list(filter(lambda x: x % 2 == 0, nums))\n# [2, 4]\n```'
    },

    encouragement: [
        '💪 You\'ve got this! Every expert was once a beginner. Keep pushing!',
        '🌟 Don\'t give up! Python mastery comes with practice. You\'re doing great!',
        '🚀 Progress > Perfection. The fact you\'re here means you\'re already ahead!',
        '✨ Learning is a journey, not a destination. Each question you try makes you stronger!'
    ],

    celebration: [
        '🎉 Amazing score! You\'re clearly a Python powerhouse! Keep that momentum!',
        '🏆 Outstanding performance! You should be proud of yourself!',
        '⭐ Brilliant work! You\'ve demonstrated genuine Python mastery!',
        '🌟 Top-tier results! You\'re on track to becoming a Python expert!'
    ],

    fallback: [
        '🤔 Hmm, I\'m not sure about that specific topic yet. Try asking about: **Python tips**, **quiz topics**, **grading**, or specific concepts like **lists**, **functions**, **classes**, or **loops**!',
        '🧠 That\'s an interesting question! I\'m best at Python concepts and quiz guidance. Try asking: "Give me a Python tip" or "Explain classes"!',
        '🔍 I didn\'t quite catch that. I can help with **Python concepts**, **quiz tips**, **grading info**, or **encouragement**. What would you like to explore?'
    ]
};

/* ── Utilities ──────────────────────────────────────────────── */
function now() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function rand(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function htmlify(text) {
    // Simple markdown-like rendering
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`([^`]+)`/g, '<code style="background:rgba(139,92,246,0.2);padding:1px 5px;border-radius:4px;font-size:0.85em;color:#c4b5fd">$1</code>')
        .replace(/```[\w]*\n?([\s\S]*?)```/g, '<pre style="background:rgba(0,0,0,0.4);border:1px solid rgba(139,92,246,0.2);border-radius:8px;padding:0.75rem;margin-top:0.5rem;overflow-x:auto;font-size:0.78em;color:#e2e8f0;line-height:1.5">$1</pre>')
        .replace(/\n/g, '<br>');
}

/* ── NLP Engine ─────────────────────────────────────────────── */
function processMessage(raw) {
    const text = raw.toLowerCase().trim();
    conversationHistory.push({ role: 'user', text: raw });

    // Greetings
    if (/^(hi|hey|hello|hiya|sup|yo|howdy|greetings)/i.test(text)) {
        return rand(KB.greetings);
    }

    // Farewells
    if (/\b(bye|goodbye|see ya|later|thanks bye|cya)\b/.test(text)) {
        return '👋 Goodbye! Good luck with the quiz — you\'ve totally got this! Come back anytime. 🌟';
    }

    // Thank you
    if (/\b(thanks|thank you|thx|ty|cheers)\b/.test(text)) {
        return '😊 You\'re so welcome! That\'s what I\'m here for. Anything else I can help with?';
    }

    // Topics
    if (/\b(topic|cover|what.*quiz|subject|content|question.*about)\b/.test(text)) {
        return KB.topics;
    }

    // Grading / score
    if (/\b(grade|grading|score|percentage|marks|points|how.*scored|evaluation)\b/.test(text)) {
        return KB.grading;
    }

    // Start quiz
    if (/\b(start|begin|how.*quiz|take quiz|attempt)\b/.test(text)) {
        return KB.start;
    }

    // Python tips
    if (/\b(tip|trick|pro tip|shortcut|best practice|advice|hint)\b/.test(text)) {
        return rand(KB.tips);
    }

    // Encouragement request
    if (/\b(struggle|hard|difficult|stuck|help|nervous|scared|fail|worried)\b/.test(text)) {
        userMood = 'struggling';
        return rand(KB.encouragement) + '\n\n' + rand(KB.tips);
    }

    // Celebration / good score
    if (/\b(great|excellent|awesome|perfect|amazing|100|90|ace|did well|scored high)\b/.test(text)) {
        userMood = 'confident';
        return rand(KB.celebration);
    }

    // Python concepts - Lists
    if (/\b(list|array|append|extend|pop|insert)\b/.test(text)) {
        return KB.python.list;
    }

    // Dict
    if (/\b(dict|dictionary|key.value|hash(map)?|mapping)\b/.test(text)) {
        return KB.python.dict;
    }

    // Loops
    if (/\b(loop|for loop|while|iterate|iteration|range|break|continue)\b/.test(text)) {
        return KB.python.loop;
    }

    // Functions
    if (/\b(function|def|return|argument|param|kwargs|args)\b/.test(text)) {
        return KB.python.function;
    }

    // Classes / OOP
    if (/\b(class|object|oop|inherit|instance|method|self|__init__)\b/.test(text)) {
        return KB.python.class;
    }

    // Exceptions
    if (/\b(exception|error|try|except|finally|raise|handle)\b/.test(text)) {
        return KB.python.exception;
    }

    // Strings
    if (/\b(string|str|char|concat|slice|upper|lower|split|replace|strip)\b/.test(text)) {
        return KB.python.string;
    }

    // Lambda
    if (/\b(lambda|anonymous|map|filter|arrow)\b/.test(text)) {
        return KB.python.lambda;
    }

    // What can you do / help
    if (/\b(what.*do|help|capability|feature|can you|abilities)\b/.test(text)) {
        return '🤖 **I can help you with:**\n\n• 📚 Explain **quiz topics** and what to expect\n• 💡 Share **Python tips & tricks**\n• 🎓 Break down **Python concepts** (lists, dicts, loops, classes…)\n• ⭐ Tell you about the **grading system**\n• 🚀 Guide you on **how to start the quiz**\n• 💪 Give you **encouragement** when you need it!\n\nJust type your question naturally and I\'ll do my best!';
    }

    // Who are you / about bot
    if (/\b(who are you|what are you|your name|about you)\b/.test(text)) {
        return '🤖 I\'m **PyBot**, your AI-powered Python quiz assistant! I was built to help you understand Python concepts, navigate the quiz, and celebrate your success. Think of me as your friendly coding companion. 🐍✨';
    }

    // Fallback
    return rand(KB.fallback);
}

/* ── DOM Rendering ──────────────────────────────────────────── */
function appendMessage(role, text, skipHistory = false) {
    const container = document.getElementById('chatbot-messages');
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;

    div.innerHTML = `
        <div class="chat-bubble">${htmlify(text)}</div>
        <div class="chat-time">${now()}</div>
    `;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;

    if (!skipHistory) {
        conversationHistory.push({ role, text });
    }
}

function showTypingIndicator() {
    const container = document.getElementById('chatbot-messages');
    const typing = document.createElement('div');
    typing.id = 'typing-indicator';
    typing.className = 'chat-msg bot';
    typing.innerHTML = `
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;
    container.appendChild(typing);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

/* ── Chat Logic ─────────────────────────────────────────────── */
function sendChatMessage() {
    const input = document.getElementById('chatbot-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';

    // Render user message
    appendMessage('user', text, true);

    // Hide suggestion chips after first real message
    const chips = document.getElementById('chat-suggestions');
    if (chips) chips.style.display = 'none';

    // Show typing indicator then respond
    showTypingIndicator();
    const delay = 700 + Math.random() * 700; // 700-1400ms realistic delay

    setTimeout(() => {
        removeTypingIndicator();
        const response = processMessage(text);
        appendMessage('bot', response, true);
    }, delay);
}

function sendSuggestion(text) {
    const input = document.getElementById('chatbot-input');
    input.value = text;
    sendChatMessage();
}

/* ── Toggle ─────────────────────────────────────────────────── */
function toggleChatbot() {
    const window_ = document.getElementById('chatbot-window');
    const btn = document.getElementById('chatbot-toggle-btn');
    const iconBot = document.getElementById('chat-icon-bot');
    const iconClose = document.getElementById('chat-icon-close');
    const notifDot = document.getElementById('chatbot-notif-dot');

    chatOpen = !chatOpen;

    if (chatOpen) {
        // Open
        window_.classList.remove('hidden');
        window_.classList.remove('closing');
        btn.classList.add('open');
        iconBot.style.display = 'none';
        iconClose.style.display = 'block';
        if (notifDot) notifDot.style.display = 'none';

        // First-time welcome
        if (!chatInitialised) {
            chatInitialised = true;
            setTimeout(() => {
                appendMessage('bot', '👋 Hey! I\'m **PyBot**, your AI Python tutor. I\'m here to help you conquer this quiz! 🐍\n\nAsk me about **Python concepts**, **quiz tips**, or try one of the quick buttons below!', true);
            }, 300);
        }

        // Focus input
        setTimeout(() => {
            document.getElementById('chatbot-input').focus();
        }, 400);

    } else {
        // Close with animation
        window_.classList.add('closing');
        btn.classList.remove('open');
        iconBot.style.display = 'block';
        iconClose.style.display = 'none';
        setTimeout(() => window_.classList.add('hidden'), 250);
    }
}

/* ── Proactive Nudge ────────────────────────────────────────── */
// After 12 seconds, gently nudge user to open chatbot
setTimeout(() => {
    if (!chatOpen && !chatInitialised) {
        const notifDot = document.getElementById('chatbot-notif-dot');
        if (notifDot) {
            notifDot.style.background = '#f59e0b';
            notifDot.title = 'PyBot has a tip for you!';
        }

        // Add a pulsing tooltip
        const btn = document.getElementById('chatbot-toggle-btn');
        if (btn) {
            const tooltip = document.createElement('div');
            tooltip.id = 'pybot-tooltip';
            tooltip.style.cssText = `
                position: absolute;
                right: 70px;
                bottom: 10px;
                background: linear-gradient(135deg, #7c3aed, #0891b2);
                color: white;
                padding: 0.5rem 0.85rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                white-space: nowrap;
                box-shadow: 0 4px 16px rgba(124,58,237,0.5);
                animation: tooltipPop 0.4s cubic-bezier(0.34,1.56,0.64,1);
                z-index: 1000;
            `;
            tooltip.innerHTML = '💡 Need help? Ask me!';

            // Inject tooltip animation CSS
            if (!document.getElementById('tooltip-style')) {
                const style = document.createElement('style');
                style.id = 'tooltip-style';
                style.textContent = `
                    @keyframes tooltipPop {
                        from { opacity: 0; transform: scale(0.7) translateX(10px); }
                        to   { opacity: 1; transform: scale(1) translateX(0); }
                    }
                    #pybot-tooltip::after {
                        content: '';
                        position: absolute;
                        right: -7px;
                        top: 50%;
                        transform: translateY(-50%);
                        border: 7px solid transparent;
                        border-right: none;
                        border-left-color: #0891b2;
                    }
                `;
                document.head.appendChild(style);
            }

            const widget = document.getElementById('chatbot-widget');
            if (widget) {
                widget.style.position = 'fixed';
                widget.appendChild(tooltip);
                setTimeout(() => tooltip.remove(), 5000);
            }
        }
    }
}, 12000);
