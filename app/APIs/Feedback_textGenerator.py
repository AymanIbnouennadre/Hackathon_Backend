from fastapi import APIRouter, Form
from dotenv import load_dotenv
import os
from google import genai

# Charger les variables d'environnement
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Créer le client Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

router = APIRouter()

@router.post("/")
async def generer_feedback(
    type_exercice: str = Form(...),  # "prononciation" ou "quiz"
    mot_attendu: str = Form(None),
    transcription_patient: str = Form(None),
    choix_correct: str = Form(None),
    choix_patient: str = Form(None),
    langue: str = Form("fr")
):
    if type_exercice == "prononciation":
        if langue == "ar":
            prompt = (
                f"الكلمة التي يجب نطقها هي: '{mot_attendu}'. "
                f"المريض نطقها: '{transcription_patient}'. "
                "هل نطق الكلمة بشكل صحيح؟ أجب بجملة واحده فقط، بطريقة مشجعة ولطيفة، وكأنك أخصائي نطق يعمل مع طفل يعاني من عسر القراءة."
            )
        else:
            prompt = (
                f"Le mot à prononcer est : '{mot_attendu}'. "
                f"Le patient a prononcé : '{transcription_patient}'. "
                "Réponds par une seule phrase , de façon bienveillante et motivante, comme un orthophoniste s’adressant à un enfant dyslexique."
            )

    elif type_exercice == "quiz":
        if langue == "ar":
            prompt = (
                f"الجواب الصحيح هو: '{choix_correct}'، واختيار الطفل هو: '{choix_patient}'. "
                "اعتمد على هذه المعلومات لإعطاء ملاحظات. "
                "إذا كانت الإجابة صحيحة، شجعه بكلمات إيجابية. إذا كانت خاطئة، صحح له بلطف، "
                "لكن لا تذكر الجواب الصحيح أبدًا في ردك. اجعل ردك بجملة واحده فقط، بطريقة مشجعة."
            )
        else:
            prompt = (
                f"La bonne réponse est : '{choix_correct}'. "
                f"L'enfant a choisi : '{choix_patient}'. "
                "Utilise cette information pour juger la réponse. "
                "S'il a bien répondu, félicite-le chaleureusement. "
                "Sinon, encourage-le avec douceur sans jamais révéler la bonne réponse. "
                "Réponds en une seule phrase motivante, comme un orthophoniste."
            )
    else:
        return {"error": "type_exercice invalide. Utilise 'prononciation' ou 'quiz'."}

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return {"feedback": response.text}
    except Exception as e:
        return {"error": str(e)}
