# Gemelo Digital – Backend API

## Demo en video

Mira el funcionamiento completo del sistema en este video de YouTube:
[![Demo en YouTube](https://img.shields.io/badge/Ver%20demo%20en%20YouTube-red?logo=youtube)](https://youtu.be/8BS_5ewmwf0)

Backend con FastAPI que genera proyectos web completos usando agentes de IA. Se conecta con el frontend en React.

## Requisitos

- Python 3.10+
- Una API key de Google Gemini (gratis) o DeepSeek

## Instalación rápida

```bash
# 1. Clonar el repo
git clone https://github.com/luis-miguel-cote/backend-ai-agents-hackathon.git
cd backend-ai-agents-hackathon

# 2. Crear entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y poner tu API key (ver sección de abajo)
```

## Configurar el .env

Copia `.env.example` como `.env` y llena **mínimo** tu API key:

```env
# Proveedor por defecto (google o deepseek)
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash-lite

# Tu API key de Google Gemini (sácala en https://aistudio.google.com/apikey)
GOOGLE_API_KEY=tu_key_aqui

# O si prefieres DeepSeek (https://platform.deepseek.com/api_keys):
# LLM_PROVIDER=deepseek
# LLM_MODEL=deepseek-chat
# DEEPSEEK_API_KEY=tu_key_aqui
```

### Modelo por agente (opcional)

Puedes usar un modelo diferente para cada agente. Por ejemplo, Gemini para análisis y DeepSeek para generar código:

```env
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash-lite

# Solo el generador usa DeepSeek
GENERADOR_PROVIDER=deepseek
GENERADOR_MODEL=deepseek-chat
DEEPSEEK_API_KEY=tu_key_aqui
```

Agentes configurables: `REQS_`, `ARQUITECTO_`, `GENERADOR_` (cada uno con `_PROVIDER` y `_MODEL`).

## Arrancar la API

```bash
# Activar el entorno virtual (si no está activado)
.venv\Scripts\activate

# Arrancar el servidor
uvicorn api:app --reload --port 8000
```

La API queda en **http://localhost:8000**

Docs interactivos (Swagger): **http://localhost:8000/docs**

## Endpoints para el frontend

### 1. Iniciar proyecto

```
POST /proyecto/iniciar
Content-Type: application/json

{
  "descripcion": "Landing page para una cafetería con menú, galería y contacto"
}
```

**Respuesta:**
```json
{
  "session_id": "a1b2c3d4",
  "requerimientos": {
    "titulo": "Cafetería Web",
    "resumen": "...",
    "total_funcionales": 5,
    "total_no_funcionales": 3,
    "preguntas_abiertas": ["¿Tiene logo?", "¿Qué colores prefiere?"]
  },
  "preguntas": ["¿Tiene logo?", "¿Qué colores prefiere?"],
  "listo_para_generar": false
}
```

### 2. Responder preguntas (si hay)

```
POST /proyecto/{session_id}/responder
Content-Type: application/json

{
  "respuestas": {
    "0": "Sí, el logo es un grano de café",
    "1": "Colores tierra: marrón y crema"
  }
}
```

Repite hasta que `listo_para_generar: true` o máximo 3 rondas.

### 3. Generar proyecto

```
POST /proyecto/{session_id}/generar
```

No necesita body. Esto lanza la generación en background. Responde inmediatamente con `estado: "en_progreso"`.

Opcional: `POST /proyecto/{session_id}/generar?skip_qa=true` para saltar la validación de calidad.

### 4. Consultar progreso (polling)

```
GET /proyecto/{session_id}/estado
```

Hacer polling cada 2 segundos. Respuesta mientras genera:

```json
{
  "estado": "en_progreso",
  "progreso": {
    "fase": "Generado: css/styles.css",
    "porcentaje": 45,
    "archivos_listos": ["index.html", "css/styles.css"]
  }
}
```

Cuando termina:

```json
{
  "estado": "completado",
  "progreso": { "fase": "Completado", "porcentaje": 100 },
  "resultado": {
    "nombre": "proyecto_20260405_143000",
    "archivos": ["index.html", "css/styles.css", "js/main.js", "README.md"],
    "qa": { "verdict": "GREEN", "pass_rate": 85 },
    "tipo_proyecto": "landing_page"
  }
}
```

### 5. Listar proyectos

```
GET /proyectos
```

### 6. Leer archivo de un proyecto

```
GET /proyecto/{nombre_proyecto}/archivos/{ruta}
```

Ejemplo: `GET /proyecto/proyecto_20260405_143000/archivos/index.html`

### 7. Ver configuración actual

```
GET /config
```

## Flujo completo desde React

```
1. POST /proyecto/iniciar        → obtener session_id + preguntas
2. POST /proyecto/{id}/responder  → (solo si hay preguntas) enviar respuestas
3. POST /proyecto/{id}/generar    → lanzar generación
4. GET  /proyecto/{id}/estado     → polling cada 2s hasta estado="completado"
5. GET  /proyecto/{nombre}/archivos/index.html → mostrar preview
```

## Ejemplo con fetch (React)

```javascript
// 1. Iniciar
const res = await fetch('http://localhost:8000/proyecto/iniciar', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ descripcion: 'Landing page para cafetería' })
});
const { session_id, preguntas, listo_para_generar } = await res.json();

// 2. Si hay preguntas, responder
if (!listo_para_generar) {
  await fetch(`http://localhost:8000/proyecto/${session_id}/responder`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ respuestas: { "0": "Logo de café", "1": "Colores tierra" } })
  });
}

// 3. Generar
await fetch(`http://localhost:8000/proyecto/${session_id}/generar`, { method: 'POST' });

// 4. Polling
const poll = setInterval(async () => {
  const estado = await fetch(`http://localhost:8000/proyecto/${session_id}/estado`).then(r => r.json());
  console.log(estado.progreso.fase, estado.progreso.porcentaje + '%');
  if (estado.estado === 'completado') {
    clearInterval(poll);
    console.log('Proyecto listo:', estado.resultado);
  }
}, 2000);
```

## Estructura del proyecto

```
├── api.py                  ← API FastAPI (punto de entrada)
├── gemelo_digital.py       ← Orquestador CLI (para terminal)
├── config.py               ← Configuración desde .env
├── .env.example            ← Template de variables de entorno
├── requirements.txt
├── core/
│   ├── llm.py              ← Proveedor LLM centralizado
│   ├── arquitecto.py       ← Define estructura de archivos
│   ├── generador.py        ← Genera código (HTML, CSS, JS, Python)
│   ├── aprendizaje.py      ← Sistema de aprendizaje por ejemplos
│   ├── input.py            ← Procesador de input (texto, PDF, DOCX)
│   ├── medicion.py         ← Medición de tiempos
│   └── progreso.py         ← Indicador de progreso
├── agentes/
│   ├── agente_requerimientos.py  ← Análisis de requerimientos con chat
│   ├── agente_qa.py              ← Validación de calidad
│   ├── agente_devops.py          ← Archivos de deployment
│   └── agente_assets.py          ← Descarga de imágenes (Pexels)
└── proyectos_generados/    ← Aquí se guardan los proyectos
```

## CORS

CORS está habilitado para todos los orígenes (`*`). Si necesitas restringirlo, edita `api.py` línea `allow_origins`.

## Notas

- La generación toma entre 30-90 segundos dependiendo del modelo y la complejidad.
- Gemini 2.5 Flash Lite tiene límite de 20 requests/día (gratis). Para más, usa `gemini-2.0-flash` (1500/día) o DeepSeek.
- Los proyectos generados se sirven como archivos estáticos en `/proyectos_static/`.
