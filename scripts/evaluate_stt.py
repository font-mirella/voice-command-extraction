# evaluate_stt.py

import json
import os

from metrics import calcular_wer, calcular_cer
from normalize_text import normalize_for_metrics


INPUT_PATH = "data/transcripts/whisper_output.json"
OUTPUT_PATH = "data/transcripts/stt_evaluation.json"


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    resultados_avaliados = []

    wer_raw_total = []
    cer_raw_total = []
    wer_norm_total = []
    cer_norm_total = []

    for item in data["resultados"]:
        referencia = item["referencia"]
        transcricao = item["transcricao_whisper"]

        ref_norm = normalize_for_metrics(referencia)
        hyp_norm = normalize_for_metrics(transcricao)

        wer_raw = calcular_wer(referencia, transcricao)
        cer_raw = calcular_cer(referencia, transcricao)

        wer_norm = calcular_wer(ref_norm, hyp_norm)
        cer_norm = calcular_cer(ref_norm, hyp_norm)

        wer_raw_total.append(wer_raw)
        cer_raw_total.append(cer_raw)
        wer_norm_total.append(wer_norm)
        cer_norm_total.append(cer_norm)

        resultados_avaliados.append({
            **item,
            "referencia_normalizada": ref_norm,
            "transcricao_normalizada": hyp_norm,
            "wer_raw": wer_raw,
            "cer_raw": cer_raw,
            "wer_normalizado": wer_norm,
            "cer_normalizado": cer_norm,
        })

    output = {
        "modelo": data.get("modelo", "whisper-base"),
        "idioma": data.get("idioma", "pt"),
        "total_casos": len(resultados_avaliados),
        "falhas_tecnicas": data.get("falhas", []),
        "metricas": {
            "wer_raw_medio": round(sum(wer_raw_total) / len(wer_raw_total), 4),
            "cer_raw_medio": round(sum(cer_raw_total) / len(cer_raw_total), 4),
            "wer_normalizado_medio": round(sum(wer_norm_total) / len(wer_norm_total), 4),
            "cer_normalizado_medio": round(sum(cer_norm_total) / len(cer_norm_total), 4),
        },
        "resultados": resultados_avaliados,
    }

    os.makedirs("data/transcripts", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("Avaliação STT concluída.")
    print(json.dumps(output["metricas"], ensure_ascii=False, indent=2))
    print(f"Resultado salvo em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()