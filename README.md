# Voice Command Extraction — STT + Extração Estruturada de Comandos Médicos

O projeto investiga um pipeline para receber **comandos de voz curtos em português brasileiro**, transcrevê-los com **Whisper** e convertê-los em uma saída **JSON estruturada e validável**. O foco do seguinte projeto é prototipagem experimental, avaliação e documentação.

> **Nota de escopo:** este protótipo não realiza recomendação clínica, não opera equipamento real e não deve ser usado para decisão médica. O objetivo é avaliar extração estruturada, robustez a erros de STT e validação de domínio em dados simulados.

---

## 1. Visão geral

O pipeline implementado é:

```text
Áudio curto (.m4a/.mp3)
        ↓
Whisper STT
        ↓
Transcrição textual
        ↓
LLM com structured output
        ↓
Schema Pydantic
        ↓
Regras determinísticas de domínio
        ↓
JSON final validado
```

Foram comparadas duas variantes:

| Variante | Descrição | Papel no experimento |
|---|---|---|
| **A — LLM puro** | Whisper → LLM → Pydantic | Baseline para avaliar o comportamento do LLM com validação estrutural |
| **B — Híbrida** | Whisper → LLM → Pydantic → regras determinísticas | Avalia o ganho de validação semântica, normalização e regras de segurança |

A hipótese testada foi que a Variante B produziria saídas mais robustas, principalmente em campos que exigem decisão auditável, como `confidence` e `requires_confirmation`.

---

## 2. Domínio modelado

O domínio foi restrito a quatro parâmetros de equipamentos médicos. Essa restrição torna o problema pequeno o suficiente para prototipagem, mas realista o bastante para exigir validação semântica.

| Parâmetro canônico | Unidade | Faixa válida | Requer confirmação se |
|---|---:|---:|---|
| `frequencia_respiratoria` | `rpm` | 8–35 | valor < 10 ou > 25 |
| `volume_corrente` | `mL` | 300–800 | variação > 20% em relação a 500 mL |
| `pressao_inspiratoria` | `cmH2O` | 5–40 | valor > 30 |
| `fio2` | `%` | 21–100 | valor > 80 |

O status `fora_de_faixa` é usado quando a extração é compreensível, mas o valor está fora dos limites definidos para o parâmetro. Exemplo: `fio2 = 200%`.

---

## 3. Schema de saída

A saída é validada com Pydantic por meio do schema `ComandoMedico`.

```python
class ComandoMedico(BaseModel):
    intent: Intent
    parameter: Optional[str]
    value: Optional[float]
    unit: Optional[str]
    status: Status
    confidence: Confidence
    requires_confirmation: bool
    validation_errors: list[str]
    normalized_transcript: str
    notes: Optional[str]
```

Enums principais:

```text
intent:
- aumentar_parametro
- reduzir_parametro
- definir_parametro
- consultar_parametro
- desconhecido

status:
- ok
- ambiguo
- incompleto
- invalido
- fora_de_faixa

confidence:
- high
- low
```

### Decisão importante sobre `confidence`

O campo `confidence` **não é confiado ao LLM como fonte final**. Na abordagem híbrida, ele é ajustado por regras determinísticas com base em completude, consistência, unidade inferida e validação de faixa. Essa decisão evita depender de uma autodeclaração subjetiva do modelo.

Em termos práticos:

```text
high = extração completa, consistente, dentro da faixa e sem confirmação obrigatória
low  = qualquer ambiguidade, inferência, ausência de campo, erro ou necessidade de confirmação
```

---

## 4. Dataset

Foram utilizados **25 casos de teste**, cobrindo casos simples e casos de borda.

| Categoria | Casos | Objetivo |
|---|---:|---|
| `valido_simples` | 1–6 | Comandos completos e esperados |
| `unidade_omitida` | 7–10 | Valor presente, unidade implícita |
| `ambiguo` | 11–14 | Intenção ou valor pouco específico |
| `incompleto` | 15–17 | Comandos sem informação suficiente |
| `fora_de_faixa` | 18–21 | Valores fora das faixas clínicas definidas |
| `erro_stt` | 22–25 | Casos com variações fonéticas ou erros simulados |

### Fonte dos áudios

O dataset combina áudio sintético e áudio real:

| Fonte | Casos | Motivo |
|---|---|---|
| Voz humana real (`.m4a`) | 1, 2, 3, 4, 7, 13, 14, 15, 18, 21 | Simular variação natural de fala |
| gTTS (`.mp3`) | demais casos | Garantir cobertura sistemática do catálogo |

Essa combinação permite testar o pipeline em condições controladas, mas sem perder totalmente a variabilidade de fala real.

---

## 5. Estrutura do repositório

```text
voice-command-extraction/
│
├── data/
│   ├── audio/                    # áudios de entrada
│   ├── transcripts/
│   │   ├── reference.json        # catálogo dos comandos
│   │   ├── whisper_output.json   # transcrições brutas
│   │   └── stt_evaluation.json   # avaliação WER/CER
│   ├── results/
│   │   ├── variante_a.json       # saída da Variante A
│   │   ├── variante_b.json       # saída da Variante B
│   │   └── evaluation.json       # comparação final
│   └── answer.py                 # gabarito estruturado
│
├── src/
│   ├── stt.py                    # transcrição de áudio único
│   ├── schema.py                 # schema Pydantic
│   ├── extractor.py              # chamada ao LLM via Groq
│   ├── validator.py              # regras determinísticas da Variante B
│   ├── normalize_text.py         # normalização lexical
│   └── metrics.py                # WER/CER
│
├── scripts/
│   ├── generate_audio.py         # geração dos áudios TTS
│   ├── transcribe_all.py         # transcrição em lote
│   ├── evaluate_stt.py           # avaliação do STT
│   ├── pipeline_a.py             # executa Variante A
│   ├── pipeline_b.py             # executa Variante B
│   └── evaluate_extraction.py    # avaliação comparativa
│
├── tests/
│   └── test_cases.py             # testes automatizados
│
├── notebooks/
│   └── analysis.ipynb            # análise experimental
│
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 6. Instalação

### 6.1. Pré-requisitos

- Python 3.10+
- `ffmpeg` instalado no sistema
- Chave gratuita da Groq para executar a chamada ao LLM

Em Ubuntu/Linux:

```bash
sudo apt install ffmpeg
```

Caso esteja em ambiente institucional sem sudo, é possível instalar o ffmpeg como binário estático em ~/.local/bin sem necessidade de permissão de administrador. Certifique-se de que o diretório esteja no PATH antes de executar o pipeline.

### 6.2. Ambiente virtual

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6.3. Chave da Groq

O projeto usa LLaMA 3.3 70B via Groq.

```bash
export GROQ_API_KEY="sua-chave-aqui"
```

---

## 7. Como executar

Execute os comandos a partir da raiz do projeto.

### 7.1. Gerar áudios TTS

Opcional se os áudios já estiverem em `data/audio/`.

```bash
python scripts/generate_audio.py
```

### 7.2. Transcrever todos os áudios

```bash
python scripts/transcribe_all.py
```

Gera:

```text
data/transcripts/whisper_output.json
```

### 7.3. Avaliar o STT

```bash
python scripts/evaluate_stt.py
```

Gera:

```text
data/transcripts/stt_evaluation.json
```

### 7.4. Rodar a Variante A

```bash
python scripts/pipeline_a.py
```

Gera:

```text
data/results/variante_a.json
```

### 7.5. Rodar a Variante B

```bash
python scripts/pipeline_b.py
```

Gera:

```text
data/results/variante_b.json
```

### 7.6. Avaliar a extração estruturada

```bash
python scripts/evaluate_extraction.py
```

Gera:

```text
data/results/evaluation.json
```

### 7.7. Rodar testes

```bash
pytest tests/ -v
```

Em ambientes com ROS ou plugins globais do pytest interferindo na execução:

```bash
PYTHONPATH="" python -m pytest tests/ -v
```

---

## 8. Resultados

### 8.1. Qualidade do STT

O Whisper foi executado com modelo `base` e `language="pt"`.

| Métrica | Raw | Normalizado | Redução relativa |
|---|---:|---:|---:|
| WER médio | 0.5967 | 0.3273 | 45.2% |
| CER médio | 0.3411 | 0.1337 | 60.8% |

A normalização reduz fortemente o erro aparente porque converte diferenças superficiais, como números por extenso e unidades, para uma forma canônica. Isso mostra que parte relevante do erro bruto não prejudica necessariamente a extração semântica.

Exemplo:

```text
"quinhentos mililitros" → "500 ml"
"fio dois"             → "fio2"
"centímetros de água"  → "cmh2o"
```

### 8.2. Comparação entre variantes

| Métrica | Variante A | Variante B | Delta |
|---|---:|---:|---:|
| Taxa de schema válido | 1.0000 | 1.0000 | 0 |
| Taxa de erro crítico | 0.0400 | 0.0400 | 0 |
| Acurácia média | 0.8343 | 0.8800 | +5.57% |
| F1 macro por intent | 0.5307 | 0.5307 | 0 |

### 8.3. Acurácia por campo

| Campo | Variante A | Variante B | Delta |
|---|---:|---:|---:|
| `intent` | 84% | 84% | 0 |
| `parameter` | 100% | 100% | 0 |
| `value` | 92% | 92% | 0 |
| `unit` | 84% | 84% | 0 |
| `status` | 80% | 80% | 0 |
| `requires_confirmation` | 84% | 88% | +4pp |
| `confidence` | 60% | 88% | +28pp |

---

## 9. Interpretação dos resultados

O ganho mais relevante da Variante B aparece em `confidence` (+28 pontos percentuais) e `requires_confirmation` (+4 pontos percentuais). Isso é coerente com a hipótese experimental: a camada determinística não necessariamente muda a extração bruta feita pelo LLM, mas melhora decisões que dependem de política de segurança e consistência do domínio.

A detecção de `fora_de_faixa` não melhorou numericamente entre as variantes. Isso não invalida a abordagem híbrida. Pelo contrário: sugere que o LLM já foi capaz de identificar casos extremos, como valores muito absurdos. A diferença é que, na Variante A, essa decisão depende do comportamento do modelo; na Variante B, ela é garantida por regra determinística.

Em outras palavras:

```text
Variante A: o modelo pode perceber que está fora da faixa.
Variante B: o sistema verifica e garante que está fora da faixa.
```

O F1 macro por intent foi baixo (0.5307), principalmente porque classes raras, como `consultar_parametro` e `desconhecido`, aparecem pouco no dataset. Em um conjunto pequeno de 25 casos, o F1 macro é sensível à baixa frequência de classes. Por isso, a métrica foi reportada, mas interpretada com cautela.

O erro crítico persistente está associado ao caso em que o STT transforma `"fio dois cem por cento"` em `"Fio 200%"`. Esse erro altera o valor numérico na fonte, tornando a recuperação downstream insegura. O caso ilustra uma limitação fundamental do pipeline: quando o STT corrompe semanticamente um valor numérico, o comportamento correto do pipeline é sinalizar o erro e solicitar reentrada — não tentar inferir o valor original. Segurança em sistemas críticos exige que incerteza seja explícita, não resolvida silenciosamente.

---

## 10. Testes automatizados

Foram implementados 19 testes com `pytest`, cobrindo schema, normalização, validação e casos de borda.

| Grupo | Cobertura |
|---|---|
| `TestSchema` | instanciação válida, valor negativo, campos opcionais, serialização |
| `TestNormalizacao` | números por extenso, números compostos, pontuação, unidades, `fio dois` |
| `TestValidator` | unidade inferida, fora de faixa, confirmação obrigatória, sinônimos |
| `TestCasosDeBorda` | saída inválida do modelo, ambiguidade, incompletude, limite de faixa |

---

## 11. Limitações

1. **Dataset pequeno:** 25 casos são suficientes para uma avaliação experimental, mas não para conclusões estatísticas robustas.
2. **STT sem adaptação ao domínio:** Whisper base não foi ajustado para vocabulário médico em português.
3. **Erros semânticos do STT:** quando o valor numérico é corrompido, o pós-processamento não deve inventar uma correção.
4. **Dependência de API externa:** a extração via LLM usa Groq; resultados podem variar se o modelo for trocado.
5. **Classe `consultar_parametro` pouco representada:** isso reduz a confiabilidade do F1 macro para intents raras.

---

## 12. Próximos passos

- Aumentar o dataset com mais locutores, ruído e variações regionais.
- Adicionar vocabulário técnico e pós-processamento específico para STT.
- Testar modelos STT maiores ou especializados em português.
- Incluir exemplos adicionais de `consultar_parametro` e `desconhecido`.
- Comparar mais modelos de LLM e prompts.
- Separar casos com erro de STT recuperável vs. irrecuperável.
- Adicionar avaliação de latência e custo por chamada.

---

## 13. Conclusão

O experimento mostra que um pipeline baseado em STT + LLM é viável para extrair comandos médicos curtos em português brasileiro, mas também evidencia que LLMs não devem ser usados isoladamente em contextos sensíveis. A camada híbrida de regras não substitui o LLM; ela complementa o modelo com validações auditáveis, especialmente para confiança, confirmação e consistência semântica.

A principal conclusão é que a abordagem mais robusta não é “LLM puro”, mas um pipeline em que o LLM interpreta linguagem natural e regras determinísticas garantem limites de segurança e previsibilidade.
