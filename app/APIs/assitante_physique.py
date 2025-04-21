from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import openai
import os
import json

# For Groq (uses OpenAI-compatible API)
client = openai.OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

router = APIRouter()

# File path for storing session history
HISTORY_FILE = os.path.join(os.getcwd(), "history.json")

# Initialize the history file if not present
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)


# Read chat history from file
def read_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# Write chat history to file
def write_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


class ChatRequest(BaseModel):
    message: str


@router.post("/", summary="Chat with AI assistant")
async def chat_with_assistant(request: ChatRequest, session_id: str = Query("default")):
    try:
        # Load previous history for this session
        history_data = read_history()
        session_history = history_data.get(session_id, [])

        # Prepare prompt
        messages = [
                       {
                           "role": "system",
                           "content": (
                               "You are a kind, supportive assistant helping people with dyslexia. "
                               "Respond in the same language the user used: Arabic, French, or English. "
                               "Keep your answers short and simple to understand. Use short sentences and friendly tone. "
                               "Avoid giving long paragraphs. "
                               "Don't mix languages in one message."
                               "if user talk in arabic then answer in arabic"
                               "when talking in arabic, don't use any other language words"
                           )
                       }
                   ] + session_history + [{"role": "user", "content": request.message}]

        # Send to Groq
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages
        )

        assistant_reply = response.choices[0].message.content

        # Update session history (max 10 messages = 5 interactions)
        session_history.append({"role": "user", "content": request.message})
        session_history.append({"role": "assistant", "content": assistant_reply})
        session_history = session_history[-10:]

        history_data[session_id] = session_history
        write_history(history_data)

        return {"response": assistant_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
