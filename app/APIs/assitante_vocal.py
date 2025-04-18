import os
import base64
import logging
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from gtts import gTTS
from dotenv import load_dotenv
from groq import Groq

from ..model import model  # Assure-toi que ce modèle est correctement chargé

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# Initialisations
router = APIRouter()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MAX_FILE_SIZE_MB = 5


def transcribe_audio(file_path: str) -> tuple[str, str]:
    try:
        segments, info = model.transcribe(file_path)
        transcription = " ".join([segment.text for segment in segments])
        detected_lang = getattr(info, "language", "fr")
        return transcription, detected_lang
    except Exception as e:
        logger.exception("Erreur de transcription Whisper")
        raise HTTPException(status_code=500, detail="Erreur lors de la transcription")


def generate_groq_response(transcription: str, lang: str) -> str:
    try:
        prompt_lang = "arabe" if lang == "ar" else "français"
        prompt = f"Vous êtes une assistante vocale. Répondez brièvement en {prompt_lang} à : '{transcription}'."

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Vous êtes une assistante vocale intelligente."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Erreur Groq API")
        return "Désolé, je n'ai pas pu traiter votre demande." if lang == "fr" else "عذرا، لم أتمكن من معالجة طلبك."


def synthesize_speech(text: str, lang: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_audio.name)
            return temp_audio.name
    except Exception as e:
        logger.exception("Erreur gTTS")
        raise HTTPException(status_code=500, detail="Erreur lors de la synthèse vocale")


@router.post("/")
async def assist_vocal(file: UploadFile = File(...)):
    if file.size and file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux")

    temp_path = ""
    audio_path = ""

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(await file.read())

        transcription, detected_lang = transcribe_audio(temp_path)
        logger.info(f"Transcription: {transcription}, Langue: {detected_lang}")

        lang = "ar" if detected_lang == "ar" else "fr"
        response_text = generate_groq_response(transcription, lang)
        audio_path = synthesize_speech(response_text, lang)

        with open(audio_path, "rb") as audio_file:
            audio_content = base64.b64encode(audio_file.read()).decode("utf-8")

        return {
            "langue_detectee": lang,
            "transcription": transcription,
            "response": response_text,
            "audio_content": audio_content
        }

    finally:
        for path in [temp_path, audio_path]:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.warning(f"Erreur nettoyage ({path}) : {e}")
