"""
Modulo centralizado para llamadas al LLM.
Configuracion desde .env:
  LLM_PROVIDER / LLM_MODEL  -> default para todos los agentes
  REQS_PROVIDER / REQS_MODEL -> override para requerimientos
  ARQUITECTO_PROVIDER / ARQUITECTO_MODEL -> override para arquitecto
  GENERADOR_PROVIDER / GENERADOR_MODEL -> override para generador
"""

import os


def _resolver_config(agente: str = None) -> tuple:
    """Resuelve provider y model: primero busca AGENTE_PROVIDER/MODEL, si no usa LLM_PROVIDER/MODEL."""
    if agente:
        prefix = agente.upper()
        provider = os.environ.get(f"{prefix}_PROVIDER", "").strip()
        model = os.environ.get(f"{prefix}_MODEL", "").strip()
        if provider and model:
            return provider.lower(), model

    provider = os.environ.get("LLM_PROVIDER", "google").lower()
    model = os.environ.get("LLM_MODEL", "gemini-2.5-flash-lite")
    return provider, model


def llamar_llm(prompt: str, temperature: float = 0.7, agente: str = None) -> str:
    """Llama al LLM configurado en .env. Retorna None si LLM no disponible (para fallback)."""
    provider, model = _resolver_config(agente)

    try:
        if provider == "google":
            return _llamar_google(prompt, model, temperature)
        elif provider == "deepseek":
            return _llamar_deepseek(prompt, model, temperature)
        elif provider == "anthropic":
            return _llamar_anthropic(prompt, model, temperature)
        elif provider == "ollama":
            return _llamar_ollama(prompt, model, temperature)
        else:
            raise ValueError(f"LLM provider no soportado: {provider}")
    except Exception as e:
        print(f"   WARNING: Error LLM: {e}. Retornando None.")
        return None



import json

def llamar_llm_structured(prompt, model_schema, temperature: float = 0, agente: str = None):
    """
    Llama al LLM con salida estructurada (Pydantic) si el proveedor lo soporta.
    Si no, usa el LLM normal y parsea el JSON manualmente.
    """
    provider, model = _resolver_config(agente)

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
        return llm.with_structured_output(model_schema, method="json_schema")
    else:
        # Llama al LLM normal y parsea el JSON manualmente
        raw_response = llamar_llm(prompt, temperature=temperature, agente=agente)
        if not raw_response:
            raise RuntimeError(f"No se pudo obtener respuesta del LLM para agente {agente}")
        # Intentar extraer JSON del texto
        try:
            # Buscar el primer bloque JSON en la respuesta
            start = raw_response.find('{')
            end = raw_response.rfind('}')
            if start == -1 or end == -1:
                raise ValueError("No se encontró bloque JSON en la respuesta del LLM")
            json_str = raw_response[start:end+1]
            data = json.loads(json_str)
            # Validar con el schema Pydantic
            return model_schema.parse_obj(data)
        except Exception as e:
            raise RuntimeError(f"Error al parsear la respuesta del LLM como JSON estructurado: {e}\nRespuesta LLM:\n{raw_response}")


def _llamar_google(prompt: str, model: str, temperature: float) -> str:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
        if not api_key:
            print("   WARNING: GOOGLE_API_KEY vacia. Retornando None para usar fallback.")
            return None
        llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"   WARNING: Error en Google Gemini: {e}")
        return None


def _llamar_deepseek(prompt: str, model: str, temperature: float) -> str:
    import requests
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY debe estar definido en .env")

    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 4096,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _llamar_anthropic(prompt: str, model: str, temperature: float) -> str:
    import anthropic
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("   WARNING: ANTHROPIC_API_KEY vacía. Retornando None para usar fallback.")
        return None
    client = anthropic.Anthropic(api_key=api_key)
    # Anthropic espera mensajes como lista de dicts con 'role' y 'content'
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    # Claude responde con response.content (lista de bloques), o response['content']
    # Buscamos el texto plano
    if hasattr(response, "content") and response.content:
        # Claude 3: content es lista de bloques, buscamos tipo 'text'
        for block in response.content:
            if block.type == "text":
                return block.text
        # Si no hay bloques tipo texto, devolvemos el primer bloque como string
        return str(response.content[0])
    # Fallback: intentamos acceder como dict
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    return ""


def _llamar_ollama(prompt: str, model: str, temperature: float) -> str:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model=model, temperature=temperature)
    response = llm.invoke(prompt)
    return response.content
