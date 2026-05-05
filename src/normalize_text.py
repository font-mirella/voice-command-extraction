# normalize_text.py

import re

NUMBER_WORDS = {
    "zero": "0",
    "um": "1",
    "uma": "1",
    "dois": "2",
    "duas": "2",
    "três": "3",
    "tres": "3",
    "quatro": "4",
    "cinco": "5",
    "seis": "6",
    "sete": "7",
    "oito": "8",
    "nove": "9",
    "dez": "10",
    "onze": "11",
    "doze": "12",
    "treze": "13",
    "quatorze": "14",
    "catorze": "14",
    "quinze": "15",
    "dezesseis": "16",
    "dezessete": "17",
    "dezoito": "18",
    "dezenove": "19",
    "vinte": "20",
    "trinta": "30",
    "quarenta": "40",
    "cinquenta": "50",
    "sessenta": "60",
    "setenta": "70",
    "oitenta": "80",
    "noventa": "90",
    "cem": "100",
    "cento": "100",
    "trezentos": "300",
    "quatrocentos": "400",
    "quinhentos": "500",
    "seiscentos": "600",
    "setecentos": "700",
    "oitocentos": "800",
}

def normalize_for_metrics(text: str) -> str:
    text = text.lower().strip()

    # normaliza pontuação básica
    text = text.replace(",", " ")
    text = text.replace(".", " ")
    text = text.replace("%", " por cento")

    # normaliza unidades
    text = text.replace("mililitros", "ml")
    text = text.replace("mililitro", "ml")
    text = text.replace("centímetros de água", "cmh2o")
    text = text.replace("centimetros de agua", "cmh2o")
    text = text.replace("centímetro de água", "cmh2o")
    text = text.replace("centimetro de agua", "cmh2o")

    # caso especial: fio dois / fio 2
    text = text.replace("fio dois", "fio2")
    text = text.replace("fio 2", "fio2")
    text = text.replace("fi o2", "fio2")

    words = text.split()
    normalized_words = []

    i = 0
    while i < len(words):
        # trata combinações tipo "quatrocentos e cinquenta"
        if (
            i + 2 < len(words)
            and words[i] in NUMBER_WORDS
            and words[i + 1] == "e"
            and words[i + 2] in NUMBER_WORDS
        ):
            try:
                value = int(NUMBER_WORDS[words[i]]) + int(NUMBER_WORDS[words[i + 2]])
                normalized_words.append(str(value))
                i += 3
                continue
            except ValueError:
                pass

        word = words[i]
        normalized_words.append(NUMBER_WORDS.get(word, word))
        i += 1

    text = " ".join(normalized_words)

    # remove espaços extras
    text = re.sub(r"\s+", " ", text).strip()

    return text