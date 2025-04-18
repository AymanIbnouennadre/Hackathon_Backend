import os
import tempfile
import base64
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv
from ..model import model  # Whisper model (assurez-vous que c'est configuré correctement)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()


router = APIRouter()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Transcribe audio with Whisper
def transcribe_audio(file_path: str) -> tuple:
    try:
        segments, info = model.transcribe(file_path)
        transcription = " ".join([segment.text for segment in segments])
        detected_lang = getattr(info, "language", "fr")
        return transcription, detected_lang
    except Exception as e:
        logger.error(f"Whisper transcription error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la transcription")

# Generate response with Groq
def generate_groq_response(transcription: str, lang: str) -> str:
    try:
        prompt = (
            f"Vous êtes une assistante vocale. Répondez brièvement en {'arabe' if lang == 'ar' else 'français'} à : '{transcription}'."
        )
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Modèle plus léger
            messages=[
                {"role": "system", "content": "Vous êtes une assistante vocale intelligente."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "Désolé, je n'ai pas pu traiter votre demande." if lang == "fr" else "عذرا، لم أتمكن من معالجة طلبك."

# Synthesize speech with gTTS
def synthesize_speech(text: str, lang: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            output_path = temp_audio.name
            tts = gTTS(text=text, lang=lang)
            tts.save(output_path)
        return output_path
    except Exception as e:
        logger.error(f"gTTS error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la synthèse vocale")

# Main route
@router.post("/")
async def assist_vocal(file: UploadFile = File(...)):
    # Vérifier la taille du fichier (limite à 5MB)
    content_length = file.size
    max_size = 5 * 1024 * 1024  # 5MB
    if content_length and content_length > max_size:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = temp_file.name
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

    try:
        # Transcription
        transcription, detected_lang = transcribe_audio(temp_path)
        logger.info(f"Transcription: {transcription}, Langue: {detected_lang}")

        # Définir la langue (arabe ou français)
        lang = "ar" if detected_lang == "ar" else "fr"

        # Générer la réponse
        response_text = generate_groq_response(transcription, lang)

        # Synthèse vocale
        audio_path = synthesize_speech(response_text, lang)

        # Lire le fichier audio en base64
        with open(audio_path, "rb") as audio_file:
            audio_content = base64.b64encode(audio_file.read()).decode("utf-8")

        return {
            "langue_detectee": lang,
            "transcription": transcription,
            "response": response_text,
            "audio_content": audio_content
        }

    finally:
        # Nettoyage des fichiers temporaires
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage des fichiers: {e}")

# Ajouter le routeur à l'application
app.include_router(router)