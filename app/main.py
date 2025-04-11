from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.APIs.image_to_textFR import router as fr_router
from app.APIs.image_to_textAR import router as ar_router
from app.APIs.text_to_speechFR import router as tts_fr_router
from app.APIs.text_to_speechAR import router as tts_ar_router
from  app.APIs.speech_to_textAR import router as stt_ar_router
from app.APIs.speech_to_textFR import router as stt_fr_router
from app.APIs.assitante_vocal import router as assist_vocal
from app.APIs.assitante_physique import router as assist_physique
from app.APIs.Feedback_textGenerator import router as feedback_text_generator
# ✅ Initialisation de FastAPI
app = FastAPI()

# ✅ Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Inclure les routeurs des différentes APIs
app.include_router(fr_router, prefix="/convert-image-to-textFR", tags=["OCR French"])
app.include_router(ar_router, prefix="/convert-image-to-textAR", tags=["OCR Arabic"])

# ✅ Inclure les routeurs des APIs TTS
app.include_router(tts_fr_router, prefix="/convert-text-to-speechFR", tags=["TTS French"])
app.include_router(tts_ar_router, prefix="/convert-text-to-speechAR", tags=["TTS Arabic"])

# ✅ Inclure les routeurs des APIs TTS
app.include_router(stt_ar_router, prefix="/convert-speech-to-textAR", tags=["STT Arabic"])
app.include_router(stt_fr_router, prefix="/convert-speech-to-textFR", tags=["STT French"])

# ✅ Inclure les routeurs des APIs Hackathon
app.include_router(assist_vocal,prefix="/assitante_vocal" , tags=["ASSITANTE VOCAL FOR SALMA"])
app.include_router(assist_physique,prefix="/assitante_physique" , tags=["ASSITANTE PHYSIQUE FOR MARWANE"])
app.include_router(feedback_text_generator,prefix="/feedback_text_generator", tags=["feedback_text_generator for AYMAN"])
# Lancer l'application FastAPI (le fichier principal)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
