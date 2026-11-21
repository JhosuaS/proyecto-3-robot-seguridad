from itertools import product

def evaluar_literal(literal: str, modelo: dict[str, bool]) -> bool:
    """
    Evalúa un literal ´VAR´ o '~VAR' bajo una asignación de verdad
    """
    if literal.startswith("~"):
        var = literal[1:]
        return not modelo[var]
    else:
        return modelo[literal]

def evaluar_clausula(clausula: set[str], modelo: dict[str, bool]) -> bool:
    """"
    Evalúa una disyunción de literales (Clausula CNF).
    Una claúsula vacia representa False
    """
    if not clausula:
        return False
    return any(evaluar_literal(literal, modelo) for literal in clausula)

def evaluar_cnf(clausulas: list[set[str]], modelo: dict[str, bool]) -> bool:
    """"
    Evalua una conjunción de cláusulas (KB o propiedad CNF).
    """
    return all(evaluar_clausula(clausula, modelo) for clausula in clausulas)

def verificar_consistencia(
    variables: list[str],
    kb_clausulas: list[set[str]],
) -> tuple[bool, dict[str, bool] | None]:
    """"
    Verifica si existe al menos un modelo que satisfaga todas las cláusulas de la KB.
    Retorna (es_consistente, primer_modelo_valido)
    """ 
    for valores in product([False, True], repeat=len(variables)):
        modelo = dict(zip(variables, valores))
        if evaluar_cnf(kb_clausulas, modelo):
            return True, modelo
    return False, None   

def verificar_por_enumeracion(
    variables: list[str],
    kb_clausulas: list[set[str]],
    propiedad_clausulas: list[set[str]]
) -> dict:
    """
    Evalúa KB |= propiedad mediante tabla de verdad / backtracking.

    Retorna un diccionario con:
      - "se_cumple": bool (True si KB |= propiedad)
      - "kb_consistente": bool (False si ningun modelo satisface KB) 
      - "modelos_evaluados": int
      - "contraejemplo": dict[str, bool] | None (primer modelo donde KB=True y propiedad=False)
    """
    modelos_evaluados = 0
    kb_satisfecha_en_modelo = False

    for valores in product([False, True], repeat=len(variables)):
        modelo = dict(zip(variables, valores))
        modelos_evaluados += 1

        if evaluar_cnf(kb_clausulas, modelo):
            kb_satisfecha_en_modelo = True
            if not evaluar_cnf(propiedad_clausulas, modelo):
                return {
                    "se_cumple": False,
                    "kb_consistente": True,
                    "modelos_evaluados": modelos_evaluados,
                    "contraejemplo": modelo,
                }
    return {
        "se_cumple": True,
        "kb_consistente": kb_satisfecha_en_modelo,
        "modelos_evaluados": modelos_evaluados,
        "contraejemplo": None,
    }
        