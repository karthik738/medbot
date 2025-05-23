import os
import re
import json
import requests
from datetime import datetime
from gtts import gTTS
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv

# === ENV SETUP ===
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}
MODEL = "anthropic/claude-3-haiku"

# # === TTS SETUP ===
# engine = pyttsx3.init()
# engine.setProperty('rate', 180)
# tts_enabled = True

# def speak(text):
#     if tts_enabled:
#         try:
#             engine.say(text)
#             engine.runAndWait()
#         except Exception as e:
#             print(f"[TTS Error] {str(e)}")

# def set_tts(enabled: bool):
#     global tts_enabled
#     tts_enabled = enabled

# === TTS SETUP ===
tts_enabled = True
tts_supported = os.getenv("SPACE_ENVIRONMENT") != "huggingface"

def set_tts(enabled: bool):
    global tts_enabled
    tts_enabled = enabled

def speak(text: str):
    if not tts_enabled or not tts_supported:
        return
    try:
        tts = gTTS(text)
        with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            os.system(f"start {tmp.name}" if os.name == 'nt' else f"mpg123 {tmp.name}")
            os.remove(tmp.name)
    except Exception as e:
        print(f"[TTS Error] {str(e)}")

# === SESSION SAVE ===
SAVE_DIR = "chat_logs"
os.makedirs(SAVE_DIR, exist_ok=True)

def save_chat_session(responses: dict, messages: list, recommendation: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_{timestamp}.json"
    path = os.path.join(SAVE_DIR, filename)

    session_data = {
        "timestamp": timestamp,
        "user_responses": responses,
        "chat_history": messages,
        "recommendation": recommendation,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=4)

# === USER STATE ===
user_state = {
    "stage": "intro",
    "responses": {},
}

# === QUESTION FLOW ===
questions = [
    {
        "key": "age",
        "text": "What is your age?",
        "type": "int",
        "validation": lambda val: val.isdigit() and 0 < int(val) < 120,
        "error": "Please enter a valid age between 1 and 120."
    },
    {
        "key": "fever",
        "text": "Do you have a fever? (yes/no)",
        "type": "yesno",
        "validation": lambda val: val.lower() in ["yes", "no"],
        "error": "Please answer with yes or no."
    },
    {
        "key": "cough",
        "text": "Are you experiencing cough or chest pain? (yes/no)",
        "type": "yesno",
        "validation": lambda val: val.lower() in ["yes", "no"],
        "error": "Please answer with yes or no."
    },
    {
        "key": "chronic",
        "text": "Do you have any chronic conditions? (yes/no)",
        "type": "yesno",
        "validation": lambda val: val.lower() in ["yes", "no"],
        "error": "Please answer with yes or no."
    },
    {
        "key": "chills",
        "text": "Since you have a fever, do you also have chills or body aches? (yes/no)",
        "depends_on": {"fever": "yes"},
        "type": "yesno",
        "validation": lambda val: val.lower() in ["yes", "no"],
        "error": "Please answer with yes or no."
    }
]

def reset_user_state():
    global user_state
    user_state = {
        "stage": "intro",
        "responses": {},
    }

def infer_yes_no(user_input):
    cleaned = user_input.lower().strip()
    if re.search(r"\b(yes|yeah|yep|i do|i am|sure|of course)\b", cleaned):
        return "yes"
    elif re.search(r"\b(no|nah|nope|i don’t|i do not|not really|i am not)\b", cleaned):
        return "no"
    return None

def query_openrouter(prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly virtual doctor. Respond in second person only. "
                "Give a short, kind explanation of what the user might be facing. "
                "Do not repeat already known symptoms. Be medically helpful but clear."
            )
        },
        {"role": "user", "content": prompt}
    ]

    data = {
        "model": MODEL,
        "messages": messages,
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=HEADERS,
            json=data,
            timeout=20
        )
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM Error: {str(e)}"

def get_next_question():
    for q in questions:
        key = q["key"]
        if key not in user_state["responses"]:
            if "depends_on" in q:
                if not all(user_state["responses"].get(k) == v for k, v in q["depends_on"].items()):
                    continue
            return q
    return None

def format_summary_prompt():
    summary = "\n".join([f"{k}: {v}" for k, v in user_state["responses"].items()])
    return f"Based on these user symptoms, provide a helpful diagnosis and suggestions:\n{summary}"

def handle_user_message(user_input, chat_history):
    global user_state

    user_input = user_input.strip()

    if user_input.lower() == "hi" and user_state["stage"] == "done":
        reset_user_state()

    if user_state["stage"] == "intro":
        bot_msg = (
            "👋 Hello! I'm your virtual health assistant. I'll ask a few questions and suggest what to do.\n\n"
            + questions[0]["text"]
        )
        user_state["stage"] = "questions"
        chat_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": bot_msg},
        ])
        speak(bot_msg)
        return bot_msg, chat_history

    elif user_state["stage"] == "questions":
        question = get_next_question()
        if question:
            key = question["key"]
            input_value = user_input.lower()

            if question["type"] == "yesno":
                inferred = infer_yes_no(input_value)
                if inferred:
                    input_value = inferred
                else:
                    bot_msg = question["error"]
                    chat_history.extend([
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": bot_msg},
                    ])
                    speak(bot_msg)
                    return bot_msg, chat_history

            if question["type"] == "int" and not question["validation"](input_value):
                bot_msg = question["error"]
                chat_history.extend([
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": bot_msg},
                ])
                speak(bot_msg)
                return bot_msg, chat_history

            user_state["responses"][key] = int(input_value) if question["type"] == "int" else input_value

            if (
                user_state["responses"].get("fever") == "yes"
                and user_state["responses"].get("cough") == "yes"
                and user_state["responses"].get("chills") == "yes"
            ):
                prompt = format_summary_prompt()
                advice = query_openrouter(prompt)
                user_state["stage"] = "done"
                chat_history.extend([
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": advice},
                ])
                speak(advice)
                save_chat_session(user_state["responses"], chat_history, advice)
                return advice, chat_history

            next_q = get_next_question()
            if next_q:
                bot_msg = next_q["text"]
            else:
                user_state["stage"] = "done"
                prompt = format_summary_prompt()
                bot_msg = query_openrouter(prompt)
                save_chat_session(user_state["responses"], chat_history, bot_msg)

            chat_history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": bot_msg},
            ])
            speak(bot_msg)
            return bot_msg, chat_history

    elif user_state["stage"] == "done":
        bot_msg = "✅ You've completed the health check. Refresh or type 'hi' to start over."
        chat_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": bot_msg},
        ])
        speak(bot_msg)
        return bot_msg, chat_history
