import whisper

model = whisper.load_model("base")

def transcribe_audio(audio_path: str) -> dict:
    result = model.transcribe(audio_path, language="pt")
    return {
        "text": result["text"].strip(),
        "language": result["language"],
        "segments": result["segments"],
    }

if __name__ == "__main__": # check
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/audio/1.m4a"
    out = transcribe_audio(path)
    print("Texto:", out["text"])
    print("Idioma:", out["language"])