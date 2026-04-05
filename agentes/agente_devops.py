"""
Agente DevOps: prepara archivos de despliegue automático.
"""

def generate_deployment_files(project_type: str) -> dict:
    files = {}

    # Frontend estático / landing
    if project_type == "landing_page":
        files["vercel.json"] = """{
  "cleanUrls": true
}"""

        files[".env.example"] = """VITE_API_URL=https://tu-backend.onrender.com"""

    # Backend Python
    elif project_type == "python_backend":
        files["Dockerfile"] = """FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
"""

        files["render.yaml"] = """services:
  - type: web
    name: ai-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
"""

        files[".env.example"] = """GOOGLE_API_KEY=tu_api_key"""

    return files