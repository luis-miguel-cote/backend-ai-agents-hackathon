"""
Agente de requerimientos: análisis estructurado usando Google GenAI y Pydantic.
"""

def analyze_requirements_google(user_request: str):
    """Analiza requerimientos usando Google GenAI y Pydantic."""
    from langchain_google_genai import ChatGoogleGenerativeAI
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

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    structured_llm = llm.with_structured_output(RequirementsAnalysis, method="json_schema")
    chain = prompt | structured_llm
    return chain.invoke({"user_request": user_request})
