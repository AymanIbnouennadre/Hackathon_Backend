from faster_whisper import WhisperModel

# Charger le modèle une fois, avec optimisation pour CPU
model = WhisperModel(
    "large",
    device="cpu",
    compute_type="int8",  # Quantification pour accélérer sur CPU soit int8 (khfifa) soit float16(tqila mais résultat hssn ) ou float32(par defaut)
    cpu_threads=8  # Utilise tous les cœurs de ton i7-11th (4 cœurs)
)