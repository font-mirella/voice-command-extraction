# pipeline_a.py

"""
Variante A — LLM puro.
Lê transcrições do Whisper, extrai estrutura via LLM e salva resultados.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from extractor import extrair_comando

INPUT_PATH  = "data/transcripts/whisper_output.json"
OUTPUT_PATH = "data/results/variante_a.json"


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs("data/results", exist_ok=True)

    resultados = []
    erros = []

    print(f"Rodando Variante A em {len(data['resultados'])} casos...\n")

    for item in data["resultados"]:
        caso_id    = item["id"]
        categoria  = item["categoria"]
        transcript = item["transcricao_whisper"]

        try:
            saida = extrair_comando(transcript)
            saida_dict = saida.model_dump(mode="json")

            resultados.append({
                "id":        caso_id,
                "categoria": categoria,
                "fonte":     item["fonte"],
                "transcript_whisper": transcript,
                "saida":     saida_dict,
                "erro":      None,
            })

            status = saida_dict["status"]
            print(f"[{caso_id:02d}] ({categoria:<18}) status={status}")

        except Exception as e:
            erros.append(caso_id)
            print(f"[{caso_id:02d}] ERRO: {e}")
            resultados.append({
                "id":        caso_id,
                "categoria": categoria,
                "fonte":     item["fonte"],
                "transcript_whisper": transcript,
                "saida":     None,
                "erro":      str(e),
            })

        # pausa pequena para não estourar rate limit do Groq
        time.sleep(0.5)

    output = {
        "variante": "A",
        "descricao": "LLM puro — sem regras de domínio",
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