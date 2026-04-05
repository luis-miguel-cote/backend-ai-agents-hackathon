"""
Agente de requerimientos: análisis estructurado con LLM configurable y Pydantic.
"""

def analyze_requirements_google(user_request: str):
    """Analiza requerimientos usando el LLM configurado en .env y Pydantic."""
    from core.llm import llamar_llm_structured
    from langchain_core.prompts import ChatPromptTemplate
    from pydantic import BaseModel, Field
    from typing import List, Literal

    class RequirementItem(BaseModel):
        code: str
        description: str
        priority: Literal["alta", "media", "baja"]
        rationale: str

    class RequirementsAnalysis(BaseModel):
        title: str
        project_summary: str
        functional_requirements: List[RequirementItem] = []
        non_functional_requirements: List[RequirementItem] = []
        assumptions: List[str] = []
        open_questions: List[str] = []
        risks: List[str] = []
        recommended_next_step: str

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
Eres un analista de requerimientos senior con mas de 15 años de experiencia en desarrollo de software.
A partir de la petición del usuario:
1. Genera requerimientos funcionales detallados:
   - Deben ser específicos, verificables y medibles.
   - Incluye condiciones, comportamiento esperado y posibles excepciones.
2. Genera requerimientos no funcionales:
   - Define métricas claras (ej: tiempos, disponibilidad, seguridad).
   - Evita generalidades como “rápido” o “responsive” sin contexto.
3. Diferencia claramente:
   - requerimientos reales
   - supuestos
   - preguntas abiertas
NOTA: Diferencia estrictamente entre:
1. Requerimientos explícitos del usuario
2. Supuestos (si algo no fue mencionado directamente)
3. Funcionalidades opcionales
NUNCA conviertas un supuesto en requerimiento obligatorio.
Si una funcionalidad no está explícita, debe ir en:
- supuestos, o
- preguntas abiertas
4. No generes requerimientos genéricos.
5. No inventes funcionalidades sin justificarlas en el rationale.
6. Usa lenguaje técnico claro.
7. Para cada requerimiento incluye:
   - qué hace
   - bajo qué condiciones
   - cómo se valida
El resultado debe ser útil para iniciar un desarrollo real.
"""
        ),
        ("human", "Petición del usuario:\n{user_request}")
    ])

    llm_structured = llamar_llm_structured(prompt, RequirementsAnalysis, temperature=0, agente="reqs")
    chain = prompt | llm_structured
    return chain.invoke({"user_request": user_request})


def _construir_resultado(analisis) -> dict:
    """Construye el dict de resultado a partir del analisis Pydantic."""
    resumen_partes = [f"Proyecto: {analisis.title}", f"Resumen: {analisis.project_summary}"]

    if analisis.functional_requirements:
        resumen_partes.append("\nRequerimientos Funcionales:")
        for req in analisis.functional_requirements:
            resumen_partes.append(f"  - [{req.priority.upper()}] {req.code}: {req.description}")

    if analisis.non_functional_requirements:
        resumen_partes.append("\nRequerimientos No Funcionales:")
        for req in analisis.non_functional_requirements:
            resumen_partes.append(f"  - [{req.priority.upper()}] {req.code}: {req.description}")

    if analisis.assumptions:
        resumen_partes.append(f"\nSupuestos: {', '.join(analisis.assumptions[:5])}")

    if analisis.risks:
        resumen_partes.append(f"Riesgos: {', '.join(analisis.risks[:3])}")

    return {
        "titulo": analisis.title,
        "resumen": analisis.project_summary,
        "resumen_completo": "\n".join(resumen_partes),
        "total_funcionales": len(analisis.functional_requirements),
        "total_no_funcionales": len(analisis.non_functional_requirements),
        "preguntas_abiertas": analisis.open_questions,
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
