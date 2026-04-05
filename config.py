"""
Configuración del Gemelo Digital.
Usa variables de entorno cargadas desde .env

Variables principales:
- LLM_PROVIDER: google | deepseek | anthropic | ollama
- LLM_MODEL: modelo por defecto para todos los agentes
- GOOGLE_API_KEY, DEEPSEEK_API_KEY, ANTHROPIC_API_KEY (segun proveedor)
- PROYECTOS_DIR, APRENDIZAJE_DIR, LOG_LEVEL, LOG_FILE
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Clase de configuración que carga valores de variables de entorno."""
    
    def __init__(self):
      # Proveedor LLM
      self.llm_provider = os.environ.get("LLM_PROVIDER", "google")
      self.llm_model = os.environ.get("LLM_MODEL", "gemini-2.5-flash-lite")

      # API Keys
      self.google_api_key = os.environ.get("GOOGLE_API_KEY")
      self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
      self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
      self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
      self.n8n_webhook_url = os.environ.get("N8N_WEBHOOK_URL")

      # Directorios
      self.proyectos_dir = Path(os.environ.get("PROYECTOS_DIR", "./proyectos_generados"))
      self.aprendizaje_dir = Path(os.environ.get("APRENDIZAJE_DIR", "./aprendizaje"))

      # Logging
      self.log_level = os.environ.get("LOG_LEVEL", "INFO")
      self.log_file = Path(os.environ.get("LOG_FILE", "./logs/gemelo_digital.log"))

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
          "paths": {
            "proyectos": str(self.proyectos_dir),
            "aprendizaje": str(self.aprendizaje_dir),
          },
          "llm_provider": self.llm_provider,
          "llm_model": self.llm_model,
          "log_level": self.log_level,
        }
    
    def __str__(self) -> str:
        """Representación en string de la configuración."""
        return f"""Configuración Gemelo Digital:
  LLM Provider: {self.llm_provider}
  LLM Model: {self.llm_model}
  
  Directorios:
    Proyectos: {self.proyectos_dir}
    Aprendizaje: {self.aprendizaje_dir}
  
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