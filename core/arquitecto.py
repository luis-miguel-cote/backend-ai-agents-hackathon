import re
import json
from core.progreso import progreso


def _llamar_llm(prompt: str) -> str:
    """Llama al LLM (Google GenAI) y retorna el texto de respuesta."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    response = llm.invoke(prompt)
    return response.content


def agente_arquitecto(state, sistema_aprendizaje):
    """Define la estructura de archivos APRENDIENDO de proyectos anteriores"""
    progreso.actualizar_etapa("🏗️ Arquitecto", "Definiendo estructura...")
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
        contenido = _llamar_llm(prompt)
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
    return {
        "tipo_proyecto": tipo_proyecto,
        "archivos_por_generar": archivos,
        "estructura_archivos": {a: {"tipo": a.split('.')[-1] if '.' in a else "html"} for a in archivos}
    }
