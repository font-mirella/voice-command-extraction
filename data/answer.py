# answer.py
"""
Gabarito dos 25 casos de teste.
Define o output esperado para cada comando após processamento completo.
Usado para avaliação da Variante A (LLM puro) e Variante B (híbrida).
"""

GABARITO = [
    # -------------------------
    # VÁLIDOS SIMPLES (1–6)
    # -------------------------
    {
        "id": 1,
        "categoria": "valido_simples",
        "referencia": "aumentar frequência respiratória para vinte rpm",
        "esperado": {
            "intent": "aumentar_parametro",
            "parameter": "frequencia_respiratoria",
            "value": 20.0,
            "unit": "rpm",
            "status": "ok",
            "confidence": "high",
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },
    {
        "id": 2,
        "categoria": "valido_simples",
        "referencia": "definir volume corrente em quinhentos mililitros",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "volume_corrente",
            "value": 500.0,
            "unit": "mL",
            "status": "ok",
            "confidence": "high",
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },
    {
        "id": 3,
        "categoria": "valido_simples",
        "referencia": "reduzir pressão inspiratória para quinze centímetros de água",
        "esperado": {
            "intent": "reduzir_parametro",
            "parameter": "pressao_inspiratoria",
            "value": 15.0,
            "unit": "cmH2O",
            "status": "ok",
            "confidence": "high",
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },
    {
        "id": 4,
        "categoria": "valido_simples",
        "referencia": "aumentar fio dois para sessenta por cento",
        "esperado": {
            "intent": "aumentar_parametro",
            "parameter": "fio2",
            "value": 60.0,
            "unit": "%",
            "status": "ok",
            "confidence": "high",
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },
    {
        "id": 5,
        "categoria": "valido_simples",
        "referencia": "diminuir frequência para doze rpm",
        "esperado": {
            "intent": "reduzir_parametro",
            "parameter": "frequencia_respiratoria",
            "value": 12.0,
            "unit": "rpm",
            "status": "ok",
            "confidence": "high",
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },
    {
        "id": 6,
        "categoria": "valido_simples",
        "referencia": "ajustar volume corrente para quatrocentos e cinquenta mililitros",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "volume_corrente",
            "value": 450.0,
            "unit": "mL",
            "status": "ok",
            "confidence": "high",
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },

    # -------------------------
    # UNIDADE OMITIDA (7–10)
    # -------------------------
    {
        "id": 7,
        "categoria": "unidade_omitida",
        "referencia": "aumentar frequência para vinte",
        "esperado": {
            "intent": "aumentar_parametro",
            "parameter": "frequencia_respiratoria",
            "value": 20.0,
            "unit": "rpm",           # inferida pelo parâmetro
            "status": "ok",
            "confidence": "low",     # unidade não foi dita explicitamente
            "requires_confirmation": True,
            "validation_errors": [],
        },
    },
    {
        "id": 8,
        "categoria": "unidade_omitida",
        "referencia": "definir fio dois em oitenta",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "fio2",
            "value": 80.0,
            "unit": "%",             # inferida pelo parâmetro
            "status": "ok",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": [],
        },
    },
    {
        "id": 9,
        "categoria": "unidade_omitida",
        "referencia": "volume corrente quinhentos",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "volume_corrente",
            "value": 500.0,
            "unit": "mL",            # inferida pelo parâmetro
            "status": "ok",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": [],
        },
    },
    {
        "id": 10,
        "categoria": "unidade_omitida",
        "referencia": "pressão trinta",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "pressao_inspiratoria",  # inferência — única pressão no domínio
            "value": 30.0,
            "unit": "cmH2O",
            "status": "ok",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": [],
        },
    },

    # -------------------------
    # AMBÍGUOS (11–14)
    # -------------------------
    {
        "id": 11,
        "categoria": "ambiguo",
        "referencia": "aumentar um pouco a frequência",
        "esperado": {
            "intent": "aumentar_parametro",
            "parameter": "frequencia_respiratoria",
            "value": None,           # valor não especificado
            "unit": None,
            "status": "ambiguo",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": ["valor não especificado"],
        },
    },
    {
        "id": 12,
        "categoria": "ambiguo",
        "referencia": "diminuir pressão",
        "esperado": {
            "intent": "reduzir_parametro",
            "parameter": "pressao_inspiratoria",
            "value": None,
            "unit": None,
            "status": "ambiguo",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": ["valor não especificado"],
        },
    },
    {
        "id": 13,
        "categoria": "ambiguo",
        "referencia": "fio dois tá baixo",
        "esperado": {
            "intent": "aumentar_parametro",  # "tá baixo" implica intenção de aumentar
            "parameter": "fio2",
            "value": None,
            "unit": None,
            "status": "ambiguo",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": ["valor não especificado"],
        },
    },
    {
        "id": 14,
        "categoria": "ambiguo",
        "referencia": "ajustar para vinte",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": None,       # parâmetro não especificado
            "value": 20.0,
            "unit": None,
            "status": "ambiguo",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": ["parâmetro não identificado"],
        },
    },

    # -------------------------
    # INCOMPLETOS (15–17)
    # -------------------------
    {
        "id": 15,
        "categoria": "incompleto",
        "referencia": "frequência",
        "esperado": {
            "intent": "desconhecido",
            "parameter": "frequencia_respiratoria",
            "value": None,
            "unit": None,
            "status": "incompleto",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": ["intenção não identificada", "valor não especificado"],
        },
    },
    {
        "id": 16,
        "categoria": "incompleto",
        "referencia": "aumentar",
        "esperado": {
            "intent": "aumentar_parametro",
            "parameter": None,
            "value": None,
            "unit": None,
            "status": "incompleto",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": ["parâmetro não identificado", "valor não especificado"],
        },
    },
    {
        "id": 17,
        "categoria": "incompleto",
        "referencia": "definir pressão inspiratória",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "pressao_inspiratoria",
            "value": None,
            "unit": None,
            "status": "incompleto",
            "confidence": "low",
            "requires_confirmation": True,
            "validation_errors": ["valor não especificado"],
        },
    },

    # -------------------------
    # FORA DE FAIXA (18–21)
    # -------------------------
    {
        "id": 18,
        "categoria": "fora_de_faixa",
        "referencia": "definir frequência respiratória para trezentos rpm",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "frequencia_respiratoria",
            "value": 300.0,          # extraído corretamente — fora da faixa 8–35
            "unit": "rpm",
            "status": "fora_de_faixa",
            "confidence": "high",    # extração foi clara, o problema é o valor
            "requires_confirmation": True,
            "validation_errors": ["valor 300 fora da faixa permitida (8–35 rpm)"],
        },
    },
    {
        "id": 19,
        "categoria": "fora_de_faixa",
        "referencia": "fio dois cem por cento",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "fio2",
            "value": 100.0,          # limítrofe superior — tecnicamente válido mas requer confirmação
            "unit": "%",
            "status": "ok",          # 100% está dentro da faixa 21–100
            "confidence": "high",
            "requires_confirmation": True,  # regra: valor > 80 requer confirmação
            "validation_errors": [],
        },
    },
    {
        "id": 20,
        "categoria": "fora_de_faixa",
        "referencia": "volume corrente em cinquenta mililitros",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "volume_corrente",
            "value": 50.0,           # abaixo do mínimo (300 mL)
            "unit": "mL",
            "status": "fora_de_faixa",
            "confidence": "high",
            "requires_confirmation": True,
            "validation_errors": ["valor 50 fora da faixa permitida (300–800 mL)"],
        },
    },
    {
        "id": 21,
        "categoria": "fora_de_faixa",
        "referencia": "pressão inspiratória cinquenta centímetros de água",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "pressao_inspiratoria",
            "value": 50.0,           # acima do máximo (40 cmH2O)
            "unit": "cmH2O",
            "status": "fora_de_faixa",
            "confidence": "high",
            "requires_confirmation": True,
            "validation_errors": ["valor 50 fora da faixa permitida (5–40 cmH2O)"],
        },
    },

    # -------------------------
    # ERRO DE STT (22–25)
    # -------------------------
    {
        "id": 22,
        "categoria": "erro_stt",
        "referencia": "aumentar efí ó dois para setenta",
        "esperado": {
            "intent": "aumentar_parametro",
            "parameter": "fio2",     # "efí ó dois" deve ser mapeado para fio2
            "value": 70.0,
            "unit": "%",
            "status": "ok",
            "confidence": "low",     # transcrição de sigla fonética é incerta
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },
    {
        "id": 23,
        "categoria": "erro_stt",
        "referencia": "frequência respiratória vinte i rpm",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "frequencia_respiratoria",
            "value": 20.0,
            "unit": "rpm",
            "status": "ok",
            "confidence": "low",
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },
    {
        "id": 24,
        "categoria": "erro_stt",
        "referencia": "volume corente quatrocentos",  # erro ortográfico proposital
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "volume_corrente",
            "value": 400.0,
            "unit": "mL",
            "status": "ok",
            "confidence": "low",
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },
    {
        "id": 25,
        "categoria": "erro_stt",
        "referencia": "definir pressão em quinze centímetros d'água",
        "esperado": {
            "intent": "definir_parametro",
            "parameter": "pressao_inspiratoria",
            "value": 15.0,
            "unit": "cmH2O",
            "status": "ok",
            "confidence": "low",
            "requires_confirmation": False,
            "validation_errors": [],
        },
    },
]

# Index por id para acesso rápido
GABARITO_POR_ID = {caso["id"]: caso for caso in GABARITO}