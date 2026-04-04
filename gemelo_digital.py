#!/usr/bin/env python3
"""
Gemelo Digital PROGRESIVO CON APRENDIZAJE
Genera proyectos aprendiendo de experiencias anteriores
"""

import os
import json
import time
import re
from pathlib import Path
from typing import TypedDict, List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# LangChain
from langchain_ollama import ChatOllama

# Para parsing de documentos
import docx
import PyPDF2

# Para UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ============================================================================
# CONFIGURACIÓN (cargada desde variables de entorno)
# ============================================================================
# La configuración se carga desde config.py que usa variables de entorno
# Ver config.py para más detalles y env_example.txt para crear .env

try:
    from config import config
    print("✅ Configuración cargada desde variables de entorno")
    CONFIG = config.to_dict()
except ImportError as e:
    raise ImportError(f"❌ No se pudo cargar config.py: {e}. Debes definir todas las variables de entorno requeridas y asegurarte de que config.py existe.")
    

# Crear directorios (ya se crean en config.py, pero por compatibilidad)
for path in CONFIG["paths"].values():
    Path(path).mkdir(parents=True, exist_ok=True)



# ============================================================================
# SISTEMA DE MEDICIÓN DE TIEMPOS
# ============================================================================

class MedidorTiempos:
    """Mide y registra tiempos de ejecución de cada fase"""
    
    def __init__(self):
        self.tiempos = {}
        self.inicio_total = None
        self.fin_total = None
        self.fase_actual = None
        self.inicio_fase = None
    
    def iniciar_total(self):
        """Inicia el temporizador global"""
        self.inicio_total = time.time()
        print(f"\n⏱️  INICIO DEL PROCESO: {datetime.now().strftime('%H:%M:%S')}")
    
    def finalizar_total(self):
        """Finaliza el temporizador global"""
        self.fin_total = time.time()
        total = self.obtener_total()
        print(f"\n⏱️  FIN DEL PROCESO: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        print(f"📊 TIEMPO TOTAL: {total:.1f} segundos ({total/60:.1f} minutos)")
        print(f"{'='*60}")
        return total
    
    def iniciar_fase(self, nombre_fase: str):
        """Inicia una nueva fase de medición"""
        # Finalizar fase anterior si existe
        if self.fase_actual and self.inicio_fase:
            self.finalizar_fase()
        
        self.fase_actual = nombre_fase
        self.inicio_fase = time.time()
        print(f"\n▶️  INICIO: {nombre_fase}")
    
    def finalizar_fase(self):
        """Finaliza la fase actual y registra el tiempo"""
        if self.fase_actual and self.inicio_fase:
            duracion = time.time() - self.inicio_fase
            self.tiempos[self.fase_actual] = duracion
            print(f"✅ FINALIZADO: {self.fase_actual} - {duracion:.1f} segundos")
            self.fase_actual = None
            self.inicio_fase = None
    
    def obtener_total(self) -> float:
        """Obtiene el tiempo total transcurrido"""
        if self.inicio_total and self.fin_total:
            return self.fin_total - self.inicio_total
        return 0
    
    def obtener_tiempo_fase(self, nombre_fase: str) -> float:
        """Obtiene el tiempo de una fase específica"""
        return self.tiempos.get(nombre_fase, 0)
    
    def mostrar_resumen_tiempos(self):
        """Muestra un resumen detallado de todos los tiempos"""
        print(f"\n{'='*60}")
        print("📊 RESUMEN DE TIEMPOS DE EJECUCIÓN")
        print(f"{'='*60}")
        
        # Ordenar por tiempo (mayor a menor)
        tiempos_ordenados = sorted(self.tiempos.items(), key=lambda x: x[1], reverse=True)
        
        for fase, tiempo in tiempos_ordenados:
            porcentaje = (tiempo / self.obtener_total()) * 100
            barra = "█" * int(porcentaje / 2) + "░" * (50 - int(porcentaje / 2))
            print(f"   {fase:20} : {tiempo:6.1f}s ({porcentaje:5.1f}%) {barra}")
        
        print(f"{'='*60}")
        print(f"   {'TOTAL':20} : {self.obtener_total():6.1f}s (100.0%)")
        print(f"{'='*60}")
        
        # Mostrar estadísticas adicionales
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   Fase más lenta: {max(self.tiempos, key=self.tiempos.get)} ({max(self.tiempos.values()):.1f}s)")
        print(f"   Fase más rápida: {min(self.tiempos, key=self.tiempos.get)} ({min(self.tiempos.values()):.1f}s)")
        print(f"   Total fases: {len(self.tiempos)}")

# Instancia global del medidor
medidor = MedidorTiempos()

# ============================================================================
# SISTEMA DE PROGRESO
# ============================================================================

class ProgresoVisual:
    def __init__(self):
        self.total_archivos = 0
        self.completados = 0
    
    def iniciar_proyecto(self, nombre: str):
        print(f"\n{'='*60}")
        print(f"🤖 GEMELO DIGITAL - {nombre}")
        print(f"{'='*60}\n")
    
    def actualizar_etapa(self, etapa: str, descripcion: str = ""):
        print(f"\n📌 {etapa}")
        if descripcion:
            print(f"   {descripcion}")
    
    def iniciar_generacion_archivo(self, ruta: str):
        print(f"   ⚙️ Generando: {ruta}")
    
    def completar_archivo(self, ruta: str, tamaño: int, preview: str = ""):
        self.completados += 1
        print(f"   ✅ Completado: {ruta} ({tamaño} bytes)")
        if preview:
            print(f"      📄 {preview[:80]}...")
        
        if self.total_archivos > 0:
            pct = (self.completados / self.total_archivos) * 100
            barra = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"   📊 [{barra}] {self.completados}/{self.total_archivos} ({pct:.0f}%)")
    
    def mostrar_resumen(self, archivos: Dict[str, str]):
        print(f"\n📁 Archivos generados ({len(archivos)} totales):")
        for ruta in sorted(archivos.keys()):
            print(f"   📄 {ruta} ({len(archivos[ruta]):,} bytes)")

progreso = ProgresoVisual()

# ============================================================================
# SISTEMA DE APRENDIZAJE
# ============================================================================

class SistemaAprendizaje:
    """Sistema que aprende de proyectos anteriores"""
    
    def __init__(self):
        self.ejemplos = []
        self.lecciones = []
        self.cargar_aprendizaje()
    
    def cargar_aprendizaje(self):
        """Carga proyectos anteriores como ejemplos"""
        # Usar config si está disponible, sino usar CONFIG
        if CONFIG_LOADED:
            ejemplos_dir = config.aprendizaje_dir / "ejemplos"
        else:
            ejemplos_dir = Path(CONFIG["paths"]["aprendizaje"]) / "ejemplos"
        
        ejemplos_dir.mkdir(parents=True, exist_ok=True)
        
        for archivo in ejemplos_dir.glob("*.json"):
            try:
                with open(archivo, 'r') as f:
                    self.ejemplos.append(json.load(f))
            except:
                pass
        
        # Cargar lecciones
        if CONFIG_LOADED:
            lecciones_file = config.aprendizaje_dir / "lecciones.json"
        else:
            lecciones_file = Path(CONFIG["paths"]["aprendizaje"]) / "lecciones.json"
            
        if lecciones_file.exists():
            try:
                with open(lecciones_file, 'r') as f:
                    self.lecciones = json.load(f)
            except:
                pass
        
        print(f"📚 Aprendizaje cargado: {len(self.ejemplos)} ejemplos, {len(self.lecciones)} lecciones")
    
    def guardar_ejemplo(self, estado: dict, ruta_proyecto: Path):
        """Guarda el proyecto como ejemplo para futuras generaciones"""
        # Usar config si está disponible, sino usar CONFIG
        if CONFIG_LOADED:
            ejemplos_dir = config.aprendizaje_dir / "ejemplos"
        else:
            ejemplos_dir = Path(CONFIG["paths"]["aprendizaje"]) / "ejemplos"
        
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
        """Guarda una lección aprendida"""
        leccion = {
            "problema": problema,
            "solucion": solucion,
            "contexto": contexto[:200],
            "fecha": datetime.now().isoformat()
        }
        
        self.lecciones.append(leccion)
        
        # Usar config si está disponible, sino usar CONFIG
        if CONFIG_LOADED:
            lecciones_file = config.aprendizaje_dir / "lecciones.json"
        else:
            lecciones_file = Path(CONFIG["paths"]["aprendizaje"]) / "lecciones.json"
            
        with open(lecciones_file, 'w') as f:
            json.dump(self.lecciones, f, indent=2)
        
        print(f"🧠 Nueva lección aprendida: {problema[:50]}...")
    
    def obtener_contexto_aprendizaje(self, descripcion: str) -> str:
        """Obtiene contexto de aprendizaje para mejorar generación"""
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
sistema_aprendizaje = SistemaAprendizaje()

# ============================================================================
# ESTADO DEL SISTEMA
# ============================================================================

class EstadoProyecto(TypedDict):
    input_usuario: str
    tipo_proyecto: str
    estructura_archivos: Dict[str, Dict]
    archivos_generados: Dict[str, str]
    archivos_por_generar: List[str]
    errores: List[str]
    revision_aprobada: bool
    logs: List[str]

# ============================================================================
# MODELOS
# ============================================================================
class ModelManager:
    def __init__(self):
        self.models = {}
        self._inicializar_modelos()
    
    def _inicializar_modelos(self):
        try:
            # Determinar qué configuración usar
            if 'CONFIG_LOADED' in globals() and CONFIG_LOADED:
                # Usar configuración desde variables de entorno
                ollama_url = config.ollama_url
                timeout = config.ollama_timeout
                num_threads = config.num_threads
                temperature = config.temperature
                model_arquitecto = config.model_arquitecto
                model_frontend = config.model_frontend
                arquitecto_context_size = config.arquitecto_context_size
                frontend_context_size = config.frontend_context_size
            else:
                # Usar configuración por defecto
                ollama_url = CONFIG["ollama_url"]
                timeout = 120  # valor por defecto
                num_threads = CONFIG["num_threads"]
                temperature = 0.2  # valor por defecto
                model_arquitecto = CONFIG["models"]["arquitecto"]
                model_frontend = CONFIG["models"]["frontend"]
                arquitecto_context_size = 2048  # valor por defecto
                frontend_context_size = 4096  # valor por defecto
            
            self.models = {
                "arquitecto": ChatOllama(
                    model=model_arquitecto,
                    temperature=temperature,
                    num_thread=num_threads,
                    num_ctx=arquitecto_context_size,
                    base_url=ollama_url,
                    timeout=timeout
                ),
                "frontend": ChatOllama(
                    model=model_frontend,
                    temperature=temperature,
                    num_thread=num_threads,
                    num_ctx=frontend_context_size,
                    base_url=ollama_url,
                    timeout=timeout
                ),
            }
            print("✅ Modelos inicializados correctamente")
            print(f"   Arquitecto: {model_arquitecto}")
            print(f"   Frontend: {model_frontend}")
        except Exception as e:
            print(f"❌ Error inicializando modelos: {e}")
            print(f"   Detalles: {type(e).__name__}: {str(e)}")
    
    def get(self, nombre: str):
        return self.models.get(nombre)

model_manager = ModelManager()

# ============================================================================
# PROCESAMIENTO DE INPUT
# ============================================================================

def procesar_input(texto_libre: str = None, ruta_documento: str = None) -> str:
    contenido = ""
    
    if texto_libre:
        contenido = texto_libre
        progreso.actualizar_etapa("📝 Procesando input", f"{len(contenido)} caracteres")
    
    elif ruta_documento:
        progreso.actualizar_etapa("📄 Leyendo documento", ruta_documento)
        ext = Path(ruta_documento).suffix.lower()
        
        try:
            if ext == '.pdf':
                with open(ruta_documento, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    contenido = "\n".join([page.extract_text() for page in reader.pages])
            elif ext in ['.docx', '.doc']:
                doc = docx.Document(ruta_documento)
                contenido = "\n".join([para.text for para in doc.paragraphs])
            else:
                with open(ruta_documento, 'r', encoding='utf-8') as f:
                    contenido = f.read()
        except Exception as e:
            progreso.actualizar_etapa("❌ Error", str(e))
    
    return contenido

# ============================================================================
# AGENTE ARQUITECTO (con aprendizaje)
# ============================================================================

def agente_arquitecto(state: EstadoProyecto):
    """Define la estructura de archivos APRENDIENDO de proyectos anteriores"""
    progreso.actualizar_etapa("🏗️ Arquitecto", "Definiendo estructura...")
    
    # Estructura por defecto
    archivos_por_defecto = ["index.html", "css/styles.css", "js/main.js", "README.md"]
    
    try:
        contexto = sistema_aprendizaje.obtener_contexto_aprendizaje(state['input_usuario'])
        
        prompt = f"""
        Eres un Arquitecto de Software que APRENDE de experiencias pasadas.
        
        {contexto}
        
        Diseña la estructura de archivos para:
        "{state['input_usuario'][:400]}"
        
        Reglas:
        - Landing page: index.html, css/styles.css, js/main.js, README.md
        - Web app: añadir main.py, requirements.txt
        - Dashboard: añadir components/, services/
        
        Responde SOLO en JSON:
        {{"tipo_proyecto": "landing_page", "archivos": ["index.html", "css/styles.css", "js/main.js", "README.md"]}}
        """
        
        response = model_manager.get("arquitecto").invoke(prompt)
        contenido = response.content
        
        # Limpiar respuesta
        json_match = re.search(r'\{.*\}', contenido, re.DOTALL)
        if json_match:
            estructura = json.loads(json_match.group(0))
        else:
            estructura = json.loads(contenido)
        
        archivos = estructura.get("archivos", archivos_por_defecto)
        tipo_proyecto = estructura.get("tipo_proyecto", "landing_page")
        
    except Exception as e:
        print(f"   ⚠️ Error en arquitecto: {e}, usando estructura por defecto")
        archivos = archivos_por_defecto
        tipo_proyecto = "landing_page"
    
    progreso.total_archivos = len(archivos)
    
    # CORREGIDO: La línea correcta sin llave extra
    estructura_archivos = {}
    for a in archivos:
        estructura_archivos[a] = {"tipo": Path(a).suffix[1:] if Path(a).suffix else "html"}
    
    return {
        "tipo_proyecto": tipo_proyecto,
        "archivos_por_generar": archivos,
        "estructura_archivos": estructura_archivos
    }
# ============================================================================
# GENERADOR DE ARCHIVOS (con aprendizaje)
# ============================================================================

def generar_archivo_individual(ruta: str, descripcion: str, tipo: str) -> str:
    """Genera contenido con prompts MUY específicos para mejor calidad"""
    
    progreso.iniciar_generacion_archivo(ruta)
    time.sleep(0.3)
    
    # Contexto de aprendizaje
    contexto = sistema_aprendizaje.obtener_contexto_aprendizaje(descripcion)
    
    if ruta == "index.html":
        prompt = f"""Eres un diseñador web EXPERTO. Genera un HTML COMPLETO y PROFESIONAL.

DESCRIPCIÓN DEL PROYECTO:
{descripcion[:400]}

{contexto}

REQUISITO ABSOLUTAMENTE OBLIGATORIO:
1. Debes generar el HTML COMPLETO desde <!DOCTYPE html> hasta </html>
2. Usa la estructura SEMÁNTICA: <header>, <nav>, <main>, <section>, <footer>
3. Los estilos DEBEN estar enlazados con: <link rel="stylesheet" href="css/styles.css">
4. El JavaScript DEBE estar enlazado con: <script src="js/main.js"></script>
5. NO incluir CSS dentro del HTML (ni <style>)
6. NO incluir explicaciones, SOLO el código HTML
7. Diseño MODERNO con paleta de colores atractiva
8. Incluye clases CSS para todos los elementos

EJEMPLO DE ESTRUCTURA ESPERADA:
<nav class="navbar">...</nav>
<section class="hero">...</section>
<section class="products">...</section>
<section class="gallery">...</section>
<section class="contact">...</section>
<footer class="footer">...</footer>

Genera SOLO el HTML:"""

        response = model_manager.get("frontend").invoke(prompt)
        contenido = response.content
        
        # Limpiar y extraer solo HTML
        html_match = re.search(r'<!DOCTYPE html>.*?</html>', contenido, re.DOTALL)
        if html_match:
            contenido = html_match.group(0)
            
    elif ruta == "css/styles.css":
        prompt = f"""Eres un diseñador CSS EXPERTO. Genera CSS COMPLETO y PROFESIONAL.

DESCRIPCIÓN:
{descripcion[:300]}

{contexto}

REQUISITOS OBLIGATORIOS:
1. Diseño RESPONSIVE con media queries (mobile, tablet, desktop)
2. Usa CSS Grid y/o Flexbox para layouts
3. Variables CSS para colores (paleta armoniosa)
4. Efectos HOVER en botones y cards
5. Animaciones suaves (transitions)
6. Tipografía moderna (Google Fonts)
7. Código BIEN COMENTADO
8. NO incluir explicaciones, SOLO CSS

ESTILOS QUE DEBES INCLUIR:
- Navbar: fija, fondo blanco, sombra
- Hero: gradiente, texto centrado, CTA button
- Productos: grid de cards con imágenes/imagenes
- Galería: grid responsivo
- Contacto: formulario con estilos modernos
- Footer: fondo oscuro, texto centrado

Genera SOLO el CSS:"""

        response = model_manager.get("frontend").invoke(prompt)
        contenido = response.content
        
    elif ruta == "js/main.js":
        prompt = f"""Genera JavaScript INTERACTIVO para:

{descripcion[:300]}

REQUISITOS:
1. Smooth scroll para navegación (querySelectorAll + scrollIntoView)
2. Validación de formulario (nombre, email, mensaje no vacíos)
3. Menú hamburguesa para móvil (toggle class)
4. Animaciones al hacer scroll (IntersectionObserver)
5. Efecto de carga suave (fade-in)
6. NO jQuery, solo Vanilla JS
7. Código dentro de DOMContentLoaded

Genera SOLO el JavaScript:"""

        response = model_manager.get("frontend").invoke(prompt)
        contenido = response.content
        
    elif ruta == "README.md":
        prompt = f"""Genera README.md profesional para:
{descripcion[:300]}

Incluye: título, descripción, tecnologías (HTML5, CSS3, JS), instalación, uso, estructura del proyecto, capturas sugeridas.

Genera SOLO markdown:"""
        
        response = model_manager.get("frontend").invoke(prompt)
        contenido = response.content
    
    else:
        contenido = f"# {ruta}\n\n{descripcion}"
    
    # Validar contenido mínimo
    if not contenido or len(contenido.strip()) < 100:
        print(f"   ⚠️ Contenido muy corto, usando plantilla mejorada")
        contenido = obtener_plantilla_respaldo_mejorada(ruta, descripcion)
    
    preview = contenido[:100].replace('\n', ' ')
    progreso.completar_archivo(ruta, len(contenido), preview)
    # Validar contenido mínimo y calidad
    if not contenido or len(contenido.strip()) < 100:
        print(f"   ⚠️ Contenido muy corto, usando plantilla mejorada")
        contenido = obtener_plantilla_respaldo_mejorada(ruta, descripcion)
    
    # ===== NUEVO: Validación específica para CSS =====
    if ruta == "css/styles.css":
        # Verificar que el CSS tenga colores y responsive
        if ":root" not in contenido or "media" not in contenido:
            print(f"   🎨 Mejorando CSS con colores y responsive...")
            contenido = obtener_plantilla_respaldo_mejorada(ruta, descripcion)
    
    if ruta == "index.html":
        # Verificar que tenga enlaces correctos
        if "css/styles.css" not in contenido:
            print(f"   🔧 Corrigiendo enlace a CSS...")
            contenido = contenido.replace('</head>', '<link rel="stylesheet" href="css/styles.css">\n</head>')
    
    # ================================================
    
    preview = contenido[:100].replace('\n', ' ')
    progreso.completar_archivo(ruta, len(contenido), preview)
    
    return contenido

def obtener_plantilla_respaldo_mejorada(ruta: str, descripcion: str) -> str:
    """Plantillas de alta calidad para respaldo"""
    
    if ruta == "index.html":
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{descripcion[:40]} | Artesanal</title>
    <link rel="stylesheet" href="css/styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <div class="logo">🥖 {descripcion[:25]}</div>
            <ul class="nav-links">
                <li><a href="#inicio">Inicio</a></li>
                <li><a href="#productos">Productos</a></li>
                <li><a href="#galeria">Galería</a></li>
                <li><a href="#contacto">Contacto</a></li>
            </ul>
            <button class="menu-toggle">☰</button>
        </div>
    </nav>

    <section id="inicio" class="hero">
        <div class="container">
            <h1>{descripcion[:50]}</h1>
            <p>{descripcion[:150]}</p>
            <a href="#productos" class="btn">Ver Productos →</a>
        </div>
    </section>

    <section id="productos" class="productos">
        <div class="container">
            <h2>Nuestros Productos</h2>
            <div class="productos-grid">
                <div class="card">
                    <div class="card-icon">🥖</div>
                    <h3>Pan de Masa Madre</h3>
                    <p>Fermentación natural, crujiente por fuera, esponjoso por dentro</p>
                </div>
                <div class="card">
                    <div class="card-icon">🍞</div>
                    <h3>Pan Integral</h3>
                    <p>100% harina integral, rico en fibra y nutrientes</p>
                </div>
                <div class="card">
                    <div class="card-icon">🥐</div>
                    <h3>Facturas Artesanales</h3>
                    <p>Medialunas, vigilantes y más, hechos a mano</p>
                </div>
                <div class="card">
                    <div class="card-icon">🥨</div>
                    <h3>Pan de Campo</h3>
                    <p>Receta tradicional, ideal para acompañar comidas</p>
                </div>
            </div>
        </div>
    </section>

    <section id="galeria" class="galeria">
        <div class="container">
            <h2>Galería</h2>
            <div class="galeria-grid">
                <div class="galeria-item">🍞 Panes recién horneados</div>
                <div class="galeria-item">🥐 Facturas artesanales</div>
                <div class="galeria-item">🥖 El proceso de amasado</div>
                <div class="galeria-item">🔥 Horno de barro</div>
            </div>
        </div>
    </section>

    <section id="contacto" class="contacto">
        <div class="container">
            <h2>Contacto</h2>
            <form id="contactForm">
                <input type="text" placeholder="Nombre completo" required>
                <input type="email" placeholder="Correo electrónico" required>
                <textarea placeholder="Mensaje" rows="4" required></textarea>
                <button type="submit">Enviar Mensaje</button>
            </form>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 Panadería Artesanal. Todos los derechos reservados.</p>
            <p>📍 Encuéntranos en [Dirección] | 📞 (123) 456-7890</p>
        </div>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>"""
    
    elif ruta == "css/styles.css":
        return """/* ========================================
   VARIABLES GLOBALES
   ======================================== */
:root {
    --primary: #8B4513;
    --primary-dark: #5C2E0B;
    --secondary: #D2691E;
    --accent: #FFD700;
    --light: #FAF8F5;
    --dark: #2C1810;
    --gray: #666;
    --white: #FFFFFF;
    --shadow: 0 5px 20px rgba(0,0,0,0.1);
    --transition: all 0.3s ease;
}

/* ========================================
   RESET Y BASE
   ======================================== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Poppins', Arial, sans-serif;
    line-height: 1.6;
    color: var(--dark);
    background: var(--light);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* ========================================
   NAVBAR
   ======================================== */
.navbar {
    background: var(--white);
    box-shadow: var(--shadow);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
    transition: var(--transition);
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 20px;
}

.logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary);
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-links a {
    text-decoration: none;
    color: var(--dark);
    font-weight: 500;
    transition: var(--transition);
}

.nav-links a:hover {
    color: var(--primary);
}

.menu-toggle {
    display: none;
    background: none;
    border: none;
    font-size: 1.8rem;
    cursor: pointer;
    color: var(--primary);
}

/* ========================================
   HERO SECTION
   ======================================== */
.hero {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: var(--white);
    text-align: center;
    padding: 180px 0 120px;
    margin-top: 60px;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    animation: fadeInUp 0.8s ease;
}

.hero p {
    font-size: 1.2rem;
    max-width: 600px;
    margin: 0 auto;
    opacity: 0.95;
}

.btn {
    display: inline-block;
    background: var(--white);
    color: var(--primary);
    padding: 12px 30px;
    border-radius: 30px;
    text-decoration: none;
    font-weight: 600;
    margin-top: 2rem;
    transition: var(--transition);
}

.btn:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow);
}

/* ========================================
   PRODUCTOS
   ======================================== */
.productos {
    padding: 80px 0;
    background: var(--white);
}

.productos h2, .galeria h2, .contacto h2 {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: var(--primary);
}

.productos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
}

.card {
    background: var(--light);
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    transition: var(--transition);
    cursor: pointer;
}

.card:hover {
    transform: translateY(-10px);
    box-shadow: var(--shadow);
}

.card-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.card h3 {
    color: var(--primary);
    margin-bottom: 1rem;
}

/* ========================================
   GALERÍA
   ======================================== */
.galeria {
    padding: 80px 0;
    background: var(--light);
}

.galeria-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.galeria-item {
    background: var(--white);
    padding: 3rem;
    text-align: center;
    border-radius: 10px;
    font-size: 2rem;
    transition: var(--transition);
    cursor: pointer;
}

.galeria-item:hover {
    transform: scale(1.05);
    box-shadow: var(--shadow);
}

/* ========================================
   CONTACTO
   ======================================== */
.contacto {
    padding: 80px 0;
    background: var(--white);
}

form {
    max-width: 600px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

input, textarea {
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-family: inherit;
    font-size: 1rem;
    transition: var(--transition);
}

input:focus, textarea:focus {
    outline: none;
    border-color: var(--primary);
}

button[type="submit"] {
    background: var(--primary);
    color: var(--white);
    border: none;
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: var(--transition);
}

button[type="submit"]:hover {
    background: var(--primary-dark);
    transform: translateY(-2px);
}

/* ========================================
   FOOTER
   ======================================== */
.footer {
    background: var(--dark);
    color: var(--white);
    text-align: center;
    padding: 2rem 0;
}

/* ========================================
   ANIMACIONES
   ======================================== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* ========================================
   RESPONSIVE
   ======================================== */
@media (max-width: 768px) {
    .nav-links {
        display: none;
        position: absolute;
        top: 70px;
        left: 0;
        width: 100%;
        background: var(--white);
        flex-direction: column;
        padding: 1rem;
        box-shadow: var(--shadow);
    }
    
    .nav-links.active {
        display: flex;
    }
    
    .menu-toggle {
        display: block;
    }
    
    .hero h1 {
        font-size: 2rem;
    }
    
    .hero {
        padding: 150px 0 80px;
    }
    
    .productos h2, .galeria h2, .contacto h2 {
        font-size: 2rem;
    }
}

@media (max-width: 480px) {
    .productos-grid {
        grid-template-columns: 1fr;
    }
    
    .galeria-grid {
        grid-template-columns: 1fr;
    }
    
    .hero h1 {
        font-size: 1.5rem;
    }
}"""
    
    elif ruta == "js/main.js":
        return """// ========================================
// SCRIPT PRINCIPAL
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Sitio web cargado correctamente');
    
    // ========================================
    // SMOOTH SCROLL
    // ========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        });
    });
    
    // ========================================
    // MENÚ HAMBURGUESA
    // ========================================
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
    
    // ========================================
    // FORMULARIO DE CONTACTO
    // ========================================
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const nombre = this.querySelector('input[type="text"]').value;
            const email = this.querySelector('input[type="email"]').value;
            const mensaje = this.querySelector('textarea').value;
            
            if (!nombre || !email || !mensaje) {
                alert('❌ Por favor, completa todos los campos');
                return;
            }
            
            if (!email.includes('@') || !email.includes('.')) {
                alert('❌ Por favor, ingresa un email válido');
                return;
            }
            
            alert('✅ ¡Mensaje enviado! Gracias por contactarnos. Pronto recibirás respuesta.');
            form.reset();
        });
    }
    
    // ========================================
    // ANIMACIONES AL HACER SCROLL
    // ========================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .galeria-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });
});"""
    
    else:
        return f"# {ruta}\n\n{descripcion}"
    
def obtener_respaldo(ruta: str, descripcion: str) -> str:
    """Plantillas de respaldo"""
    
    if ruta == "index.html":
        return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{descripcion[:40]}</title>
<link rel="stylesheet" href="css/styles.css">
</head>
<body>
<header><h1>{descripcion[:50]}</h1></header>
<main><p>Proyecto generado por Gemelo Digital</p></main>
<footer><p>&copy; 2024</p></footer>
<script src="js/main.js"></script>
</body>
</html>"""
    
    elif ruta == "css/styles.css":
        return """*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial;line-height:1.6;color:#333}
header{background:#8B4513;color:#fff;padding:2rem;text-align:center}
main{max-width:1200px;margin:0 auto;padding:2rem}
footer{background:#333;color:#fff;text-align:center;padding:1rem}"""
    
    elif ruta == "js/main.js":
        return """document.addEventListener('DOMContentLoaded',()=>{console.log('Listo')})"""
    
    else:
        return f"# {ruta}\n\n{descripcion}"

# ============================================================================
# AGENTE GENERADOR PROGRESIVO
# ============================================================================

def agente_generador_progresivo(state: EstadoProyecto):
    """Genera archivos UNO POR UNO"""
    
    archivos_generados = state.get("archivos_generados", {}).copy()
    archivos_por_generar = state.get("archivos_por_generar", [])
    
    if not archivos_por_generar:
        return {"archivos_generados": archivos_generados}
    
    # Encontrar siguiente archivo
    archivo_actual = None
    for archivo in archivos_por_generar:
        if archivo not in archivos_generados:
            archivo_actual = archivo
            break
    
    if archivo_actual is None:
        return {"archivos_generados": archivos_generados}
    
    print(f"\n   📝 Generando {len(archivos_generados)+1}/{len(archivos_por_generar)}: {archivo_actual}")
    
    try:
        contenido = generar_archivo_individual(
            archivo_actual,
            state["input_usuario"],
            state.get("tipo_proyecto", "landing_page")
        )
        archivos_generados[archivo_actual] = contenido
    except Exception as e:
        print(f"   ❌ Error: {e}")
        archivos_generados[archivo_actual] = f"<!-- Error: {e} -->"
    
    return {"archivos_generados": archivos_generados}

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def crear_proyecto_con_progreso(texto_libre: str = None, ruta_documento: str = None) -> Dict:
    """Crea un proyecto con aprendizaje continuo y medición de tiempos"""
    
    # Iniciar medición total
    medidor.iniciar_total()
    
    nombre = texto_libre[:50] + "..." if texto_libre and len(texto_libre) > 50 else "Nuevo Proyecto"
    progreso.iniciar_proyecto(nombre)
    
    # ===== FASE 1: Procesar input =====
    medidor.iniciar_fase("1. Procesamiento de input")
    contenido_input = procesar_input(texto_libre=texto_libre, ruta_documento=ruta_documento)
    medidor.finalizar_fase()
    
    if not contenido_input:
        return {"error": "Input vacío"}
    
    # Estado inicial
    estado: EstadoProyecto = {
        "input_usuario": contenido_input,
        "tipo_proyecto": "",
        "estructura_archivos": {},
        "archivos_generados": {},
        "archivos_por_generar": [],
        "errores": [],
        "revision_aprobada": False,
        "logs": []
    }
    
    # ===== FASE 2: Arquitecto (definir estructura) =====
    medidor.iniciar_fase("2. Arquitecto (definir estructura)")
    resultado_arquitecto = agente_arquitecto(estado)
    medidor.finalizar_fase()
    
    estado.update({
        "tipo_proyecto": resultado_arquitecto.get("tipo_proyecto", "landing_page"),
        "archivos_por_generar": resultado_arquitecto.get("archivos_por_generar", []),
        "estructura_archivos": resultado_arquitecto.get("estructura_archivos", {})
    })
    
    if not estado.get("archivos_por_generar"):
        return {"error": "No hay archivos definidos"}
    
    print(f"\n📋 Archivos a generar: {estado['archivos_por_generar']}")
    
    # ===== FASE 3: Generación de archivos (uno por uno) =====
    medidor.iniciar_fase("3. Generación de archivos")
    progreso.actualizar_etapa("🎨 Generando archivos", "Creando cada archivo...")
    
    max_iter = len(estado["archivos_por_generar"]) * 2
    iteracion = 0
    
    # Sub-fases para cada archivo
    tiempos_archivos = {}
    
    while len(estado.get("archivos_generados", {})) < len(estado["archivos_por_generar"]):
        iteracion += 1
        if iteracion > max_iter:
            break
        
        # Medir tiempo de cada archivo individualmente
        archivos_pendientes = [a for a in estado["archivos_por_generar"] if a not in estado.get("archivos_generados", {})]
        if archivos_pendientes:
            archivo_actual = archivos_pendientes[0]
            inicio_archivo = time.time()
            
            resultado = agente_generador_progresivo(estado)
            nuevos = resultado.get("archivos_generados", {})
            if nuevos:
                estado["archivos_generados"].update(nuevos)
            
            tiempo_archivo = time.time() - inicio_archivo
            tiempos_archivos[archivo_actual] = tiempo_archivo
            print(f"      ⏱️  Tiempo: {tiempo_archivo:.1f}s")
        
        completados = len(estado["archivos_generados"])
        total = len(estado["archivos_por_generar"])
        print(f"   📊 Progreso: {completados}/{total}")
        time.sleep(0.3)
    
    medidor.finalizar_fase()
    
    # Mostrar tiempos individuales por archivo
    print(f"\n📄 TIEMPOS POR ARCHIVO:")
    for archivo, tiempo in tiempos_archivos.items():
        print(f"   {archivo:20} : {tiempo:.1f} segundos")
    
    # ===== FASE 4: Guardar en disco =====
     # ===== FASE 4: Guardar en disco =====
    medidor.iniciar_fase("4. Guardado en disco")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Usar config si está disponible, sino usar CONFIG
    if CONFIG_LOADED:
        ruta_proyecto = config.proyectos_dir / f"proyecto_{timestamp}"
    else:
        ruta_proyecto = Path(CONFIG["paths"]["proyectos"]) / f"proyecto_{timestamp}"
    
    ruta_proyecto.mkdir(parents=True, exist_ok=True)
    for ruta, contenido in estado["archivos_generados"].items():
        archivo = ruta_proyecto / ruta
        archivo.parent.mkdir(parents=True, exist_ok=True)
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"   💾 Guardado: {ruta}")
    
    medidor.finalizar_fase()
    
    # ===== FASE 5: Aprendizaje =====
    medidor.iniciar_fase("5. Aprendizaje (guardar ejemplo)")
    sistema_aprendizaje.guardar_ejemplo(estado, ruta_proyecto)
    medidor.finalizar_fase()
    
    # Finalizar medición total
    tiempo_total = medidor.finalizar_total()
    
    # Mostrar resumen detallado
    medidor.mostrar_resumen_tiempos()
    
    # Resumen del proyecto
    print("\n" + "="*60)
    print("🎉 PROYECTO COMPLETADO")
    print("="*60)
    
    progreso.mostrar_resumen(estado["archivos_generados"])
    print(f"\n📁 Ubicación: {ruta_proyecto}")
    print(f"\n💡 Para ver tu proyecto:")
    print(f"   cd {ruta_proyecto}")
    print(f"   python -m http.server 8000")
    
    return {
        "success": True, 
        "ruta": str(ruta_proyecto), 
        "archivos": list(estado["archivos_generados"].keys()),
        "tiempos": medidor.tiempos,
        "tiempo_total": tiempo_total,
        "tiempos_archivos": tiempos_archivos
    }

def guardar_estadisticas(resultado: Dict):
    """Guarda las estadísticas de tiempo en un archivo para análisis"""
    
    # Usar config si está disponible, sino usar CONFIG
    if CONFIG_LOADED:
        stats_file = config.aprendizaje_dir / "estadisticas_tiempos.json"
    else:
        stats_file = Path(CONFIG["paths"]["aprendizaje"]) / "estadisticas_tiempos.json"
    
    # Cargar estadísticas existentes
    estadisticas = []
    if stats_file.exists():
        with open(stats_file, 'r') as f:
            estadisticas = json.load(f)
    
    # Agregar nueva ejecución
    estadisticas.append({
        "fecha": datetime.now().isoformat(),
        "tiempo_total": resultado.get("tiempo_total", 0),
        "tiempos_por_fase": resultado.get("tiempos", {}),
        "tiempos_por_archivo": resultado.get("tiempos_archivos", {}),
        "total_archivos": len(resultado.get("archivos", []))
    })
    
    # Guardar solo las últimas 20 ejecuciones
    with open(stats_file, 'w') as f:
        json.dump(estadisticas[-20:], f, indent=2)
    
    # Calcular y mostrar promedio
    if len(estadisticas) > 1:
        tiempos_anteriores = [e["tiempo_total"] for e in estadisticas[:-1]]
        promedio = sum(tiempos_anteriores) / len(tiempos_anteriores)
        mejora = ((promedio - resultado["tiempo_total"]) / promedio) * 100
        print(f"\n📊 VS PROMEDIO ANTERIOR: {promedio:.1f}s → {resultado['tiempo_total']:.1f}s")
        if mejora > 0:
            print(f"   🚀 Mejora del {mejora:.1f}% (más rápido)")
        elif mejora < 0:
            print(f"   ⚠️ {mejora:.1f}% más lento que el promedio")
# ============================================================================
# DEMO
# ============================================================================

def demo():
    ejemplo = """
    Landing page para panadería artesanal 'Pan Casero'
    Con hero section, menú de productos, galería y formulario de contacto
    """
    resultado = crear_proyecto_con_progreso(texto_libre=ejemplo)
    if resultado.get("success"):
        print(f"\n✨ Proyecto en: {resultado['ruta']}")
        guardar_estadisticas(resultado)

if __name__ == "__main__":
    demo()