# metrics.py

def calcular_wer(referencia: str, transcricao: str) -> float:
    """
    Word Error Rate simples: (S + D + I) / N
    onde S=substituições, D=deleções, I=inserções, N=palavras de referência
    Implementação via programação dinâmica (distância de edição em palavras)
    """
    ref = referencia.lower().split()
    hyp = transcricao.lower().split()

    n = len(ref)
    m = len(hyp)

    # Matriz de edição
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],    # deleção
                                   dp[i][j - 1],    # inserção
                                   dp[i - 1][j - 1]) # substituição

    return round(dp[n][m] / max(n, 1), 4)


def calcular_cer(referencia: str, transcricao: str) -> float:
    """Character Error Rate — mesma lógica do WER mas em nível de caractere"""
    ref = list(referencia.lower())
    hyp = list(transcricao.lower())

    n = len(ref)
    m = len(hyp)

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],
                                   dp[i][j - 1],
                                   dp[i - 1][j - 1])

    return round(dp[n][m] / max(n, 1), 4)
