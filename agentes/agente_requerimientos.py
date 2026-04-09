"""
Agente de requerimientos: análisis estructurado con LLM configurable y Pydantic.
"""

def _generate_contextual_analysis(user_request: str):
    """Genera análisis contextualizado cuando el LLM no está disponible."""
    from pydantic import BaseModel, Field
    from typing import List, Literal, Optional
    
    class RequirementItem(BaseModel):
        code: str
        description: str
        priority: Literal["alta", "media", "baja"]
        rationale: str

    class RequirementsAnalysis(BaseModel):
        title: str
        project_summary: str
        type_of_web: str
        problem_questions: List[str] = []
        actors: List[str] = []
        analysis_questions: List[str] = []
        functional_requirements: List[RequirementItem] = []
        non_functional_requirements: List[RequirementItem] = []
        final_questions: List[str] = []
        assumptions: List[str] = []
        open_questions: List[str] = []
        risks: List[str] = []
        recommended_next_step: str
    
    # Detectar palabras clave para personalizar preguntas
    request_lower = user_request.lower()
    keywords = {
        'tienda': 'E-comerce',
        'ecommerce': 'E-comerce',
        'blog': 'Blogs',
        'curso': 'E-learnings',
        'educaci': 'E-learnings',
        'red social': 'Redes sociales',
        'portafolio': 'Sitios web corporativos',
        'landing': 'Landing pages',
        'admin': 'Aplicaciones web',
        'dashboard': 'Aplicaciones web',
        'app': 'Aplicaciones web',
        'video': 'Sitios web de entretenimiento',
        'contenido': 'Dinámicas',
        'información': 'Estáticas',
    }
    
    web_type = 'Dinámicas'
    for keyword, wtype in keywords.items():
        if keyword in request_lower:
            web_type = wtype
            break
    
    # Generar preguntas contextualizadas según el tipo detectado
    if web_type == 'E-comerce':
        specific_questions = [
            "¿Qué tipos de productos o servicios venderás en la tienda?",
            "¿Cuál es tu modelo de negocio: B2C, B2B, marketplace?",
            "¿Necesitas integración con pasarelas de pago (Stripe, PayPal)?",
            "¿Cuántos productos manejarás inicialmente?",
        ]
    elif web_type == 'Blogs':
        specific_questions = [
            "¿Cuál es el tema principal del blog?",
            "¿Con qué frecuencia publicarás contenido?",
            "¿Necesitas sistema de comentarios y categorías?",
            "¿Requieres integración con redes sociales?",
        ]
    elif web_type == 'E-learnings':
        specific_questions = [
            "¿Qué cursos o módulos educativos ofrecerás?",
            "¿Necesitas certificados o diplomas digitales?",
            "¿Cómo será el sistema de evaluación?",
            "¿Qué tipo de contenido: video, texto, quizzes?",
        ]
    elif web_type == 'Aplicaciones web':
        specific_questions = [
            "¿Cuál es la funcionalidad principal de la aplicación?",
            "¿Requiere registro y autenticación de usuarios?",
            "¿Necesita integración con otras APIs o servicios?",
            "¿Cuál es el volumen de usuarios esperado?",
        ]
    elif web_type == 'Redes sociales':
        specific_questions = [
            "¿Cuál será el tipo de contenido principal?",
            "¿Necesitas sistema de mensajería directa?",
            "¿Requerimientos de escalabilidad y tiempo real?",
            "¿Plan de moderación de contenido?",
        ]
    elif web_type == 'Landing pages':
        specific_questions = [
            "¿Cuál es el objetivo principal (ventas, leads, descarga)?",
            "¿Qué acción esperas que haga el usuario?",
            "¿Necesitas formulario de contacto o registro?",
            "¿Integración con herramientas de email marketing?",
        ]
    elif web_type == 'Sitios web de entretenimiento':
        specific_questions = [
            "¿Qué tipo de contenido multimedia ofrecerás?",
            "¿Necesitas sistema de streaming o solo reproducción?",
            "¿Requerimientos de CDN para distribución global?",
            "¿Plan de monetización (suscripción, ads)?",
        ]
    else:
        specific_questions = [
            "¿Cuál es el objetivo principal del sitio web?",
            "¿Qué información o funcionalidades serán prioritarias?",
            "¿Para qué tipo de usuarios se diseña?",
            "¿Hay integraciones o conexiones con otros sistemas?",
        ]
    
    return RequirementsAnalysis(
        title=f"Análisis de {web_type}",
        project_summary=user_request[:200],
        type_of_web=web_type,
        problem_questions=specific_questions[:3],
        actors=["Usuarios"],
        analysis_questions=[
            "¿Cuál es el alcance del proyecto?",
            "¿Cuáles son los requisitos de rendimiento?"
        ],
        functional_requirements=[],
        non_functional_requirements=[],
        final_questions=specific_questions[3:],
        assumptions=["Se asume una arquitectura estándar"],
        open_questions=specific_questions,
        risks=["Cambios de requerimientos"],
        recommended_next_step="Por favor responde las preguntas para obtener un análisis más detallado.",
    )


def analyze_requirements_google(user_request: str):
    """Analiza requerimientos usando el LLM configurado en .env y Pydantic."""
    from core.llm import llamar_llm
    from langchain_core.prompts import ChatPromptTemplate
    from pydantic import BaseModel, Field
    from typing import List, Literal, Optional
    import json

    class RequirementItem(BaseModel):
        code: str
        description: str
        priority: Literal["alta", "media", "baja"]
        rationale: str

    class RequirementsAnalysis(BaseModel):
        title: str
        project_summary: str
        type_of_web: str
        problem_questions: List[str] = []
        actors: List[str] = []
        analysis_questions: List[str] = []
        functional_requirements: List[RequirementItem] = []
        non_functional_requirements: List[RequirementItem] = []
        final_questions: List[str] = []
        assumptions: List[str] = []
        open_questions: List[str] = []
        risks: List[str] = []
        recommended_next_step: str

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
Eres un analista de requerimientos experto en soluciones web. Tu tarea es convertir cada solicitud del usuario en un análisis estructurado, concreto y distinto.

Instrucciones:
- Genera un JSON limpio y estructurado con el formato exacto pedido.
- Usa un lenguaje creativo, variado y profesional; evita repetir siempre el mismo estilo, la misma fórmula o las mismas preguntas.
- Analiza el contenido específico de la solicitud y ajusta cada sección al contexto real del proyecto.
- No uses preguntas genéricas estándar. Cada pregunta debe derivar directamente de los detalles del requerimiento.
- Identifica el tipo de proyecto web con una de estas categorías exactas:
  "Estáticas", "Dinámicas", "Híbridas", "Sitios web corporativos", "E-comerce", "Blogs", "E-learnings", "Sitios web de entretenimiento", "Landing pages", "Portales web", "Foros", "Wikis", "Redes sociales", "Aplicaciones web", "Sitios web de servicios (SaaS)".
- Si la solicitud ya contiene suficiente información, deja "final_questions" vacío.
- Si falta información fundamental, genera hasta 5 preguntas de clarificación muy específicas en "final_questions".
- Prioriza siempre la relevancia: cada pregunta debe ayudar a comprender mejor el alcance, los actores, la experiencia de usuario, las integraciones y las restricciones.

Formato obligatorio:
{
  "title": "...",
  "project_summary": "...",
  "type_of_web": "...",
  "problem_questions": ["..."],
  "actors": ["..."],
  "analysis_questions": ["..."],
  "functional_requirements": [{"code":"REQ-1","description":"...","priority":"alta","rationale":"..."}],
  "non_functional_requirements": [{"code":"NFR-1","description":"...","priority":"media","rationale":"..."}],
  "final_questions": ["..."],
  "assumptions": ["..."],
  "open_questions": ["..."],
  "risks": ["..."],
  "recommended_next_step": "..."
}

Crea:
- preguntas iniciales específicas y distintas, directamente orientadas al requerimiento.
- actores principales del sistema con nombres de roles claros.
- preguntas de análisis enfocadas en alcance, experiencia y datos.
- requerimientos funcionales y no funcionales relevantes al dominio del proyecto.
- razones claras para cada requerimiento.

No incluyas explicaciones adicionales fuera del JSON.
"""
        ),
        ("human", "Petición del usuario:\n{user_request}")
    ])

    # Usar llamar_llm para evitar problemas de serialización
    formatted_prompt = prompt.format(user_request=user_request)
    raw_response = llamar_llm(formatted_prompt, temperature=0.7, agente="reqs")
    
    if not raw_response:
        # Si el LLM no está disponible, generar análisis básico pero contextualizado
        return _generate_contextual_analysis(user_request)

    def _extract_json_block(text: str) -> Optional[str]:
        start = text.find('{')
        if start == -1:
            return None
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text[start:], start):
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i+1]
        return None

    def _extract_questions_from_text(text: str) -> List[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        questions = [line for line in lines if line.endswith('?')]
        return questions[:10]

    try:
        json_str = _extract_json_block(raw_response)
        if not json_str:
            raise ValueError("No se encontró bloque JSON en la respuesta")
        data = json.loads(json_str)
        return RequirementsAnalysis.parse_obj(data)
    except Exception as e:
        fallback_questions = _extract_questions_from_text(raw_response)
        if fallback_questions:
            return RequirementsAnalysis.parse_obj({
                "title": "Proyecto web",
                "project_summary": user_request[:200],
                "functional_requirements": [],
                "non_functional_requirements": [],
                "assumptions": [],
                "open_questions": fallback_questions,
                "risks": [],
                "recommended_next_step": "Responde las preguntas abiertas para completar el análisis.",
            })
        raise RuntimeError(f"Error al parsear respuesta del LLM: {e}\nRespuesta: {raw_response}")


def _construir_resultado(analisis) -> dict:
    """Construye el dict de resultado a partir del analisis Pydantic."""

    resumen_partes = [
        f"Proyecto: {analisis.title}",
        f"Resumen: {analisis.project_summary}",
        f"Tipo de página web: {getattr(analisis, 'type_of_web', 'N/A')}"
    ]

    if getattr(analisis, 'problem_questions', None):
        resumen_partes.append("\nPreguntas de definición del problema:")
        for q in analisis.problem_questions:
            resumen_partes.append(f"  - {q}")

    if getattr(analisis, 'actors', None):
        resumen_partes.append("\nActores identificados:")
        for a in analisis.actors:
            resumen_partes.append(f"  - {a}")

    if getattr(analisis, 'analysis_questions', None):
        resumen_partes.append("\nPreguntas de análisis:")
        for q in analisis.analysis_questions:
            resumen_partes.append(f"  - {q}")

    if getattr(analisis, 'functional_requirements', None):
        resumen_partes.append("\nRequerimientos Funcionales:")
        for req in analisis.functional_requirements:
            resumen_partes.append(f"  - [{req.priority.upper()}] {req.code}: {req.description}")

    if getattr(analisis, 'non_functional_requirements', None):
        resumen_partes.append("\nRequerimientos No Funcionales:")
        for req in analisis.non_functional_requirements:
            resumen_partes.append(f"  - [{req.priority.upper()}] {req.code}: {req.description}")

    if getattr(analisis, 'final_questions', None):
        resumen_partes.append("\nPreguntas aclaratorias finales:")
        for q in analisis.final_questions:
            resumen_partes.append(f"  - {q}")

    if getattr(analisis, 'assumptions', None):
        resumen_partes.append(f"\nSupuestos: {', '.join(analisis.assumptions[:5])}")

    if getattr(analisis, 'risks', None):
        resumen_partes.append(f"Riesgos: {', '.join(analisis.risks[:3])}")

    return {
        "titulo": analisis.title,
        "resumen": analisis.project_summary,
        "resumen_completo": "\n".join(resumen_partes),
        "total_funcionales": len(getattr(analisis, 'functional_requirements', [])),
        "total_no_funcionales": len(getattr(analisis, 'non_functional_requirements', [])),
        "preguntas_abiertas": getattr(analisis, 'open_questions', []),
        "siguiente_paso": analisis.recommended_next_step,
    }


def agente_requerimientos(input_usuario: str, max_rondas: int = 3) -> dict:
    """Analiza requerimientos con chat interactivo.

    Si el agente detecta preguntas abiertas, las presenta al usuario en terminal.
    El usuario responde y se re-analiza hasta que no queden preguntas
    o se alcance max_rondas. El usuario puede escribir 'continuar' para saltar.
    """
    contexto_acumulado = input_usuario

    for ronda in range(1, max_rondas + 1):
        print(f"\n   🔄 Analizando requerimientos (ronda {ronda})...")
        try:
            analisis = analyze_requirements_google(contexto_acumulado)
        except Exception as e:
            print(f"   ⚠️ Error en analisis de requerimientos: {e}")
            return {
                "titulo": "Proyecto web",
                "resumen": input_usuario[:200],
                "resumen_completo": input_usuario,
                "total_funcionales": 0,
                "total_no_funcionales": 0,
                "preguntas_abiertas": [],
                "siguiente_paso": "Continuar con la informacion disponible",
            }

        resultado = _construir_resultado(analisis)

        print(f"   📋 {resultado['titulo']}")
        print(f"   📌 Funcionales: {resultado['total_funcionales']}, No funcionales: {resultado['total_no_funcionales']}")

        # Si no hay preguntas abiertas, los requerimientos estan completos
        preguntas = analisis.open_questions
        if not preguntas:
            print("   ✅ Requerimientos completos, sin preguntas abiertas.")
            return resultado

        # Mostrar preguntas y pedir respuestas
        print(f"\n   ❓ El agente tiene {len(preguntas)} pregunta(s) para mejorar los requerimientos:")
        print("   (Escribe 'continuar' para seguir con lo que hay)\n")

        respuestas = []
        saltar = False
        for i, pregunta in enumerate(preguntas, 1):
            try:
                resp = input(f"   {i}. {pregunta}\n      > ").strip()
            except (KeyboardInterrupt, EOFError):
                saltar = True
                break

            if resp.lower() in ("continuar", "skip", "c", ""):
                saltar = True
                break
            respuestas.append(f"Pregunta: {pregunta}\nRespuesta: {resp}")

        if saltar or not respuestas:
            print("   ➡️  Continuando con los requerimientos actuales.")
            return resultado

        # Enriquecer contexto con las respuestas y re-analizar
        contexto_acumulado += "\n\n--- RESPUESTAS ADICIONALES DEL USUARIO ---\n" + "\n".join(respuestas)

    print("   ✅ Maximo de rondas alcanzado, continuando.")
    return resultado
