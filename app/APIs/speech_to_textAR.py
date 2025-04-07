import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from io import BytesIO
import subprocess
from ..model import model

router = APIRouter()

temp_dir = "/temp"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
audio_path = os.path.join(temp_dir, "temp_audio.wav")

def transcribe_audio(audio_file: BytesIO):
    temp_input = os.path.join(temp_dir, "input_audio")
    with open(temp_input, "wb") as f:
        f.write(audio_file.read())

    subprocess.run(
        ["ffmpeg", "-i", temp_input, "-ar", "16000", "-ac", "1", "-threads", "4", audio_path, "-y", "-loglevel",
         "quiet"],
        check=True
    )

    segments, _ = model.transcribe(
        audio_path,
        language="ar",
        beam_size=5,
        initial_prompt="هذه جملة بالعربية.",
        word_timestamps=False
    )
    transcribed_text = " ".join([segment.text for segment in segments])

    # Vérifier si aucun texte n'a été extrait
    if not transcribed_text.strip():
        raise HTTPException(status_code=400, detail="لا يوجد نص تم اكتشافه في الصوت. يرجى التحقق من جودة الصوت أو محتواه.")

    os.remove(temp_input)
    os.remove(audio_path)

    return transcribed_text

@router.post("/")
async def transcribe_ar(file: UploadFile = File(...)):
    audio_file = BytesIO(await file.read())
    transcribed_text = transcribe_audio(audio_file)
    return {"language": "ar", "transcribed_text": transcribed_text}