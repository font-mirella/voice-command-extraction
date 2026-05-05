# validator.py
"""
Camada híbrida da Variante B.
Aplica regras de domínio sobre a saída do LLM.
"""

from schema import ComandoMedico, Status, Confidence

PARAMETROS = {
    "frequencia_respiratoria": {
        "unidade_canonica": "rpm",
        "faixa": (8, 35),
        "requer_confirmacao_se": lambda v: v > 25 or v < 10,
    },
    "volume_corrente": {
        "unidade_canonica": "mL",
        "faixa": (300, 800),
        "requer_confirmacao_se": lambda v: abs(v - 500) / 500 > 0.2,
    },
    "pressao_inspiratoria": {
        "unidade_canonica": "cmH2O",
        "faixa": (5, 40),
        "requer_confirmacao_se": lambda v: v > 30,
    },
    "fio2": {
        "unidade_canonica": "%",
        "faixa": (21, 100),
        "requer_confirmacao_se": lambda v: v > 80,
    },
}

# Unidades que o LLM pode devolver e que mapeiam para a canônica
UNIDADES_SINONIMOS = {
    "rpm": "rpm", "irpm": "rpm", "rpm.": "rpm",
    "ml": "mL", "ml.": "mL", "mililitros": "mL", "mililitro": "mL",
    "cmh2o": "cmH2O", "cm h2o": "cmH2O", "centímetros de água": "cmH2O",
    "centimetros de agua": "cmH2O", "cm": "cmH2O",
    "%": "%", "por cento": "%", "porcento": "%",
}


def _normalizar_unidade(unit: str | None) -> str | None:
    if unit is None:
        return None
    return UNIDADES_SINONIMOS.get(unit.lower().strip(), unit)


def _unidade_foi_inferida(transcript: str, unit: str | None) -> bool:
    """
    Verifica se a unidade canônica aparece explicitamente na transcrição.
    Se não aparecer, foi inferida pelo LLM — incerteza maior.
    """
    if unit is None:
        return False
    transcript_lower = transcript.lower()
    sinonimos_da_unidade = [
        k for k, v in UNIDADES_SINONIMOS.items() if v == unit
    ]
    return not any(s in transcript_lower for s in sinonimos_da_unidade)


def aplicar_regras(comando: ComandoMedico, transcript_original: str) -> ComandoMedico:
    """
    Recebe saída do LLM e aplica regras determinísticas de domínio.
    Retorna novo ComandoMedico corrigido.
    """
    dados = comando.model_dump(mode="json")
    erros = list(dados["validation_errors"])

    parametro = dados.get("parameter")
    value     = dados.get("value")
    unit      = dados.get("unit")

    # 1. Normalizar unidade para forma canônica
    unit_normalizada = _normalizar_unidade(unit)
    dados["unit"] = unit_normalizada

    # 2. Se unidade foi inferida (não dita explicitamente), baixar confiança
    if parametro and unit_normalizada:
        if _unidade_foi_inferida(transcript_original, unit_normalizada):
            dados["confidence"] = "low"
            dados["requires_confirmation"] = True

    # 3. Validar faixa clínica se tiver parâmetro e valor
    if parametro and value is not None and parametro in PARAMETROS:
        regras = PARAMETROS[parametro]
        minimo, maximo = regras["faixa"]

        if value < minimo or value > maximo:
            dados["status"] = "fora_de_faixa"
            dados["requires_confirmation"] = True
            msg = f"valor {value} fora da faixa permitida ({minimo}–{maximo} {regras['unidade_canonica']})"
            if msg not in erros:
                erros.append(msg)
        elif regras["requer_confirmacao_se"](value):
            dados["requires_confirmation"] = True

    # 4. Se status ainda é ok mas há validation_errors, promove para ambiguo
    if dados["status"] == "ok" and erros:
        dados["status"] = "ambiguo"

    dados["validation_errors"] = erros
    return ComandoMedico(**dados)