import time
from pathlib import Path

from src import (
    cargar_escenario,
    procesar_reglas,
    formula_a_clausulas,
    procesar_propiedades,
    procesar_variables,
)
from src.enumeracion import verificar_por_enumeracion
from src.resolucion import verificar_por_resolucion


def aplanar_kb(kb_dict: dict[str, list[set[str]]]) -> list[set[str]]:
    clausulas: list[set[str]] = []
    for lista_clausulas in kb_dict.values():
        clausulas.extend(lista_clausulas)
    return clausulas


def ejecutar_verificacion(ruta_json: Path) -> None:
    print("=" * 70)
    print(f"ESCENARIO: {ruta_json.name}")
    escenario = cargar_escenario(ruta_json)

    variables = procesar_variables(escenario)
    kb_dict = procesar_reglas(escenario)
    kb_clausulas = aplanar_kb(kb_dict)
    propiedades_dict = procesar_propiedades(escenario)
    formulas_prop = {p["id"]: p["formula"] for p in escenario["propiedades"]}

    print(f"Variables ({len(variables)}): {variables}")
    print(f"Total de cláusulas en KB: {len(kb_clausulas)}\n")

    for prop_id, prop_clausulas in propiedades_dict.items():
        formula_orig = formulas_prop[prop_id]
        neg_prop_clausulas = formula_a_clausulas(f"~({formula_orig})")

        print(f"--- Propiedad {prop_id}: {formula_orig} ---")

        t0 = time.perf_counter()
        res_enum = verificar_por_enumeracion(variables, kb_clausulas, prop_clausulas)
        t_enum = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        res_res = verificar_por_resolucion(kb_clausulas, neg_prop_clausulas)
        t_res = (time.perf_counter() - t0) * 1000

        print(
            f"  [Enumeración] Se cumple: {res_enum['se_cumple']} | "
            f"Modelos: {res_enum['modelos_evaluados']} | Tiempo: {t_enum:.3f} ms"
        )
        if res_enum.get("contraejemplo"):
            print(f"     -> Contraejemplo: {res_enum['contraejemplo']}")

        print(
            f"  [Resolución]  Se cumple: {res_res['se_cumple']} | "
            f"Cláusulas gen.: {res_res['clausulas_generadas']} | Tiempo: {t_res:.3f} ms"
        )
        print()


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    carpeta_datos = base_dir / "data"
    escenarios = sorted(carpeta_datos.glob("*.json"))

    if not escenarios:
        print(f"[AVISO] No se encontraron archivos .json en {carpeta_datos}")
        return

    for ruta in escenarios:
        ejecutar_verificacion(ruta)


if __name__ == "__main__":
    main()