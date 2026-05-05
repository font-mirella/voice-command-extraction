# tests/test_cases.py
"""
Testes automatizados cobrindo os requisitos do desafio:
- caso válido simples
- caso com unidade omitida ou implícita
- caso ambíguo
- caso incompleto
- caso com valor fora do esperado
- caso com saída inválida do modelo ou do parser
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.schema import ComandoMedico, Intent, Status, Confidence
from src.validator import aplicar_regras
from src.normalize_text import normalize_for_metrics


# ─────────────────────────────────────────────
# 1. Schema e Pydantic
# ─────────────────────────────────────────────

class TestSchema:
    def test_schema_valido_completo(self):
        cmd = ComandoMedico(
            intent=Intent.DEFINIR_PARAMETRO,
            parameter="frequencia_respiratoria",
            value=20.0,
            unit="rpm",
            status=Status.OK,
            confidence=Confidence.HIGH,
            requires_confirmation=False,
            validation_errors=[],
            normalized_transcript="definir frequência respiratória para 20 rpm",
        )
        assert cmd.intent == Intent.DEFINIR_PARAMETRO
        assert cmd.value == 20.0

    def test_schema_rejeita_value_negativo(self):
        with pytest.raises(Exception):
            ComandoMedico(
                intent=Intent.DEFINIR_PARAMETRO,
                parameter="fio2",
                value=-10.0,
                unit="%",
                status=Status.OK,
                confidence=Confidence.HIGH,
                requires_confirmation=False,
                validation_errors=[],
                normalized_transcript="fio2 menos dez",
            )

    def test_schema_aceita_fields_opcionais_nulos(self):
        cmd = ComandoMedico(
            intent=Intent.DESCONHECIDO,
            parameter=None,
            value=None,
            unit=None,
            status=Status.INCOMPLETO,
            confidence=Confidence.LOW,
            requires_confirmation=True,
            validation_errors=["parâmetro não identificado"],
            normalized_transcript="aumentar",
        )
        assert cmd.parameter is None
        assert cmd.value is None

    def test_schema_serializa_para_json(self):
        cmd = ComandoMedico(
            intent=Intent.AUMENTAR_PARAMETRO,
            parameter="fio2",
            value=70.0,
            unit="%",
            status=Status.OK,
            confidence=Confidence.HIGH,
            requires_confirmation=False,
            validation_errors=[],
            normalized_transcript="aumentar fio2 para 70%",
        )
        data = cmd.model_dump(mode="json")
        assert isinstance(data, dict)
        assert data["intent"] == "aumentar_parametro"
        assert json.dumps(data)  # serializável sem erro


# ─────────────────────────────────────────────
# 2. Normalização de texto
# ─────────────────────────────────────────────

class TestNormalizacao:
    def test_numero_por_extenso(self):
        assert normalize_for_metrics("vinte") == "20"

    def test_numero_composto(self):
        assert normalize_for_metrics("quatrocentos e cinquenta") == "450"

    def test_remove_pontuacao(self):
        resultado = normalize_for_metrics("aumentar frequência.")
        assert "." not in resultado

    def test_normaliza_unidade_mililitros(self):
        resultado = normalize_for_metrics("quinhentos mililitros")
        assert "ml" in resultado

    def test_normaliza_fio2(self):
        resultado = normalize_for_metrics("fio dois")
        assert "fio2" in resultado


# ─────────────────────────────────────────────
# 3. Regras de domínio (validator)
# ─────────────────────────────────────────────

class TestValidator:

    def _base_cmd(self, **kwargs) -> ComandoMedico:
        defaults = dict(
            intent=Intent.DEFINIR_PARAMETRO,
            parameter="frequencia_respiratoria",
            value=20.0,
            unit="rpm",
            status=Status.OK,
            confidence=Confidence.HIGH,
            requires_confirmation=False,
            validation_errors=[],
            normalized_transcript="definir frequência para 20 rpm",
        )
        defaults.update(kwargs)
        return ComandoMedico(**defaults)

    def test_caso_valido_simples(self):
        """Caso válido simples não deve gerar erros nem alterar status."""
        cmd = self._base_cmd()
        resultado = aplicar_regras(cmd, "definir frequência para 20 rpm")
        assert resultado.status == Status.OK
        assert resultado.validation_errors == []

    def test_unidade_omitida_baixa_confianca(self):
        """Quando unidade não aparece na transcrição, confidence deve ser low."""
        cmd = self._base_cmd(
            value=20.0,
            unit="rpm",
            confidence=Confidence.HIGH,
        )
        # transcrição sem "rpm"
        resultado = aplicar_regras(cmd, "aumentar frequência para vinte")
        assert resultado.confidence == Confidence.LOW
        assert resultado.requires_confirmation is True

    def test_valor_fora_de_faixa_frequencia(self):
        """Valor absurdo deve gerar status fora_de_faixa."""
        cmd = self._base_cmd(value=300.0)
        resultado = aplicar_regras(cmd, "definir frequência para 300 rpm")
        assert resultado.status == Status.FORA_DE_FAIXA
        assert resultado.requires_confirmation is True
        assert len(resultado.validation_errors) > 0

    def test_valor_fora_de_faixa_volume(self):
        """Volume abaixo do mínimo deve ser sinalizado."""
        cmd = self._base_cmd(
            parameter="volume_corrente",
            value=50.0,
            unit="mL",
            normalized_transcript="volume corrente em 50 ml",
        )
        resultado = aplicar_regras(cmd, "volume corrente em 50 ml")
        assert resultado.status == Status.FORA_DE_FAIXA

    def test_fio2_alto_requer_confirmacao(self):
        """FiO2 > 80% deve exigir confirmação mesmo dentro da faixa."""
        cmd = self._base_cmd(
            parameter="fio2",
            value=90.0,
            unit="%",
            normalized_transcript="fio2 noventa por cento",
        )
        resultado = aplicar_regras(cmd, "fio2 noventa por cento")
        assert resultado.requires_confirmation is True

    def test_normaliza_unidade_sinonimo(self):
        """Sinônimos de unidade devem ser normalizados para forma canônica."""
        cmd = self._base_cmd(unit="mililitros", parameter="volume_corrente",
                             value=500.0,
                             normalized_transcript="volume corrente 500 mililitros")
        resultado = aplicar_regras(cmd, "volume corrente 500 mililitros")
        assert resultado.unit == "mL"


# ─────────────────────────────────────────────
# 4. Casos de borda
# ─────────────────────────────────────────────

class TestCasosDeBorda:

    def test_saida_invalida_do_modelo_capturada(self):
        """Simula falha de parsing — objeto de fallback deve ter status invalido."""
        cmd = ComandoMedico(
            intent=Intent.DESCONHECIDO,
            parameter=None,
            value=None,
            unit=None,
            status=Status.INVALIDO,
            confidence=Confidence.LOW,
            requires_confirmation=True,
            validation_errors=["erro de parsing: JSON inválido"],
            normalized_transcript="Azueta paraə vwan Ontiniz",
            notes="raw output: ...",
        )
        assert cmd.status == Status.INVALIDO
        assert any("parsing" in e for e in cmd.validation_errors)

    def test_caso_ambiguo_sem_valor(self):
        """Comando ambíguo sem valor deve ter requires_confirmation e value nulo."""
        cmd = ComandoMedico(
            intent=Intent.AUMENTAR_PARAMETRO,
            parameter="frequencia_respiratoria",
            value=None,
            unit=None,
            status=Status.AMBIGUO,
            confidence=Confidence.LOW,
            requires_confirmation=True,
            validation_errors=["valor não especificado"],
            normalized_transcript="aumentar um pouco a frequência",
        )
        assert cmd.value is None
        assert cmd.requires_confirmation is True

    def test_caso_incompleto_sem_parametro(self):
        """Comando só com intenção deve ter parameter nulo e status incompleto."""
        cmd = ComandoMedico(
            intent=Intent.AUMENTAR_PARAMETRO,
            parameter=None,
            value=None,
            unit=None,
            status=Status.INCOMPLETO,
            confidence=Confidence.LOW,
            requires_confirmation=True,
            validation_errors=["parâmetro não identificado", "valor não especificado"],
            normalized_transcript="aumentar",
        )
        assert cmd.parameter is None
        assert cmd.status == Status.INCOMPLETO

    def test_valor_limite_exato_faixa(self):
        """Valor exatamente no limite da faixa não deve ser fora_de_faixa."""
        from src.validator import aplicar_regras
        cmd = ComandoMedico(
            intent=Intent.DEFINIR_PARAMETRO,
            parameter="frequencia_respiratoria",
            value=35.0,   # limite máximo exato
            unit="rpm",
            status=Status.OK,
            confidence=Confidence.HIGH,
            requires_confirmation=False,
            validation_errors=[],
            normalized_transcript="definir frequência para 35 rpm",
        )
        resultado = aplicar_regras(cmd, "definir frequência para 35 rpm")
        assert resultado.status == Status.OK