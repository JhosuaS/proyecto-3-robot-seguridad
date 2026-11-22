def _complemento(literal: str) -> str:
    return literal[1:] if literal.startswith("~") else "~" + literal


def _texto(clausula: frozenset[str]) -> str:
    ordenados = sorted(clausula, key=lambda l: (l.lstrip("~"), l.startswith("~")))
    return "{" + ", ".join(ordenados) + "}"


def _resolver(iniciales: list[set[str]]) -> tuple[list[frozenset[str]], dict]:
    clausulas = list(dict.fromkeys(frozenset(c) for c in iniciales))
    padres: dict = {}
    i = 0
    while i < len(clausulas) and frozenset() not in clausulas:
        for j in range(i):
            for literal in clausulas[i]:
                complemento = _complemento(literal)
                if complemento not in clausulas[j]:
                    continue
                resolvente = (clausulas[i] - {literal}) | (clausulas[j] - {complemento})
                if resolvente in clausulas or any(_complemento(l) in resolvente for l in resolvente):
                    continue
                clausulas.append(resolvente)
                padres[resolvente] = (clausulas[i], clausulas[j], literal)
        i += 1
    return clausulas, padres


def _pasos(padres: dict) -> list[str]:
    pasos: list[str] = []
    vistos: set = set()

    def visitar(clausula: frozenset[str]) -> None:
        if clausula not in padres or clausula in vistos:
            return
        vistos.add(clausula)
        a, b, literal = padres[clausula]
        visitar(a)
        visitar(b)
        pasos.append(f"{_texto(a)} + {_texto(b)} [{literal.lstrip('~')}] -> {_texto(clausula)}")

    visitar(frozenset())
    return pasos


def verificar_por_resolucion(
    kb_clausulas: list[set[str]],
    neg_propiedad_clausulas: list[set[str]]
) -> dict:
    """
    Evalúa KB |= propiedad por refutación: aplica resolución proposicional
    sobre (KB & ~propiedad) hasta derivar la cláusula vacía o saturar.

    Retorna un diccionario con:
      - "se_cumple": bool (True si se deriva la cláusula vacía)
      - "kb_consistente": bool (False si la KB sola ya deriva la cláusula vacía)
      - "pasos": list[str] (prueba mínima hasta la cláusula vacía)
      - "clausulas_generadas": int
    """
    clausulas_kb, padres_kb = _resolver(kb_clausulas)
    if frozenset() in clausulas_kb:
        return {
            "se_cumple": True,
            "kb_consistente": False,
            "pasos": _pasos(padres_kb),
            "clausulas_generadas": len(padres_kb),
        }

    clausulas, padres = _resolver(kb_clausulas + neg_propiedad_clausulas)
    se_cumple = frozenset() in clausulas
    return {
        "se_cumple": se_cumple,
        "kb_consistente": True,
        "pasos": _pasos(padres) if se_cumple else [],
        "clausulas_generadas": len(padres),
    }
