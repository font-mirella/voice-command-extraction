# schema.py

from pydantic import BaseModel, field_validator
from typing import Optional
from enum import Enum


class Intent(str, Enum):
    AUMENTAR_PARAMETRO  = "aumentar_parametro"
    REDUZIR_PARAMETRO   = "reduzir_parametro"
    DEFINIR_PARAMETRO   = "definir_parametro"
    CONSULTAR_PARAMETRO = "consultar_parametro"
    DESCONHECIDO        = "desconhecido"


class Status(str, Enum):
    OK            = "ok"
    AMBIGUO       = "ambiguo"
    INCOMPLETO    = "incompleto"
    INVALIDO      = "invalido"
    FORA_DE_FAIXA = "fora_de_faixa"


class Confidence(str, Enum):
    HIGH = "high"
    LOW  = "low"


class ComandoMedico(BaseModel):
    intent:                Intent
    parameter:             Optional[str]   = None
    value:                 Optional[float] = None
    unit:                  Optional[str]   = None
    status:                Status
    confidence:            Confidence
    requires_confirmation: bool
    validation_errors:     list[str]
    normalized_transcript: str
    notes:                 Optional[str]   = None

    @field_validator("value")
    @classmethod
    def value_deve_ser_positivo(cls, v):
        if v is not None and v < 0:
            raise ValueError("value não pode ser negativo")
        return v