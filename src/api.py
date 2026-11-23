"""
Micro-API REST con FastAPI para el Verificador Lógico de Seguridad.

Endpoints:
  GET  /api/escenarios          → Lista los archivos .json disponibles en data/
  GET  /api/escenarios/{nombre} → Devuelve el contenido JSON de un escenario
  POST /api/verificar           → Ejecuta la verificación lógica y retorna resultados
"""

import json
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.parser_cnf import (
    cargar_escenario,
    formula_a_clausulas,
    procesar_propiedades,
    procesar_reglas,
    procesar_variables,
)
from src.enumeracion import verificar_por_enumeracion
from src.resolucion import verificar_por_resolucion

# ---------------------------------------------------------------------------
# App & CORS
# ---------------------------------------------------------------------------

app = FastAPI(title="Verificador de Seguridad – Robot Doméstico")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Rutas de directorios
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = Path(__file__).resolve().parent / "static"

# ---------------------------------------------------------------------------
# Servir el frontend estático
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _aplanar_kb(kb_dict: dict[str, list[set[str]]]) -> list[set[str]]:
    clausulas: list[set[str]] = []
    for lista_clausulas in kb_dict.values():
        clausulas.extend(lista_clausulas)
    return clausulas


def _sets_a_listas(obj):
    """Convierte sets a listas para serialización JSON."""
    if isinstance(obj, set | frozenset):
        return sorted(obj)
    if isinstance(obj, dict):
        return {k: _sets_a_listas(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sets_a_listas(item) for item in obj]
    return obj


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    """Sirve el index.html principal."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html no encontrado")
    return FileResponse(str(index_path))


@app.get("/api/escenarios")
async def listar_escenarios():
    """Lista los nombres de archivos .json en data/."""
    if not DATA_DIR.exists():
        return JSONResponse(content=[])
    archivos = sorted(f.name for f in DATA_DIR.glob("*.json"))
    return JSONResponse(content=archivos)


@app.get("/api/escenarios/{nombre}")
async def obtener_escenario(nombre: str):
    """Devuelve el contenido JSON de un escenario."""
    ruta = DATA_DIR / nombre
    if not ruta.exists() or not ruta.suffix == ".json":
        raise HTTPException(status_code=404, detail=f"Escenario '{nombre}' no encontrado")
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = json.load(f)
    return JSONResponse(content=contenido)


@app.post("/api/verificar")
async def verificar(request: Request):
    """
    Recibe un escenario JSON completo, ejecuta la verificación por
    enumeración y resolución, y devuelve los resultados.
    """
    try:
        escenario = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    # Validar claves requeridas
    for clave in ("variables", "reglas", "propiedades"):
        if clave not in escenario:
            raise HTTPException(
                status_code=400,
                detail=f"Falta la clave requerida: '{clave}'",
            )

    try:
        variables = procesar_variables(escenario)
        kb_dict = procesar_reglas(escenario)
        kb_clausulas = _aplanar_kb(kb_dict)
        propiedades_dict = procesar_propiedades(escenario)
        formulas_prop = {p["id"]: p["formula"] for p in escenario["propiedades"]}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al procesar el escenario: {str(e)}",
        )

    resultados = []

    for prop_id, prop_clausulas in propiedades_dict.items():
        formula_orig = formulas_prop[prop_id]
        neg_prop_clausulas = formula_a_clausulas(f"~({formula_orig})")

        # Enumeración
        t0 = time.perf_counter()
        res_enum = verificar_por_enumeracion(variables, kb_clausulas, prop_clausulas)
        t_enum = (time.perf_counter() - t0) * 1000

        # Resolución
        t0 = time.perf_counter()
        res_res = verificar_por_resolucion(kb_clausulas, neg_prop_clausulas)
        t_res = (time.perf_counter() - t0) * 1000

        # Buscar descripción de la propiedad
        descripcion = ""
        for p in escenario["propiedades"]:
            if p["id"] == prop_id:
                descripcion = p.get("descripcion", "")
                break

        resultados.append({
            "id": prop_id,
            "formula": formula_orig,
            "descripcion": descripcion,
            "enumeracion": {
                "se_cumple": res_enum["se_cumple"],
                "kb_consistente": res_enum["kb_consistente"],
                "modelos_evaluados": res_enum["modelos_evaluados"],
                "contraejemplo": _sets_a_listas(res_enum.get("contraejemplo")),
                "tiempo_ms": round(t_enum, 3),
            },
            "resolucion": {
                "se_cumple": res_res["se_cumple"],
                "kb_consistente": res_res["kb_consistente"],
                "clausulas_generadas": res_res["clausulas_generadas"],
                "pasos": res_res.get("pasos", []),
                "tiempo_ms": round(t_res, 3),
            },
        })

    # Estado global
    todo_seguro = all(r["enumeracion"]["se_cumple"] and r["resolucion"]["se_cumple"] for r in resultados)

    return JSONResponse(content={
        "estado_global": "SEGURO" if todo_seguro else "VULNERABLE",
        "total_variables": len(variables),
        "total_clausulas_kb": len(kb_clausulas),
        "propiedades": resultados,
    })
