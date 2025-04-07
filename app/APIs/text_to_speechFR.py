from gtts import gTTS
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter()


@router.post("/")
async def synthesize_text_fr(text: str):
    try:
        # Générer le son à partir du texte en français
        tts = gTTS(text=text, lang='fr')

        # Créer un buffer en mémoire
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        # Retourner le streaming response directement
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mp3",
            headers={"Content-Disposition": "inline"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in TTS processing: {str(e)}")