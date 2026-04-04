# DeepSeek (modelo chino)
def analizar_con_deepseek(prompt: str) -> str:
    import requests
    api_url = os.environ.get("DEEPSEEK_API_URL")
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_url or not api_key:
        raise ValueError("DEEPSEEK_API_URL y DEEPSEEK_API_KEY deben estar definidos en el entorno")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"prompt": prompt, "max_tokens": 2048}
    response = requests.post(api_url, json=data, headers=headers, timeout=60)
    response.raise_for_status()
    result = response.json()
    # Ajusta la clave según la respuesta real de la API de DeepSeek
    return result.get("result") or result.get("text") or str(result)
"""
Módulo de proveedores de IA para análisis y generación de requerimientos.
Permite seleccionar entre Anthropic (Claude), Google GenAI, Webhook externo (N8N) u Ollama local.
"""

import os
import requests


# Anthropic (Claude)
def analizar_con_anthropic(prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-opus-20240229",  # O el modelo que prefieras
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text if response.content else ""

# Google GenAI
def analizar_con_google(prompt: str) -> str:
    from langchain_google_genai import ChatGoogleGenerativeAI
    chat = ChatGoogleGenerativeAI(model="gemini-pro")
    return chat.invoke(prompt).content

# Webhook externo (N8N)
def analizar_con_webhook(prompt: str) -> str:
    webhook_url = os.environ["N8N_WEBHOOK_URL"]
    response = requests.post(webhook_url, json={"prompt": prompt}, timeout=120)
    response.raise_for_status()
    return response.json().get("result", "")

# Ollama local (compatibilidad)
def analizar_con_ollama(prompt: str) -> str:
    from langchain_ollama import ChatOllama
    chat = ChatOllama(model=os.environ["MODEL_QA"])
    return chat.invoke(prompt).content

# Función principal de selección de proveedor
def analizar_codigo(prompt: str, provider: str = None) -> str:
    provider = provider or os.environ.get("QA_PROVIDER", "ollama")
    if provider == "anthropic":
        return analizar_con_anthropic(prompt)
    elif provider == "google":
        return analizar_con_google(prompt)
    elif provider == "webhook":
        return analizar_con_webhook(prompt)
    elif provider == "deepseek":
        return analizar_con_deepseek(prompt)
    else:
        return analizar_con_ollama(prompt)
