"""
API REST con FastAPI para el Gemelo Digital.
Conecta el flujo de generacion de proyectos con el frontend en React.
"""

import io
import time
import uuid
import zipfile
import threading
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

from config import config
from core.aprendizaje import SistemaAprendizaje
from core.input import procesar_input
from core.arquitecto import agente_arquitecto
from core.generador import generar_archivo_individual
from agentes.agente_devops import generate_deployment_files
from agentes.agente_assets import descargar_imagenes_proyecto
from agentes.agente_documentacion import generar_documentacion_pdf
from agentes.agente_requerimientos import analyze_requirements_google, _construir_resultado

from agentes.agente_qa import agente_qa

# -- Config -------------------------------------------------------------------
CONFIG = config.to_dict()
sistema_aprendizaje = SistemaAprendizaje(CONFIG)

# -- FastAPI app --------------------------------------------------------------
app = FastAPI(title="Gemelo Digital API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir proyectos generados como archivos estaticos
proyectos_path = Path(CONFIG["paths"]["proyectos"])
proyectos_path.mkdir(parents=True, exist_ok=True)

# -- Sesiones en memoria ------------------------------------------------------
sesiones: dict = {}
_lock = threading.Lock()


# -- Schemas ------------------------------------------------------------------
class IniciarRequest(BaseModel):
    descripcion: str

class ResponderRequest(BaseModel):
    respuestas: dict  # {"0": "respuesta a pregunta 1", "1": "respuesta a pregunta 2"}


# -- Endpoints ----------------------------------------------------------------

# Endpoint para exponer el pipeline de agentes al frontend
@app.get("/pipeline")
def obtener_pipeline():
    """
    Devuelve la estructura del pipeline de agentes para el frontend.
    """
    nodes = [
        {"id": "1", "label": "User"},
        {"id": "2", "label": "Orchestrator"},
        {"id": "3", "label": "Requirement"},
        {"id": "4", "label": "Development"},
        {"id": "5", "label": "QA"},
        {"id": "7", "label": "Documentación"},
        {"id": "6", "label": "Output"},
    ]
    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
        {"source": "2", "target": "4"},
        {"source": "3", "target": "5"},
        {"source": "4", "target": "5"},
        {"source": "5", "target": "7"},
        {"source": "7", "target": "6"},
    ]
    return {"nodes": nodes, "edges": edges}

@app.post("/proyecto/iniciar")
def iniciar_proyecto(req: IniciarRequest):
    """Fase 1-2: Procesa input y analiza requerimientos. Devuelve preguntas si las hay."""
    session_id = str(uuid.uuid4())[:8]

    contenido = procesar_input(texto_libre=req.descripcion)
    if not contenido:
        raise HTTPException(status_code=400, detail="Descripcion vacia")

    try:
        analisis = analyze_requirements_google(contenido)
        resultado_reqs = _construir_resultado(analisis)
    except Exception as e:
        resultado_reqs = {
            "titulo": "Proyecto web",
            "resumen": contenido[:200],
            "resumen_completo": contenido,
            "total_funcionales": 0,
            "total_no_funcionales": 0,
            "preguntas_abiertas": [],
            "siguiente_paso": "Continuar con la informacion disponible",
        }
        analisis = None

    preguntas = analisis.open_questions if analisis else []

    sesiones[session_id] = {
        "contenido_original": contenido,
        "contexto_acumulado": contenido,
        "requerimientos": resultado_reqs,
        "preguntas": preguntas,
        "ronda": 1,
        "listo_para_generar": len(preguntas) == 0,
        "estado_generacion": None,
        "resultado": None,
        "progreso": {"fase": "Esperando", "porcentaje": 0, "archivos_listos": []},
    }

    return {
        "session_id": session_id,
        "requerimientos": resultado_reqs,
        "preguntas": preguntas,
        "listo_para_generar": len(preguntas) == 0,
    }


@app.post("/proyecto/{session_id}/responder")
def responder_preguntas(session_id: str, req: ResponderRequest):
    """Recibe respuestas a las preguntas abiertas y re-analiza."""
    sesion = sesiones.get(session_id)
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")

    if sesion["ronda"] >= 3:
        sesion["listo_para_generar"] = True
        return {
            "requerimientos": sesion["requerimientos"],
            "preguntas": [],
            "listo_para_generar": True,
            "mensaje": "Maximo de rondas alcanzado",
        }

    # Enriquecer contexto con respuestas
    partes = []
    for idx, respuesta in req.respuestas.items():
        pregunta = sesion["preguntas"][int(idx)] if int(idx) < len(sesion["preguntas"]) else f"Pregunta {idx}"
        partes.append(f"Pregunta: {pregunta}\nRespuesta: {respuesta}")

    sesion["contexto_acumulado"] += "\n\n--- RESPUESTAS ADICIONALES ---\n" + "\n".join(partes)
    sesion["ronda"] += 1

    # Re-analizar con contexto enriquecido
    try:
        analisis = analyze_requirements_google(sesion["contexto_acumulado"])
        resultado_reqs = _construir_resultado(analisis)
        preguntas = analisis.open_questions
    except Exception:
        resultado_reqs = sesion["requerimientos"]
        preguntas = []

    sesion["requerimientos"] = resultado_reqs
    sesion["preguntas"] = preguntas
    sesion["listo_para_generar"] = len(preguntas) == 0

    return {
        "requerimientos": resultado_reqs,
        "preguntas": preguntas,
        "listo_para_generar": sesion["listo_para_generar"],
        "ronda": sesion["ronda"],
    }


@app.post("/proyecto/{session_id}/generar")
def generar_proyecto(session_id: str, skip_qa: bool = False):
    """Lanza la generacion completa del proyecto en background."""
    sesion = sesiones.get(session_id)
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")

    if sesion["estado_generacion"] == "en_progreso":
        raise HTTPException(status_code=409, detail="Ya hay una generacion en curso")

    sesion["estado_generacion"] = "en_progreso"
    sesion["progreso"] = {"fase": "Iniciando...", "porcentaje": 0, "archivos_listos": []}
    sesion["resultado"] = None

    def _generar():
        try:
            _ejecutar_pipeline(session_id, skip_qa)
        except Exception as e:
            sesion["estado_generacion"] = "error"
            sesion["progreso"]["fase"] = f"Error: {str(e)}"

    thread = threading.Thread(target=_generar, daemon=True)
    thread.start()

    return {"session_id": session_id, "estado": "en_progreso"}


@app.get("/proyecto/{session_id}/estado")
def estado_proyecto(session_id: str):
    """Polling: devuelve el estado actual de la generacion."""
    sesion = sesiones.get(session_id)
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesion no encontrada")

    resp = {
        "estado": sesion.get("estado_generacion"),
        "progreso": sesion.get("progreso", {}),
    }

    if sesion["estado_generacion"] == "completado":
        resp["resultado"] = sesion["resultado"]

    return resp


@app.get("/proyectos")
def listar_proyectos():
    """Lista todos los proyectos generados."""
    carpeta = Path(CONFIG["paths"]["proyectos"])
    proyectos = []

    for p in sorted(carpeta.iterdir(), reverse=True):
        if p.is_dir() and p.name.startswith("proyecto_"):
            archivos = [str(f.relative_to(p)) for f in p.rglob("*") if f.is_file()]
            proyectos.append({
                "nombre": p.name,
                "ruta": str(p),
                "fecha": p.name.replace("proyecto_", ""),
                "archivos": archivos,
                "total_archivos": len(archivos),
            })

    return {"proyectos": proyectos, "total": len(proyectos)}


@app.get("/proyecto/{nombre}/archivos/{ruta_archivo:path}")
def leer_archivo(nombre: str, ruta_archivo: str):
    """Lee el contenido de un archivo de un proyecto generado."""
    carpeta = Path(CONFIG["paths"]["proyectos"])
    archivo = carpeta / nombre / ruta_archivo

    # Prevenir path traversal
    try:
        archivo.resolve().relative_to(carpeta.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    if not archivo.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return {"contenido": archivo.read_text(encoding="utf-8"), "ruta": ruta_archivo}


@app.get("/config")
def ver_config():
    """Devuelve la configuracion actual (sin API keys)."""
    return {
        "llm_provider": config.llm_provider,
        "llm_model": config.llm_model,
        "proyectos_dir": str(config.proyectos_dir),
    }


@app.get("/proyecto/{nombre}/descargar")
def descargar_proyecto(nombre: str):
    """Descarga un proyecto generado como archivo ZIP."""
    carpeta = Path(CONFIG["paths"]["proyectos"])
    ruta_proyecto = carpeta / nombre

    # Prevenir path traversal
    try:
        ruta_proyecto.resolve().relative_to(carpeta.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    if not ruta_proyecto.exists() or not ruta_proyecto.is_dir():
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for archivo in ruta_proyecto.rglob("*"):
            if archivo.is_file():
                zf.write(archivo, archivo.relative_to(ruta_proyecto))
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={nombre}.zip"},
    )


# -- Pipeline interno ---------------------------------------------------------

def _ejecutar_pipeline(session_id: str, skip_qa: bool = False):
    """Ejecuta el pipeline completo de generacion (corre en background thread)."""
    sesion = sesiones[session_id]
    progreso = sesion["progreso"]
    reqs = sesion["requerimientos"]

    input_con_reqs = f"{sesion['contexto_acumulado']}\n\n--- REQUERIMIENTOS ---\n{reqs['resumen_completo']}"

    estado = {
        "input_usuario": input_con_reqs,
        "tipo_proyecto": "",
        "estructura_archivos": {},
        "archivos_generados": {},
        "archivos_por_generar": [],
        "errores": [],
        "revision_aprobada": False,
        "logs": [],
        "requerimientos": reqs,
    }

    # Fase 3: Arquitecto
    progreso["fase"] = "Definiendo arquitectura..."
    progreso["porcentaje"] = 10
    progreso["logs"] = []
    progreso["logs"].append("🧠 Arquitecto: analizando requerimientos...")
    resultado_arq = agente_arquitecto(estado, sistema_aprendizaje)

    estado.update({
        "tipo_proyecto": resultado_arq.get("tipo_proyecto", "landing_page"),
        "archivos_por_generar": resultado_arq.get("archivos_por_generar", []),
        "estructura_archivos": resultado_arq.get("estructura_archivos", {}),
    })

    if not estado["archivos_por_generar"]:
        sesion["estado_generacion"] = "error"
        progreso["fase"] = "Error: No hay archivos definidos"
        progreso["logs"].append("❌ Arquitecto: no se definieron archivos")
        return

    progreso["logs"].append(f"🧠 Arquitecto: tipo={estado['tipo_proyecto']}, archivos={estado['archivos_por_generar']}")

    # Fase 4: Generacion
    progreso["fase"] = "Generando archivos..."
    progreso["porcentaje"] = 20
    progreso["logs"].append("⚙️ Generador: iniciando generación de archivos...")
    tiempos_archivos = {}

    orden = {"index.html": 0, "css/styles.css": 1, "js/main.js": 2}
    archivos_ordenados = sorted(estado["archivos_por_generar"], key=lambda a: orden.get(a, 99))
    total = len(archivos_ordenados)

    for i, archivo in enumerate(archivos_ordenados):
        tipo = estado["estructura_archivos"].get(archivo, {}).get("tipo", "txt")
        inicio = time.time()

        try:
            contenido = generar_archivo_individual(
                archivo, estado["input_usuario"], tipo, sistema_aprendizaje,
                archivos_previos=estado["archivos_generados"]
            )
        except Exception as e:
            contenido = f"<!-- Error: {e} -->"

        estado["archivos_generados"][archivo] = contenido
        tiempos_archivos[archivo] = time.time() - inicio
        progreso["archivos_listos"].append(archivo)
        progreso["porcentaje"] = 20 + int((i + 1) / total * 50)
        progreso["fase"] = f"Generado: {archivo}"
        progreso["logs"].append(f"⚙️ Generador: {archivo} ({tiempos_archivos[archivo]:.1f}s)")

    # DevOps
    progreso["fase"] = "🚀 Generando archivos DevOps..."
    progreso["porcentaje"] = 75
    deploy_files = generate_deployment_files(estado["tipo_proyecto"])
    estado["archivos_generados"].update(deploy_files)
    archivos_devops = list(deploy_files.keys())
    progreso["archivos_listos"].extend(archivos_devops)
    progreso["logs"] = progreso.get("logs", [])
    progreso["logs"].append(f"🚀 DevOps: generados {', '.join(archivos_devops)}")

    # QA
    veredicto_qa = {"verdict": "SKIPPED", "pass_rate": 0, "color": "YELLOW"}
    if not skip_qa:
        progreso["fase"] = "Validando calidad (QA)..."
        progreso["porcentaje"] = 80
        progreso["logs"].append("🔍 QA: ejecutando análisis de calidad...")
        veredicto_qa = agente_qa(estado["archivos_generados"], estado["input_usuario"])
        progreso["logs"].append(f"🔍 QA: {veredicto_qa.get('verdict', 'N/A')} — pass rate: {veredicto_qa.get('pass_rate', 0)}%")

    estado["revision_aprobada"] = veredicto_qa.get("color") != "RED"

    # Guardar en disco
    progreso["fase"] = "Guardando proyecto..."
    progreso["porcentaje"] = 90
    progreso["logs"].append("💾 Guardando proyecto en disco...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_proyecto = Path(CONFIG["paths"]["proyectos"]) / f"proyecto_{timestamp}"
    ruta_proyecto.mkdir(parents=True, exist_ok=True)

    for ruta, contenido in estado["archivos_generados"].items():
        destino = ruta_proyecto / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(contenido)

    # Assets (imagenes)
    progreso["fase"] = "Descargando imagenes..."
    progreso["logs"].append("🖼️ Assets: descargando imágenes...")
    descargar_imagenes_proyecto(ruta_proyecto, estado["input_usuario"])
    progreso["logs"].append("🖼️ Assets: imágenes descargadas")

    # Documentación PDF
    progreso["fase"] = "Generando documentación PDF..."
    progreso["porcentaje"] = 93
    progreso["logs"].append("📄 Documentación: generando PDF...")
    try:
        generar_documentacion_pdf(estado, ruta_proyecto, veredicto_qa)
        progreso["logs"].append("📄 Documentación: PDF generado")
    except Exception as e:
        print(f"   WARNING: Error generando PDF: {e}")
        progreso["logs"].append(f"📄 Documentación: error ({e})")

    # Aprendizaje
    sistema_aprendizaje.guardar_ejemplo(estado, ruta_proyecto)
    progreso["logs"].append("📚 Aprendizaje: ejemplo guardado")

    # Resultado final
    progreso["fase"] = "Completado"
    progreso["porcentaje"] = 100
    progreso["logs"].append("✅ Pipeline completado")

    sesion["estado_generacion"] = "completado"
    sesion["resultado"] = {
        "nombre": ruta_proyecto.name,
        "ruta": str(ruta_proyecto),
        "archivos": list(estado["archivos_generados"].keys()),
        "tiempos_archivos": tiempos_archivos,
        "requerimientos": reqs,
        "qa": veredicto_qa,
        "tipo_proyecto": estado["tipo_proyecto"],
    }


# -- Montar archivos estaticos (al final para no interceptar rutas API) -------
app.mount("/proyectos_static", StaticFiles(directory=str(proyectos_path)), name="proyectos")
