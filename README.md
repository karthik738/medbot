# 🧠 Smart Medical Chatbot with Voice

An AI-powered medical assistant that interacts like a virtual doctor:
- Collects symptoms via a dynamic questionnaire
- Provides basic, friendly medical suggestions using an LLM (Claude via OpenRouter)
- Reads out questions and answers using Text-to-Speech (TTS)
- Stores chat sessions for record keeping in JSON format

---

## ✅ Features

- 🔄 Rule-based + dynamic questioning
- 🧠 LLM-generated medical suggestions (Claude 3 via OpenRouter)
- 🗣️ Voice response using `pyttsx3`
- 💾 JSON chat session logging
- 🔘 Toggle TTS from UI (Gradio-based)
- ♻️ Smart validation and yes/no inference from user text

---

## 📦 Requirements

Install all dependencies using:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install gradio pyttsx3 requests python-dotenv
```

---

## 🔐 .env file

Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

## 🚀 How to Run

```bash
python app.py
```

This will launch the Gradio interface.

---

## 🧪 Sample Conversation

```
Bot: Hello! I'm your virtual health assistant. What is your age?
User: 23
Bot: Do you have a fever? (yes/no)
User: yes, I think I do
Bot: Are you experiencing cough or chest pain? (yes/no)
User: no
Bot: Do you have any chronic conditions? (yes/no)
User: no
Bot: Do you have chills or body aches? (yes/no)
User: yes
Bot: Based on your symptoms, it seems like you may have a mild viral infection...
```

---

## 📁 Project Structure

```
.
├── app.py                  # Gradio frontend
├── chatbot_logic.py        # Main chatbot logic
├── .env                    # OpenRouter API key
├── chat_logs/              # Stored conversations
├── README.md               # You're reading this!
├── .gitignore              # Excludes cache/env/logs
```

---

## 📝 .gitignore

```gitignore
__pycache__/
*.pyc
.env
chat_logs/
venv/
.env/
.DS_Store
```

---

## 🔮 Future Add-ons

- 🎤 Voice input (speech recognition)
- 🌐 Deploy to HuggingFace or Render
- 📱 Convert to a web/mobile app
- 🧠 Integrate fine-tuned models for diagnosis

---

## 👨‍⚕️ Built with ❤️ for smarter, accessible healthcare tech.