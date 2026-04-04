"""
Configuración del Gemelo Digital.
Usa variables de entorno con valores por defecto.
"""

import os
from pathlib import Path
from typing import Dict, Any


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