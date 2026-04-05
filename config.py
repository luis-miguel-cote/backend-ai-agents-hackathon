"""
Configuración del Gemelo Digital.
Usa variables de entorno. Incluye soporte para proveedores de IA en la nube.

Variables esperadas:
- OLLAMA_URL, OLLAMA_TIMEOUT, MODEL_ARQUITECTO, MODEL_FRONTEND, MODEL_QA, NUM_THREADS, TEMPERATURE
- PROYECTOS_DIR, APRENDIZAJE_DIR, ARQUITECTO_CONTEXT_SIZE, FRONTEND_CONTEXT_SIZE
- LOG_LEVEL, LOG_FILE
# Proveedores IA:
- QA_PROVIDER: ollama | anthropic | google | webhook
- REQS_PROVIDER: ollama | anthropic | google | webhook
- ANTHROPIC_API_KEY (si usas Anthropic)
- GOOGLE_API_KEY (si usas Google GenAI)
- N8N_WEBHOOK_URL (si usas Webhook externo)
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Clase de configuración que carga valores de variables de entorno."""
    
    def __init__(self):
      # Variables obligatorias
      self.ollama_url = os.environ["OLLAMA_URL"]
      self.ollama_timeout = int(os.environ["OLLAMA_TIMEOUT"])
      self.model_arquitecto = os.environ["MODEL_ARQUITECTO"]
      self.model_frontend = os.environ["MODEL_FRONTEND"]
      self.model_qa = os.environ["MODEL_QA"]
      self.num_threads = int(os.environ["NUM_THREADS"])
      self.temperature = float(os.environ["TEMPERATURE"])
      self.proyectos_dir = Path(os.environ["PROYECTOS_DIR"])
      self.aprendizaje_dir = Path(os.environ["APRENDIZAJE_DIR"])
      self.arquitecto_context_size = int(os.environ["ARQUITECTO_CONTEXT_SIZE"])
      self.frontend_context_size = int(os.environ["FRONTEND_CONTEXT_SIZE"])
      self.log_level = os.environ["LOG_LEVEL"]
      self.log_file = Path(os.environ["LOG_FILE"])

      # Proveedores IA (opcional, pero recomendados para nube)
      self.qa_provider = os.environ.get("QA_PROVIDER", "ollama")
      self.reqs_provider = os.environ.get("REQS_PROVIDER", "ollama")
      self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
      self.google_api_key = os.environ.get("GOOGLE_API_KEY")
      self.n8n_webhook_url = os.environ.get("N8N_WEBHOOK_URL")

      # Crear directorios necesarios
      self._crear_directorios()
    
    def _crear_directorios(self):
        """Crea los directorios necesarios si no existen."""
        self.proyectos_dir.mkdir(parents=True, exist_ok=True)
        self.aprendizaje_dir.mkdir(parents=True, exist_ok=True)
        self.aprendizaje_dir.joinpath("ejemplos").mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario para compatibilidad."""
        return {
          "ollama_url": self.ollama_url,
          "num_threads": self.num_threads,
          "models": {
            "arquitecto": self.model_arquitecto,
            "frontend": self.model_frontend,
            "qa": self.model_qa,
          },
          "paths": {
            "proyectos": str(self.proyectos_dir),
            "aprendizaje": str(self.aprendizaje_dir),
          },
          "context_sizes": {
            "arquitecto": self.arquitecto_context_size,
            "frontend": self.frontend_context_size,
          },
          "temperature": self.temperature,
          "timeout": self.ollama_timeout,
          "qa_provider": self.qa_provider,
          "reqs_provider": self.reqs_provider,
          "anthropic_api_key": self.anthropic_api_key,
          "google_api_key": self.google_api_key,
          "n8n_webhook_url": self.n8n_webhook_url,
        }
    
    def __str__(self) -> str:
        """Representación en string de la configuración."""
        return f"""Configuración Gemelo Digital:
  Ollama URL: {self.ollama_url}
  Timeout: {self.ollama_timeout}s
  
  Modelos:
    Arquitecto: {self.model_arquitecto}
    Frontend: {self.model_frontend}
    QA: {self.model_qa}
  
  Ejecución:
    Threads: {self.num_threads}
    Temperature: {self.temperature}
  
  Directorios:
    Proyectos: {self.proyectos_dir}
    Aprendizaje: {self.aprendizaje_dir}
  
  Contexto:
    Arquitecto: {self.arquitecto_context_size} tokens
    Frontend: {self.frontend_context_size} tokens
  
  Logging:
    Nivel: {self.log_level}
    Archivo: {self.log_file}
"""


# Instancia global de configuración
config = Config()


if __name__ == "__main__":
    # Mostrar configuración actual
    print(config)
    print("\nPara usar variables de entorno, crea un archivo .env o exporta:")
    print("  export OLLAMA_URL=http://localhost:11434")
    print("  export MODEL_ARQUITECTO=llama3.2:3b")
    print("  export MODEL_FRONTEND=qwen2.5-coder:3b")
    print("  ...")