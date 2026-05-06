# pipeline_b.py

"""
Variante B — LLM + regras de domínio (abordagem híbrida).
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))



from extractor import extrair_comando
from validator import aplicar_regras

INPUT_PATH  = "data/transcripts/whisper_output.json"
OUTPUT_PATH = "data/results/variante_b.json"


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs("data/results", exist_ok=True)

    resultados = []
    erros = []

    print(f"Rodando Variante B em {len(data['resultados'])} casos...\n")

    for item in data["resultados"]:
        caso_id    = item["id"]
        categoria  = item["categoria"]
        transcript = item["transcricao_whisper"]

        try:
            # Passo 1 — LLM extrai
            saida_llm = extrair_comando(transcript)

            # Passo 2 — regras de domínio corrigem
            saida_final = aplicar_regras(saida_llm, transcript)
            saida_dict  = saida_final.model_dump(mode="json")

            resultados.append({
                "id":        caso_id,
                "categoria": categoria,
                "fonte":     item["fonte"],
                "transcript_whisper": transcript,
                "saida_llm":   saida_llm.model_dump(mode="json"),
                "saida_final": saida_dict,
                "erro": None,
            })

            status = saida_dict["status"]
            conf   = saida_dict["confidence"]
            print(f"[{caso_id:02d}] ({categoria:<18}) status={status} confidence={conf}")

        except Exception as e:
            erros.append(caso_id)
            print(f"[{caso_id:02d}] ERRO: {e}")
            resultados.append({
                "id":        caso_id,
                "categoria": categoria,
                "fonte":     item["fonte"],
                "transcript_whisper": transcript,
                "saida_llm":   None,
                "saida_final": None,
                "erro": str(e),
            })

        time.sleep(0.5)

    output = {
        "variante": "B",
        "descricao": "LLM + regras de domínio (híbrida)",
        "modelo": "llama-3.3-70b-versatile",
        "total_casos": len(resultados),
        "erros_criticos": erros,
        "resultados": resultados,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nConcluído. Erros críticos: {erros if erros else 'nenhum'}")
    print(f"Resultados salvos em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()