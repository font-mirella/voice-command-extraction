# src/extractor.py

import json
from groq import Groq
from schema import ComandoMedico

client = Groq()  # lê GROQ_API_KEY do ambiente automaticamente

SYSTEM_PROMPT = """Você é um sistema de extração estruturada de comandos médicos em português brasileiro.

Seu trabalho é analisar transcrições de comandos de voz curtos e extrair informações estruturadas.

O domínio é restrito a equipamentos médicos com os seguintes parâmetros:
- frequencia_respiratoria (unidade canônica: rpm, faixa normal: 8–35)
- volume_corrente (unidade canônica: mL, faixa normal: 300–800)
- pressao_inspiratoria (unidade canônica: cmH2O, faixa normal: 5–40)
- fio2 (unidade canônica: %, faixa normal: 21–100)

Regras de extração:
- intent deve ser um de: aumentar_parametro, reduzir_parametro, definir_parametro, consultar_parametro, desconhecido
- parameter deve ser o nome canônico do parâmetro ou null se não identificado
- value deve ser numérico ou null se não especificado
- unit deve ser a unidade canônica ou null se não identificada
- status deve ser: ok, ambiguo, incompleto, invalido ou fora_de_faixa
- confidence deve ser high ou low
- requires_confirmation deve ser true se houver ambiguidade, valor alto ou unidade inferida
- validation_errors deve listar problemas encontrados (lista vazia se nenhum)
- normalized_transcript deve ser a transcrição limpa que você recebeu

Responda APENAS com JSON válido, sem texto adicional, sem markdown, sem explicações."""

USER_PROMPT_TEMPLATE = """Transcrição do comando de voz:
\"{transcript}\"

Extraia as informações estruturadas seguindo exatamente o schema definido."""


def extrair_comando(transcript: str) -> ComandoMedico:
    """
    Variante A — LLM puro.
    Recebe transcrição e devolve ComandoMedico validado pelo Pydantic.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": USER_PROMPT_TEMPLATE.format(transcript=transcript)},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)
        return ComandoMedico(**data)
    except Exception as e:
        return ComandoMedico(
            intent="desconhecido",
            parameter=None,
            value=None,
            unit=None,
            status="invalido",
            confidence="low",
            requires_confirmation=True,
            validation_errors=[f"erro de parsing: {str(e)}"],
            normalized_transcript=transcript,
            notes=f"raw output: {raw[:200]}",
        )


if __name__ == "__main__":
    transcript = "Aumentar frequência respiratória para vinte rpm"
    resultado = extrair_comando(transcript)
    print(resultado.model_dump_json(indent=2))