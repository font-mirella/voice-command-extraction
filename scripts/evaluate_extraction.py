# src/evaluate_extraction.py
"""
Avalia Variante A e Variante B contra o gabarito.
Calcula acurácia por campo, F1 por intent, taxa de schema válido
e taxa de erro crítico.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.answer import GABARITO_POR_ID

VARIANTE_A_PATH = "data/results/variante_a.json"
VARIANTE_B_PATH = "data/results/variante_b.json"
OUTPUT_PATH     = "data/results/evaluation.json"


def _campo_correto(saida: dict, esperado: dict, campo: str) -> bool:
    v_saida    = saida.get(campo)
    v_esperado = esperado.get(campo)
    if v_saida is None and v_esperado is None:
        return True
    if isinstance(v_esperado, float) and isinstance(v_saida, float):
        return abs(v_saida - v_esperado) < 0.01
    return str(v_saida).lower() == str(v_esperado).lower()


def _erro_critico(saida: dict, esperado: dict) -> bool:
    """
    Erro crítico = sistema disse 'ok' quando gabarito era fora_de_faixa,
    ou extraiu value/parameter errado em caso válido.
    """
    status_saida    = saida.get("status")
    status_esperado = esperado.get("status")

    # Sinalizou ok quando era fora_de_faixa
    if status_esperado == "fora_de_faixa" and status_saida == "ok":
        return True

    # Extraiu valor errado em caso que deveria ser ok
    if status_esperado == "ok":
        if not _campo_correto(saida, esperado, "value"):
            return True
        if not _campo_correto(saida, esperado, "parameter"):
            return True

    return False


def avaliar_variante(path: str, label: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    campos_avaliados = ["intent", "parameter", "value", "unit", "status",
                        "requires_confirmation", "confidence"]

    acertos_por_campo = {c: 0 for c in campos_avaliados}
    total_casos = 0
    erros_criticos = 0
    schema_invalidos = 0

    # Para F1 de intent
    intents_possiveis = [
        "aumentar_parametro", "reduzir_parametro",
        "definir_parametro", "consultar_parametro", "desconhecido"
    ]
    tp_intent = {i: 0 for i in intents_possiveis}
    fp_intent = {i: 0 for i in intents_possiveis}
    fn_intent = {i: 0 for i in intents_possiveis}

    detalhes = []

    for resultado in data["resultados"]:
        caso_id  = resultado["id"]
        gabarito = GABARITO_POR_ID.get(caso_id)

        if gabarito is None:
            continue

        # Variante B tem saida_final, Variante A tem saida
        saida = resultado.get("saida_final") or resultado.get("saida")

        if saida is None:
            schema_invalidos += 1
            total_casos += 1
            continue

        esperado = gabarito["esperado"]
        total_casos += 1

        acertos = {}
        for campo in campos_avaliados:
            correto = _campo_correto(saida, esperado, campo)
            acertos_por_campo[campo] += int(correto)
            acertos[campo] = correto

        # F1 de intent
        intent_pred = saida.get("intent")
        intent_true = esperado.get("intent")

        for intent in intents_possiveis:
            pred_pos = intent_pred == intent
            true_pos = intent_true == intent
            if pred_pos and true_pos:
                tp_intent[intent] += 1
            elif pred_pos and not true_pos:
                fp_intent[intent] += 1
            elif not pred_pos and true_pos:
                fn_intent[intent] += 1

        # Erro crítico
        ec = _erro_critico(saida, esperado)
        if ec:
            erros_criticos += 1

        detalhes.append({
            "id":        caso_id,
            "categoria": gabarito["categoria"],
            "acertos":   acertos,
            "erro_critico": ec,
        })

    # Acurácia por campo
    acuracia = {
        c: round(acertos_por_campo[c] / total_casos, 4)
        for c in campos_avaliados
    }
    acuracia_media = round(sum(acuracia.values()) / len(acuracia), 4)

    # F1 por intent
    f1_por_intent = {}
    for intent in intents_possiveis:
        tp = tp_intent[intent]
        fp = fp_intent[intent]
        fn = fn_intent[intent]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) > 0 else 0.0)
        f1_por_intent[intent] = {
            "precision": round(precision, 4),
            "recall":    round(recall, 4),
            "f1":        round(f1, 4),
        }

    f1_macro = round(
        sum(v["f1"] for v in f1_por_intent.values()) / len(f1_por_intent), 4
    )

    return {
        "variante":           label,
        "total_casos":        total_casos,
        "schema_invalidos":   schema_invalidos,
        "taxa_schema_valido": round(1 - schema_invalidos / total_casos, 4),
        "erros_criticos":     erros_criticos,
        "taxa_erro_critico":  round(erros_criticos / total_casos, 4),
        "acuracia_por_campo": acuracia,
        "acuracia_media":     acuracia_media,
        "f1_por_intent":      f1_por_intent,
        "f1_macro_intent":    f1_macro,
        "detalhes":           detalhes,
    }


def main():
    os.makedirs("data/results", exist_ok=True)

    print("Avaliando Variante A...")
    resultado_a = avaliar_variante(VARIANTE_A_PATH, "A — LLM puro")

    print("Avaliando Variante B...")
    resultado_b = avaliar_variante(VARIANTE_B_PATH, "B — LLM + regras")

    output = {
        "variante_a": resultado_a,
        "variante_b": resultado_b,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Imprime sumário comparativo
    print("\n" + "=" * 60)
    print(f"{'Métrica':<30} {'Var A':>10} {'Var B':>10}")
    print("=" * 60)

    metricas = [
        ("Taxa schema válido",   "taxa_schema_valido"),
        ("Taxa erro crítico",    "taxa_erro_critico"),
        ("Acurácia média",       "acuracia_media"),
        ("F1 macro intent",      "f1_macro_intent"),
    ]

    for label, chave in metricas:
        va = resultado_a[chave]
        vb = resultado_b[chave]
        print(f"{label:<30} {va:>10.4f} {vb:>10.4f}")

    print("\nAcurácia por campo:")
    for campo in resultado_a["acuracia_por_campo"]:
        va = resultado_a["acuracia_por_campo"][campo]
        vb = resultado_b["acuracia_por_campo"][campo]
        delta = vb - va
        sinal = "+" if delta >= 0 else ""
        print(f"  {campo:<28} {va:>6.2%}  {vb:>6.2%}  ({sinal}{delta:.2%})")

    print(f"\nResultados salvos em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()