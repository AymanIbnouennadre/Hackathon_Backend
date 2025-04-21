from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
import io

# Initialize APIRouter instead of FastAPI
router = APIRouter()

# Model for validating input data
class SpeechRequest(BaseModel):
    text: str
    lang: str

@router.post("/")
async def generate_speech(request: SpeechRequest):
    try:
        # Check that the text is not empty
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Create the gTTS object
        tts = gTTS(text=request.text, lang=request.lang, slow=False)

        # Save the audio to an in-memory buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        # Return the audio file as a streaming response
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )

    except Exception as e:
        # Handle errors (e.g., unsupported language or gTTS issues)
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")