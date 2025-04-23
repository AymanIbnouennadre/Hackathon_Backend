import os
import json
import base64
import logging
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv

# ==== CONFIGURATION ====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AssistVocal")

load_dotenv()

HISTORY_FILE = Path("history.json")
MAX_HISTORY = 5
DEFAULT_SESSION_ID = "default"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Clé API GROQ manquante dans le fichier .env")

groq_client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()
router = APIRouter()

# ==== INITIALISATION ====
def init_history():
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text(json.dumps({}, indent=2), encoding="utf-8")
        logger.info("Fichier d'historique initialisé.")

def read_history():
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Erreur lecture historique: {e}")
        return {}

def write_history(data):
    try:
        HISTORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.error(f"Erreur écriture historique: {e}")
        raise HTTPException(status_code=500, detail="Erreur d'enregistrement de l'historique.")

init_history()

# ==== SCHEMA ====
class AssistVocalRequest(BaseModel):
    text: str
    session_id: str = DEFAULT_SESSION_ID

# ==== MODULES ====
def generate_response(transcription: str, session_id: str) -> str:
    history = read_history()
    session = history.get(session_id, [])

    cleaned = [
        {
            "role": msg["role"],
            "content": msg["content"],
            "timestamp": msg.get("timestamp", datetime.now().isoformat())
        }
        for msg in session if isinstance(msg, dict) and "role" in msg and "content" in msg
    ]

    cleaned.append({"role": "user", "content": transcription, "timestamp": datetime.now().isoformat()})
    cleaned = cleaned[-MAX_HISTORY:]

    messages = [{"role": "system", "content": (
        "Tu es une assistante vocale qui incarne une orthophoniste.\n"
        "Tu échanges avec des enfants dyslexiques ou avec leurs parents.\n"
        "Adapte ton langage et ton ton à la personne en face de toi, avec bienveillance et professionnalisme.\n"
        "- Réponds en 1 ou 2 phrases, ou 3 maximum en cas de besoin.\n"
        "- Utilise un langage simple et amical.\n"
    "- Garde tes réponses courtes, en dessous de 130 tokens si possible."
    )}] + [
                   {"role": msg["role"], "content": msg["content"]} for msg in cleaned
               ]

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=130,  # 👈 idéal pour des réponses concises
            temperature=0.5  # 👈 moins de "blabla" créatif, plus de précision
        )

        answer = response.choices[0].message.content.strip()
        cleaned.append({"role": "assistant", "content": answer, "timestamp": datetime.now().isoformat()})
        history[session_id] = cleaned
        write_history(history)
        return answer
    except Exception as e:
        logger.error(f"Erreur API Groq: {e}")
        return "Désolé, une erreur s'est produite."

def synthesize_speech(text: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            gTTS(text=text, lang="fr").save(temp_audio.name)
            return temp_audio.name
    except Exception as e:
        logger.error(f"Erreur synthèse vocale: {e}")
        raise HTTPException(status_code=500, detail="Erreur de synthèse vocale.")

def clean_temp_files(*paths):
    for path in paths:
        if path and Path(path).exists():
            try:
                Path(path).unlink()
                logger.debug(f"Fichier temporaire supprimé: {path}")
            except Exception as e:
                logger.warning(f"Erreur suppression {path}: {e}")

# ==== ROUTE ====
@router.post("/")
async def assist_vocal(request: AssistVocalRequest):
    session_id = request.session_id
    transcription = request.text.strip()

    if not transcription:
        raise HTTPException(status_code=400, detail="Texte vide fourni.")

    audio_path = None
    try:
        response_text = generate_response(transcription, session_id)
        audio_path = synthesize_speech(response_text)
        audio_b64 = base64.b64encode(Path(audio_path).read_bytes()).decode("utf-8")

        return {
            "langue_detectee": "fr",
            "transcription": transcription,
            "response": response_text,
            "audio_content": audio_b64,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur traitement: {str(e)}")
    finally:
        clean_temp_files(audio_path)

app.include_router(router)

# ==== NETTOYAGE AUTOMATIQUE HISTORIQUE ====
def clean_old_history(days: int = 30):
    try:
        history = read_history()
        cutoff = datetime.now() - timedelta(days=days)
        for session_id in list(history.keys()):
            history[session_id] = [
                msg for msg in history[session_id]
                if datetime.fromisoformat(msg["timestamp"]) >= cutoff
            ]
            if not history[session_id]:
                del history[session_id]
        write_history(history)
        logger.info(f"Historique nettoyé (> {days} jours).")
    except Exception as e:
        logger.error(f"Erreur nettoyage historique: {e}")