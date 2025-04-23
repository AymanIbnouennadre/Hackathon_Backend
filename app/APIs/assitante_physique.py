from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import openai
import os
import json
from langdetect import detect

# Groq (OpenAI-compatible API)
client = openai.OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

router = APIRouter()

# History file mapping by language
HISTORY_FILES = {
    "ar": os.path.join(os.getcwd(), "history_Chabot_ar.json"),
    "fr": os.path.join(os.getcwd(), "history_Chatbot_fr.json"),
    "default": os.path.join(os.getcwd(), "history_default.json")
}

# Ensure all history files exist
for path in HISTORY_FILES.values():
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)

# Detect language
def detect_language(text):
    try:
        lang = detect(text)
        if lang == "ar":
            return "ar"
        elif lang == "fr":
            return "fr"
        else:
            return "default"
    except:
        return "default"

# Read chat history
def read_history(lang):
    file_path = HISTORY_FILES.get(lang, HISTORY_FILES["default"])
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# Write chat history
def write_history(history, lang):
    file_path = HISTORY_FILES.get(lang, HISTORY_FILES["default"])
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

# Request model
class ChatRequest(BaseModel):
    message: str

# Main chat route
@router.post("/", summary="Chat with AI assistant")
async def chat_with_assistant(request: ChatRequest, session_id: str = Query("default")):
    try:
        # Detect language
        language = detect_language(request.message)

        # Load history for the session in that language
        history_data = read_history(language)
        session_history = history_data.get(session_id, [])

        # Prompt with clear language separation
        system_prompt = (
            "You are a kind and supportive assistant who helps people with dyslexia.\n\n"
            "Rules:\n"
            "- Always respond in the same language the user used: Arabic, French, or English.\n"
            "- When the user speaks Arabic, your answer must be entirely in Arabic only.\n"
            "- Never mix languages in a single message.\n"
            "- Use short, simple sentences with a friendly tone.\n"
            "- Avoid long paragraphs or complicated words.\n"
            "- Keep your replies under 100 tokens whenever possible.\n"
        )

        messages = [{"role": "system", "content": system_prompt}] + session_history + [
            {"role": "user", "content": request.message}
        ]

        # Send request to Groq (LLaMA 3)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=100,
            temperature=0.5
        )

        assistant_reply = response.choices[0].message.content

        # Update and trim session history
        session_history.append({"role": "user", "content": request.message})
        session_history.append({"role": "assistant", "content": assistant_reply})
        session_history = session_history[-10:]

        history_data[session_id] = session_history
        write_history(history_data, language)

        return {"response": assistant_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))