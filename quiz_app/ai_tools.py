# quiz_app/ai_tools.py
import os
import json
import urllib.request
import urllib.error

def get_api_key():
    """Retrieve Gemini API Key from environment variables."""
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def call_gemini_api(prompt: str, system_instruction: str = None) -> dict:
    """
    Sends a request to the Google Gemini API, requesting a JSON response.
    Returns the parsed JSON dictionary.
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError("Gemini API key is not configured. Please add GEMINI_API_KEY=your_key in your .env file.")

    # Using gemini-1.5-flash for fast and cost-effective generation
    model_name = "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    contents = {
        "parts": [{"text": prompt}]
    }

    payload = {
        "contents": [contents],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            
            # Extract text from standard Gemini response structure
            candidates = res_data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini API returned an empty response (no candidates).")
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise ValueError("Gemini API response structure is missing the parts field.")
            
            text_response = parts[0].get("text", "").strip()
            
            # Parse the text response as JSON
            return json.loads(text_response)
            
    except urllib.error.HTTPError as e:
        status_code = e.code
        error_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(error_body)
            msg = err_json.get("error", {}).get("message", error_body)
        except Exception:
            msg = error_body
        raise RuntimeError(f"Gemini API HTTP {status_code} Error: {msg}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Gemini API Connection Error: {e.reason}")
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse Gemini AI response as valid JSON.")
    except Exception as e:
        raise RuntimeError(f"AI Service Error: {str(e)}")

def generate_ai_question(topic: str, difficulty: str, prompt_guidance: str = None) -> dict:
    """
    Generates a Python multiple choice question.
    """
    system_instruction = (
        "You are an expert Python curriculum developer and tutor. Your task is to generate "
        "one high-quality multiple choice question testing Python coding skills.\n"
        "You must return a JSON object with the exact fields:\n"
        "{\n"
        "  \"question\": \"The question prompt or description (use formatted code blocks if including code snippet)\",\n"
        "  \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
        "  \"answer\": \"The correct option text (must exactly match one of the items in the options list)\",\n"
        "  \"topic\": \"The specific python topic (e.g. Lists, OOP, Exceptions, Loops)\"\n"
        "}\n"
        "Ensure the question is correct, educational, and fits the requested difficulty level.\n"
        "Do not include any extra text outside of the JSON block."
    )

    prompt = f"Generate a Python quiz question.\nTopic: {topic}\nDifficulty: {difficulty}"
    if prompt_guidance:
        prompt += f"\nSpecial Guidelines/Focus: {prompt_guidance}"

    question_data = call_gemini_api(prompt, system_instruction)

    # Validate output structure
    required_fields = ["question", "options", "answer", "topic"]
    for field in required_fields:
        if field not in question_data:
            raise ValueError(f"AI response is missing the required field: {field}")

    if not isinstance(question_data["options"], list) or len(question_data["options"]) < 2:
        raise ValueError("AI response 'options' must be a list of at least 2 strings.")

    # Standardize options to exactly 4 for consistent layout, matching admin.html form
    options = [str(opt).strip() for opt in question_data["options"]]
    while len(options) < 4:
        options.append(f"Dummy Option {len(options) + 1}")
    if len(options) > 4:
        options = options[:4]
    question_data["options"] = options

    # Ensure correct answer matches one of the options
    answer = str(question_data["answer"]).strip()
    if answer not in options:
        # Fallback: check if the answer specifies a letter like "A" or "Option A"
        # Or just pick the first option as fallback to prevent crash
        question_data["answer"] = options[0]
    else:
        question_data["answer"] = answer

    # Keep topic clean
    question_data["topic"] = str(question_data.get("topic", topic)).strip()
    return question_data

def modify_ai_question(question: str, options: list, answer: str, topic: str, instruction: str) -> dict:
    """
    Modifies an existing Python question based on instructions.
    """
    system_instruction = (
        "You are an expert Python curriculum developer. Your task is to modify an existing "
        "multiple choice question based on the user's instructions (e.g. make it harder, "
        "simplify wording, change variable names, fix typos).\n"
        "You must return the updated question details in a JSON object with the exact fields:\n"
        "{\n"
        "  \"question\": \"The modified question text\",\n"
        "  \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
        "  \"answer\": \"The updated correct option text (must exactly match one of the items in the options list)\",\n"
        "  \"topic\": \"The topic (updated if needed, otherwise kept as before)\"\n"
        "}\n"
        "Do not include any extra text outside of the JSON block."
    )

    current_data = {
        "question": question,
        "options": options,
        "answer": answer,
        "topic": topic
    }

    prompt = (
        f"Modify the following question:\n"
        f"{json.dumps(current_data, indent=2)}\n\n"
        f"Modification Instructions: {instruction}"
    )

    question_data = call_gemini_api(prompt, system_instruction)

    # Validate output structure
    required_fields = ["question", "options", "answer", "topic"]
    for field in required_fields:
        if field not in question_data:
            raise ValueError(f"AI response is missing the required field: {field}")

    # Standardize options to exactly 4
    options = [str(opt).strip() for opt in question_data["options"]]
    while len(options) < 4:
        options.append(f"Dummy Option {len(options) + 1}")
    if len(options) > 4:
        options = options[:4]
    question_data["options"] = options

    # Ensure answer is one of the options
    answer = str(question_data["answer"]).strip()
    if answer not in options:
        question_data["answer"] = options[0]
    else:
        question_data["answer"] = answer

    return question_data
