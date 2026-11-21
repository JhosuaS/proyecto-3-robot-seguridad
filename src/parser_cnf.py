import json
import sympy
from sympy.logic.boolalg import to_cnf

def cargar_escenario(ruta_json):
    """Abre el archivo JSON del escenario y retorna su contenido."""
    with open(ruta_json, 'r', encoding='utf-8') as f:
        return json.load(f)

def formula_a_clausulas(formula_str):
    """
    Toma una fórmula en string (ej. "(OBS >> ~PERMISO_MOV)"),
    la convierte con SymPy a CNF, y extrae sus cláusulas.
    """
    expr = sympy.sympify(formula_str)
    expr_cnf = to_cnf(expr, simplify=True)
    term_array = extraer_clausulas(expr_cnf)
    return term_array

def extraer_clausulas(expr):
    """
    Separa las cláusulas de una expresión en la entrada por cada conjunción
    y devuelve una lista[]
    """
    if expr.func == sympy.And:
        clausulas = []
        for hijo in expr.args:
            clausulas.extend(extraer_clausulas(hijo))
        
        return clausulas
    else:
        return [clausula_a_set(expr)]

def clausula_a_set(clausula):
    """
    Determina si cada cláusula está compuesta por más disyunciones
    Retorna un conjunto de cláusulas o símbolos
    """
    lit = set()

    if clausula.func == sympy.Or:
        for arg in clausula.args:
            lit.update(clausula_a_set(arg))
    else:
        if clausula.func == sympy.Not:
            lit.add('~' + str(clausula.args[0]))
        else:
            lit.add(str(clausula))

    return lit

def procesar_reglas(escenario):
    """
    Recupera el conjunto de reglas o Base del Conocimiento (KB) del escenario.
    Retorna un diccionario {id: formula}
    """
    kb_clausulas = {}

    for regla in escenario["reglas"]:
        kb_clausulas[regla["id"]] = formula_a_clausulas(regla["formula"])
        
    return kb_clausulas

def procesar_propiedades(escenario):
    """
    Recupera el conjunto de propiedades del escenario.
    Retorna un diccionario {id: formula}
    """
    propiedades = {}

    for propiedad in escenario["propiedades"]:
        propiedades[propiedad["id"]] = formula_a_clausulas(propiedad["formula"])

    return propiedades

def procesar_variables(escenario):
    """
    Recupera la lista de variables del escenario.
    Retorna una lista[] con los nombres de las variables.
    """
    return list(escenario["variables"])