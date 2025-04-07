from fastapi import APIRouter, UploadFile, File
import requests
from PIL import Image
import io

# ✅ Initialisation du routeur pour l'API française
router = APIRouter()

# ✅ Clé API OCR.space
OCR_API_KEY = "K81378610988957"

# ✅ URL de base de l'API OCR.space
OCR_API_URL = "https://api.ocr.space/parse/image"

# ✅ Fonction de compression d'image
def compress_image(img_bytes, max_size=1024 * 1024):  # 1 Mo en octets
    img = Image.open(io.BytesIO(img_bytes))
    img_format = img.format or "JPEG"  # Utiliser JPEG par défaut si le format n'est pas détecté

    # Réduire la qualité initialement à 75%
    output = io.BytesIO()
    img.save(output, format=img_format, quality=75, optimize=True)
    compressed_bytes = output.getvalue()

    # Si l'image dépasse encore 1 Mo, réduire la résolution
    while len(compressed_bytes) > max_size:
        # Réduire la taille de l'image (par exemple, diviser les dimensions par 1.5)
        new_width = int(img.width / 1.5)
        new_height = int(img.height / 1.5)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img_resized.save(output, format=img_format, quality=75, optimize=True)
        compressed_bytes = output.getvalue()
        img = img_resized  # Mettre à jour l'image pour la prochaine itération si nécessaire

    return compressed_bytes

# ✅ Route OCR en français
@router.post("/")
async def convert_image_to_text_fr(file: UploadFile = File(...)):
    try:
        # Lire l'image envoyée par l'utilisateur
        img_bytes = await file.read()

        # Compresser l'image pour respecter la limite de 1 Mo
        compressed_img_bytes = compress_image(img_bytes)

        # Préparer les données pour la requête
        files = {"file": (file.filename, compressed_img_bytes, file.content_type)}
        headers = {
            "apikey": OCR_API_KEY,  # Clé API envoyée dans l'en-tête
        }
        params = {
            "language": "fre",  # Langue française
            "isOverlayRequired": "false",
            "scale": "true",
            "OCREngine": "2"  # Utiliser le moteur OCR 2 pour une meilleure précision
        }

        # Envoyer la requête à OCR.space
        response = requests.post(OCR_API_URL, files=files, data=params, headers=headers)
        response.raise_for_status()  # Vérifier si la requête a réussi

        # Parser la réponse JSON
        result = response.json()
        if result.get("IsErroredOnProcessing", True):
            return {"error": result.get("ErrorMessage", "Erreur inconnue")}

        # Extraire le texte
        extracted_text = result["ParsedResults"][0]["ParsedText"].strip()
        return {"extracted_text": extracted_text}

    except Exception as e:
        return {"error": str(e)}
