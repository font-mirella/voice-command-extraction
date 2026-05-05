# transcribe_all.py

"""
Transcreve todos os áudios de data/audio/ usando Whisper
e salva os resultados em data/transcripts/whisper_output.json
"""

import whisper
import json
import os


CASOS_REFERENCIA = {
    1:  "aumentar frequência respiratória para vinte rpm",
    2:  "definir volume corrente em quinhentos mililitros",
    3:  "reduzir pressão inspiratória para quinze centímetros de água",
    4:  "aumentar fio dois para sessenta por cento",
    5:  "diminuir frequência para doze rpm",
    6:  "ajustar volume corrente para quatrocentos e cinquenta mililitros",
    7:  "aumentar frequência para vinte",
    8:  "definir fio dois em oitenta",
    9:  "volume corrente quinhentos",
    10: "pressão trinta",
    11: "aumentar um pouco a frequência",
    12: "diminuir pressão",
    13: "fio dois tá baixo",
    14: "ajustar para vinte",
    15: "frequência",
    16: "aumentar",
    17: "definir pressão inspiratória",
    18: "definir frequência respiratória para trezentos rpm",
    19: "fio dois cem por cento",
    20: "volume corrente em cinquenta mililitros",
    21: "pressão inspiratória cinquenta centímetros de água",
    22: "aumentar efí ó dois para setenta",
    23: "frequência respiratória vinte i rpm",
    24: "volume corente quatrocentos",
    25: "definir pressão em quinze centímetros d'água",
}


CATEGORIAS = {
    1:  "valido_simples",
    2:  "valido_simples",
    3:  "valido_simples",
    4:  "valido_simples",
    5:  "valido_simples",
    6:  "valido_simples",
    7:  "unidade_omitida",
    8:  "unidade_omitida",
    9:  "unidade_omitida",
    10: "unidade_omitida",
    11: "ambiguo",
    12: "ambiguo",
    13: "ambiguo",
    14: "ambiguo",
    15: "incompleto",
    16: "incompleto",
    17: "incompleto",
    18: "fora_de_faixa",
    19: "fora_de_faixa",
    20: "fora_de_faixa",
    21: "fora_de_faixa",
    22: "erro_stt",
    23: "erro_stt",
    24: "erro_stt",
    25: "erro_stt",
}


FONTE = {
    1:  "voz_humana",
    2:  "voz_humana",
    3:  "voz_humana",
    4:  "voz_humana",
    7:  "voz_humana",
    13: "voz_humana",
    14: "voz_humana",
    15: "voz_humana",
    18: "voz_humana",
    21: "voz_humana",
}


def encontrar_audio(audio_dir: str, caso_id: int) -> str | None:
    """Procura o arquivo de áudio pelo id, aceitando .m4a e .mp3."""
    for ext in [".m4a", ".mp3", ".wav"]:
        path = os.path.join(audio_dir, f"{caso_id}{ext}")
        if os.path.exists(path):
            return path

        path = os.path.join(audio_dir, f"cmd_{caso_id:02d}{ext}")
        if os.path.exists(path):
            return path

    return None


def main():
    audio_dir = "data/audio"
    output_path = "data/transcripts/whisper_output.json"
    os.makedirs("data/transcripts", exist_ok=True)

    print("Carregando modelo Whisper (base)...")
    model = whisper.load_model("base")
    print("Modelo carregado.\n")

    resultados = []
    falhas = []

    for caso_id in range(1, 26):
        audio_path = encontrar_audio(audio_dir, caso_id)

        if audio_path is None:
            print(f"[{caso_id:02d}] AVISO: áudio não encontrado, pulando.")
            falhas.append(caso_id)
            continue

        referencia = CASOS_REFERENCIA[caso_id]
        categoria = CATEGORIAS[caso_id]
        fonte = FONTE.get(caso_id, "gtts")

        try:
            result = model.transcribe(audio_path, language="pt")
            transcricao = result["text"].strip()

            entrada = {
                "id": caso_id,
                "categoria": categoria,
                "fonte": fonte,
                "audio": audio_path,
                "referencia": referencia,
                "transcricao_whisper": transcricao,
            }

            resultados.append(entrada)

            print(f"[{caso_id:02d}] ({categoria:<18}) transcrito")
            print(f"       REF: {referencia}")
            print(f"       HYP: {transcricao}")
            print()

        except Exception as e:
            print(f"[{caso_id:02d}] ERRO ao transcrever: {e}")
            falhas.append(caso_id)

    output = {
        "modelo": "whisper-base",
        "idioma": "pt",
        "total_casos": len(resultados),
        "falhas": falhas,
        "resultados": resultados,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"Transcritos: {len(resultados)} casos")
    print(f"Falhas técnicas: {falhas if falhas else 'nenhuma'}")
    print(f"Resultados salvos em: {output_path}")


if __name__ == "__main__":
    main()