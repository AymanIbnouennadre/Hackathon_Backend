from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
import os

# For Groq (uses OpenAI-compatible API)
client = openai.OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

router = APIRouter()

@router.post("/")
async def chat_with_assistant(request: str):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant supporting patients with dyslexia."},
                {"role": "user", "content": request}
            ]
        )
        return {"response": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
