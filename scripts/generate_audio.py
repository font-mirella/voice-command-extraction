print("SCRIPT COMEÇOU")

from gtts import gTTS
import json
import os

# Os 25 comandos definidos no catálogo
CASOS = [
    # Válidos simples
    {"id": 5, "texto": "diminuir frequência para doze rpm", "categoria": "valido_simples"},
    {"id": 6, "texto": "ajustar volume corrente para quatrocentos e cinquenta mililitros", "categoria": "valido_simples"},

    # Unidade omitida ou implícita
    {"id": 8, "texto": "definir fio dois em oitenta", "categoria": "unidade_omitida"},
    {"id": 9, "texto": "volume corrente quinhentos", "categoria": "unidade_omitida"},
    {"id": 10, "texto": "pressão trinta", "categoria": "unidade_omitida"},

    # Ambíguos
    {"id": 11, "texto": "aumentar um pouco a frequência", "categoria": "ambiguo"},
    {"id": 12, "texto": "diminuir pressão", "categoria": "ambiguo"},

    # Incompletos
    {"id": 16, "texto": "aumentar", "categoria": "incompleto"},
    {"id": 17, "texto": "definir pressão inspiratória", "categoria": "incompleto"},

    # Fora de faixa
    {"id": 19, "texto": "fio dois cem por cento", "categoria": "fora_de_faixa"},
    {"id": 20, "texto": "volume corrente em cinquenta mililitros", "categoria": "fora_de_faixa"},

    # Erros simulados de STT (você gera o áudio com o texto correto,
    # mas documenta que o Whisper vai transcrever diferente)
    {"id": 22, "texto": "aumentar efí ó dois para setenta", "categoria": "erro_stt"},
    {"id": 23, "texto": "frequência respiratória vinte i rpm", "categoria": "erro_stt"},
    {"id": 24, "texto": "volume corente quatrocentos", "categoria": "erro_stt"},
    {"id": 25, "texto": "definir pressão em quinze centímetros d'água", "categoria": "erro_stt"},
]

def gerar_audios(output_dir: str = "data/audio"):
    os.makedirs(output_dir, exist_ok=True)

    for caso in CASOS:
        filename = f"cmd_{caso['id']:02d}.mp3"
        filepath = os.path.join(output_dir, filename)

        tts = gTTS(text=caso["texto"], lang="pt", tld="com.br")
        tts.save(filepath)
        print(f"[{caso['id']:02d}] gerado: {filename}")

    # Salva o catálogo como referência
    catalog_path = "data/transcripts/reference.json"
    os.makedirs("data/transcripts", exist_ok=True)
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(CASOS, f, ensure_ascii=False, indent=2)

    print(f"\nCatálogo salvo em {catalog_path}")

if __name__ == "__main__":
    gerar_audios()