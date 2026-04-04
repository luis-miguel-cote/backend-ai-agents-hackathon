import json
from pathlib import Path
from datetime import datetime

class SistemaAprendizaje:
    """Sistema que aprende de proyectos anteriores"""
    def __init__(self, config):
        self.ejemplos = []
        self.lecciones = []
        self.config = config
        self.cargar_aprendizaje()
    def cargar_aprendizaje(self):
        ejemplos_dir = Path(self.config["paths"]["aprendizaje"]) / "ejemplos"
        ejemplos_dir.mkdir(parents=True, exist_ok=True)
        for archivo in ejemplos_dir.glob("*.json"):
            try:
                with open(archivo, 'r') as f:
                    self.ejemplos.append(json.load(f))
            except:
                pass
        lecciones_file = Path(self.config["paths"]["aprendizaje"]) / "lecciones.json"
        if lecciones_file.exists():
            try:
                with open(lecciones_file, 'r') as f:
                    self.lecciones = json.load(f)
            except:
                pass
        print(f"📚 Aprendizaje cargado: {len(self.ejemplos)} ejemplos, {len(self.lecciones)} lecciones")
    def guardar_ejemplo(self, estado: dict, ruta_proyecto: Path):
        ejemplos_dir = Path(self.config["paths"]["aprendizaje"]) / "ejemplos"
        ejemplos_dir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "descripcion": estado.get("input_usuario", "")[:300],
            "tipo": estado.get("tipo_proyecto", "landing_page"),
            "archivos": list(estado.get("archivos_generados", {}).keys()),
            "fecha": datetime.now().isoformat(),
            "estructura": estado.get("estructura_archivos", {})
        }
        filename = f"ejemplo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(ejemplos_dir / filename, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"📚 Proyecto guardado como ejemplo para aprendizaje futuro")
    def guardar_leccion(self, problema: str, solucion: str, contexto: str):
        leccion = {
            "problema": problema,
            "solucion": solucion,
            "contexto": contexto[:200],
            "fecha": datetime.now().isoformat()
        }
        self.lecciones.append(leccion)
        lecciones_file = Path(self.config["paths"]["aprendizaje"]) / "lecciones.json"
        with open(lecciones_file, 'w') as f:
            json.dump(self.lecciones, f, indent=2)
        print(f"🧠 Nueva lección aprendida: {problema[:50]}...")
    def obtener_contexto_aprendizaje(self, descripcion: str) -> str:
        contexto = ""
        if self.ejemplos:
            contexto += "\n--- EJEMPLOS DE PROYECTOS ANTERIORES ---\n"
            for i, ejemplo in enumerate(self.ejemplos[-2:], 1):
                contexto += f"Ejemplo {i}: {ejemplo.get('descripcion', '')[:100]}\n"
                contexto += f"Archivos: {ejemplo.get('archivos', [])}\n\n"
        if self.lecciones:
            contexto += "--- LECCIONES APRENDIDAS ---\n"
            for leccion in self.lecciones[-3:]:
                contexto += f"- Problema: {leccion.get('problema', '')}\n"
                contexto += f"  Solución: {leccion.get('solucion', '')}\n"
        return contexto
