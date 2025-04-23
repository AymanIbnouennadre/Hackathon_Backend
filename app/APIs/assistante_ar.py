import os
import json
import base64
import logging
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv

# ==== CONFIGURATION ====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AssistVocalAr")

load_dotenv()

HISTORY_FILE = Path("history_ar.json")
MAX_HISTORY = 100
DEFAULT_SESSION_ID = "default"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Clé API GROQ manquante dans .env")

groq_client = Groq(api_key=GROQ_API_KEY)

router = APIRouter()

# ==== INITIALISATION ====
def init_history():
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text(json.dumps({}, indent=2), encoding="utf-8")

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
        "أنتِ مساعدة صوتية تمثلين أخصائية نطق.\n"
        "تتحدثين مع أطفال يعانون من عسر القراءة أو مع أوليائهم.\n"
        "تحدثي بلغة بسيطة وبأسلوب مشجع واحترافي.\n"
        "- أجيبي بجملة أو جملتين فقط، أو ثلاث جمل كحد أقصى إذا دعت الحاجة.\n"
        "- لا تخلطي بين اللغات في نفس الجواب.\n"
    )}] + [
                   {"role": msg["role"], "content": msg["content"]} for msg in cleaned
               ]

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=130,  # 👈 pour éviter les réponses longues
            temperature=0.5
        )

        answer = response.choices[0].message.content.strip()
        cleaned.append({"role": "assistant", "content": answer, "timestamp": datetime.now().isoformat()})
        history[session_id] = cleaned
        write_history(history)
        return answer
    except Exception as e:
        logger.error(f"Erreur API Groq: {e}")
        return "عذرًا، حدث خطأ أثناء معالجة الطلب."

def synthesize_speech(text: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            gTTS(text=text, lang="ar").save(temp_audio.name)
            return temp_audio.name
    except Exception as e:
        logger.error(f"Erreur synthèse vocale: {e}")
        raise HTTPException(status_code=500, detail="خطأ في توليد الصوت.")

def clean_temp_files(*paths):
    for path in paths:
        if path and Path(path).exists():
            try:
                Path(path).unlink()
            except Exception as e:
                logger.warning(f"Erreur suppression {path}: {e}")

# ==== ROUTE ====
@router.post("/")
async def assist_vocal_ar(request: AssistVocalRequest):
    session_id = request.session_id
    transcription = request.text.strip()

    if not transcription:
        raise HTTPException(status_code=400, detail="النص المقدم فارغ.")

    temp_audio_path = None
    try:
        response_text = generate_response(transcription, session_id)
        temp_audio_path = synthesize_speech(response_text)
        audio_b64 = base64.b64encode(Path(temp_audio_path).read_bytes()).decode("utf-8")

        return {
            "langue_detectee": "ar",
            "transcription": transcription,
            "response": response_text,
            "audio_content": audio_b64,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur traitement: {str(e)}")
    finally:
        clean_temp_files(temp_audio_path)