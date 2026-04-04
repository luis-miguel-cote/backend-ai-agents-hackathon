#!/usr/bin/env python3
"""
Gemelo Digital PROGRESIVO CON APRENDIZAJE
Genera proyectos aprendiendo de experiencias anteriores.
Orquestador principal - toda la logica vive en core/ y agentes/.
"""

import json
import time
from pathlib import Path
from datetime import datetime

from config import config
from core.medicion import medidor
from core.progreso import progreso
from core.aprendizaje import SistemaAprendizaje
from core.input import procesar_input
from core.arquitecto import agente_arquitecto
from core.generador import generar_archivo_individual


# -- Configuracion -----------------------------------------------------------
CONFIG = config.to_dict()
for path in CONFIG["paths"].values():
    Path(path).mkdir(parents=True, exist_ok=True)

# -- Sistema de aprendizaje --------------------------------------------------
sistema_aprendizaje = SistemaAprendizaje(CONFIG)


# -- Flujo principal ----------------------------------------------------------
def crear_proyecto_con_progreso(texto_libre: str = None, ruta_documento: str = None) -> dict:
    """Crea un proyecto con aprendizaje continuo y medicion de tiempos."""

    medidor.iniciar_total()

    # Fase 1: Procesar input
    medidor.iniciar_fase("1. Procesamiento de input")
    contenido_input = procesar_input(texto_libre=texto_libre, ruta_documento=ruta_documento)
    medidor.finalizar_fase()

    if not contenido_input:
        return {"error": "Input vacio"}

    estado = {
        "input_usuario": contenido_input,
        "tipo_proyecto": "",
        "estructura_archivos": {},
        "archivos_generados": {},
        "archivos_por_generar": [],
        "errores": [],
        "revision_aprobada": False,
        "logs": [],
    }

    # Fase 2: Arquitecto
    medidor.iniciar_fase("2. Arquitecto (definir estructura)")
    resultado_arq = agente_arquitecto(estado, sistema_aprendizaje)
    medidor.finalizar_fase()

    estado.update({
        "tipo_proyecto": resultado_arq.get("tipo_proyecto", "landing_page"),
        "archivos_por_generar": resultado_arq.get("archivos_por_generar", []),
        "estructura_archivos": resultado_arq.get("estructura_archivos", {}),
    })

    if not estado["archivos_por_generar"]:
        return {"error": "No hay archivos definidos"}

    print(f"\n\U0001f4cb Archivos a generar: {estado['archivos_por_generar']}")
    progreso.total_archivos = len(estado["archivos_por_generar"])

    # Fase 3: Generacion de archivos
    medidor.iniciar_fase("3. Generacion de archivos")
    progreso.actualizar_etapa("\U0001f3a8 Generando archivos", "Creando cada archivo...")
    tiempos_archivos = {}

    for archivo in estado["archivos_por_generar"]:
        tipo = estado["estructura_archivos"].get(archivo, {}).get("tipo", "txt")
        inicio = time.time()
        try:
            contenido = generar_archivo_individual(archivo, estado["input_usuario"], tipo, sistema_aprendizaje)
        except Exception as e:
            print(f"   \u274c Error generando {archivo}: {e}")
            contenido = f"<!-- Error: {e} -->"
        estado["archivos_generados"][archivo] = contenido
        tiempos_archivos[archivo] = time.time() - inicio
        print(f"      \u23f1\ufe0f  {archivo}: {tiempos_archivos[archivo]:.1f}s")

    medidor.finalizar_fase()

    print(f"\n\U0001f4c4 TIEMPOS POR ARCHIVO:")
    for archivo, t in tiempos_archivos.items():
        print(f"   {archivo:20} : {t:.1f}s")

    # Fase 4: Guardar en disco
    medidor.iniciar_fase("4. Guardado en disco")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_proyecto = Path(CONFIG["paths"]["proyectos"]) / f"proyecto_{timestamp}"
    ruta_proyecto.mkdir(parents=True, exist_ok=True)

    for ruta, contenido in estado["archivos_generados"].items():
        destino = ruta_proyecto / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"   \U0001f4be Guardado: {ruta}")

    medidor.finalizar_fase()

    # Fase 5: Aprendizaje
    medidor.iniciar_fase("5. Aprendizaje (guardar ejemplo)")
    sistema_aprendizaje.guardar_ejemplo(estado, ruta_proyecto)
    medidor.finalizar_fase()

    # Resumen
    tiempo_total = medidor.finalizar_total()
    medidor.mostrar_resumen_tiempos()

    print("\n" + "=" * 60)
    print("\U0001f389 PROYECTO COMPLETADO")
    print("=" * 60)
    print(f"\n\U0001f4c1 Ubicacion: {ruta_proyecto}")
    print(f"\n\U0001f4a1 Para ver tu proyecto:")
    print(f"   cd {ruta_proyecto}")
    print(f"   python -m http.server 8000")

    return {
        "success": True,
        "ruta": str(ruta_proyecto),
        "archivos": list(estado["archivos_generados"].keys()),
        "tiempos": medidor.tiempos,
        "tiempo_total": tiempo_total,
        "tiempos_archivos": tiempos_archivos,
    }


# -- Estadisticas ------------------------------------------------------------
def guardar_estadisticas(resultado: dict):
    """Guarda estadisticas de tiempo para analisis."""
    stats_file = Path(CONFIG["paths"]["aprendizaje"]) / "estadisticas_tiempos.json"

    estadisticas = []
    if stats_file.exists():
        with open(stats_file, "r") as f:
            estadisticas = json.load(f)

    estadisticas.append({
        "fecha": datetime.now().isoformat(),
        "tiempo_total": resultado.get("tiempo_total", 0),
        "tiempos_por_fase": resultado.get("tiempos", {}),
        "tiempos_por_archivo": resultado.get("tiempos_archivos", {}),
        "total_archivos": len(resultado.get("archivos", [])),
    })

    with open(stats_file, "w") as f:
        json.dump(estadisticas[-20:], f, indent=2)

    if len(estadisticas) > 1:
        anteriores = [e["tiempo_total"] for e in estadisticas[:-1]]
        promedio = sum(anteriores) / len(anteriores)
        mejora = ((promedio - resultado["tiempo_total"]) / promedio) * 100
        print(f"\n\U0001f4ca VS PROMEDIO ANTERIOR: {promedio:.1f}s -> {resultado['tiempo_total']:.1f}s")
        if mejora > 0:
            print(f"   \U0001f680 Mejora del {mejora:.1f}% (mas rapido)")
        else:
            print(f"   \u26a0\ufe0f {abs(mejora):.1f}% mas lento que el promedio")


# -- Demo ---------------------------------------------------------------------
def demo():
    ejemplo = """
    Landing page para panaderia artesanal 'Pan Casero'
    Con hero section, menu de productos, galeria y formulario de contacto
    """
    resultado = crear_proyecto_con_progreso(texto_libre=ejemplo)
    if resultado.get("success"):
        print(f"\n\u2728 Proyecto en: {resultado['ruta']}")
        guardar_estadisticas(resultado)


if __name__ == "__main__":
    demo()
