"""
Agente de requerimientos: análisis estructurado con LLM configurable y Pydantic.
"""

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
        problem_questions: List[str] = []
        actors: List[str] = []
        analysis_questions: List[str] = []
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
CONTEXTO

QUE SE HACE EN EL ANALISIS DE REQUERIMIENTOS

- Levantamiento de información: Aquí se recopila información para generar un contexto.

- Identificación de necesidades: Con la información obtenida se detecta la necesidad de cada actor involucrado.

- Análisis y organización: Se ordena la información recopilada en el levantamiento de información y en la identificación de necesidades para definir prioridades.

- Especificación: Se escriben los requerimientos de forma clara, precisa y verificable.

- Validación: Se revisa lo obtenido en la especificación con el usuario para verificar que lo obtenido resuelve su problema.

QUE SON LOS REQUERIMIENTOS

Son necesidades, condiciones o capacidades que debe cumplir el producto que se va a desarrollar.

TIPOS DE REQUERIMIENTOS

- Requerimientos funcionales: Describen que debe hacer el producto que se va a desarrollar.

- Requerimientos no funcionales: Describen como debe comportarse el sistema.

CARACTERISTICAS DE UN BUEN REQUERIMIENTO

- Claridad: Un requerimiento no puede ser confuso.

- Especificidad: Un requerimiento debe explicar de manera exacta lo que debe hacer.

- Consistencia: Un requerimiento no puede contradecir otros.

- Verificabilidad: Un requerimiento debe poder comprobarse.

- Realismo: Un requerimiento debe poder implementarse teniendo en cuenta las limitaciones del proyecto.

TIPOS DE PAGINAS WEB

- Estáticas
	Definición: Son paginas web con contenido, es decir que no cambia según el usuario.
	Sirven para: mostrar información simple.
	Ejemplos: Portafolios web, landing pages simples.

- Dinámicas
	Definición: Son paginas web con generación de contenido en tiempo real, utilizan bases de datos y pueden personalizarse.
	Sirven para: Que los usuarios interactúen con ellas y para actualizar contenido de manera frecuente.
	Ejemplos: Redes sociales, blogs que permiten comentarios, plataformas educativas (E-learnings), sistemas de gestión empresarial, foros.

- Híbridos
	Definición: Son paginas web que combinan partes estáticas y dinámicas.
	Sirven para: Optimizar el rendimiento y mejorar la funcionalidad de la pagina.
	Ejemplos: Sitios web corporativos, sitios web periodísticos, landing pages complejas (Es decir que usan formularios dinámicos por poner un ejemplo), portales institucionales con 	login, plataformas SaaS.

- Sitios web corporativos
	Definición: Son paginas web diseñadas para representar a una empresa o institución a través de información sobre las mismas.
	Sirven para: Aumentar la presencia de la empresa o institución de modo que mas personas las conozcan.
	Ejemplos: Las paginas web de empresas como Coca-Cola o de instituciones como los bancos, las universidades o las ONG´s institucionales.

- E-comerce
	Definición: Son paginas web diseñadas para vender productos o servicios.
	Sirven para: Aumentar la cantidad de clientes de modo que las ventas aumenten.
	Ejemplos: Amazon, Mercado Libre, eBay, Shopify o AliExpress.

- Blogs
	Definición: Son paginas web diseñadas para publicar contenido de manera periódica.
	Sirven para: 
	Ejemplos: Las paginas web dedicadas a publicar contenido sobre temas como tecnología, marketing, viajes o incluso contenido personal.

- E-learnings
	Definición: Son paginas web educativas diseñadas para promover la formación y el aprendizaje.
	Sirven para:
	Ejemplos: Coursera, Khan Academy, Moodle, Udemy o Platzi.

- Sitios web de entretenimiento
	Definición: Son paginas web diseñadas pasa consumir contenido multimedia.
	Sirven para:
	Ejemplos: Netflix, YouTube, Spotify, Twitch o Disney+.

- Landing pages
	Definición: Son paginas web diseñadas para transformar visitantes en leads a través de la interacción.
	Sirven para: 
	Ejemplos: Paginas de registro, de campañas publicitarias o de capacitación de leads.

- Portales web
	Definición: Son paginas web diseñadas para centralizar información.
	Sirven para:
	Ejemplos: Yahoo, MSN, portales gubernamentales, intranets empresariales o portales periodísticos.

- Foros
	Definición: Son paginas web diseñadas para compartir información y comentar dicha información a través de la interacción de usuarios.
	Sirven para:
	Ejemplos: Reddit, Stack Overflow, foros de videojuegos o académicos, e incluso comunidades técnicas.

- Wikis
	Definición: Son paginas web diseñadas para promover la construcción colaborativa de conocimiento.
	Sirven para:
	Ejemplos: Wikipedia, Wikihow, Wiktionary, Wikibooks o Wikidata.

- Redes sociales
	Definición: Son paginas diseñadas para interacción social a través de entornos digitales.
	Sirven para:
	Ejemplos: Facebook, Instagram, Twitter (X), TikTok o LinkedIn.

- Aplicaciones web
	Definición: Son paginas web diseñadas para correr una app a través de un navegador web.
	Sirven para:
	Ejemplos: Google Docs, Gmail, Trello, Notion o Canva.

- Sitios web de servicios (SaaS)
	Definición: Son paginas web diseñadas para ofrecer software como servicio
	Sirven para:
	Ejemplos: Salesforce, Slack, Zoom, Dropbox o HubSpot.

COMPONENTES MINIMOS PARA EL DESARROLLO DE PAGINAS WEB

- Dominio: Es la dirección de la pagina web y permite que el usuario encuentre la pagina web de manera eficiente.

- Hosting (Servidor): Es el componente que aloja los archivos y servicios de la pagina web, su importancia radica en que sin este componente la pagina web no puede estar disponible en internet.

- Frontend: Es el componente que muestra la interfaz que el usuario va a observar al momento de ingresar a la pagina web, su importancia radica en que sin este componente la experiencia del usuario será un desastre.

- Estructura HTML: Organiza contenidos como los títulos, las imágenes, los textos o los enlaces de la pagina web, su importancia radica en que sin este componente el navegador no puede interpretar la pagina web.

- Estilos CSS: Es el componente que define la apariencia de la pagina web, se encarga de los colores, tamaños o distribuciones, su importancia radica en que sin este componente la pagina web no seria legible, usable o visualmente coherente.

- Lógica de comportamiento (JavaScript o similares): Es el componente que maneja la interacción de la pagina web con los usuarios en cuanto a menús, formularios, filtros o validaciones, esto permite que la pagina web responda de forma dinámica.

- Seguridad básica (HTTPS o certificados): Es el componente que se encarga del cifrado de la información y la protección de datos, permite que la pagina web sea una pagina web de confianza, integra y privada.

- Adaptabilidad móvil: Es el componente que le permite a la pagina web adaptarse a celulares, tablets, portátiles o computadores de escritorio, su importancia radica en que la mayor parte de los clientes suelen ingresar a las paginas a través de dispositivos móviles.

- Interacciones: Se encargan del envió de datos hacia la pagina web y permiten facilitar labores de comunicación, registro o solicitud.

- Bases de datos: Sirven para almacenar datos de usuarios, productos, pedidos, entre otros, es indispensable cuando el contenido cambia.

- Backend: Es el componte que procesa las reglas del negocio y las solicitudes de la pagina web, permite autenticar, guardar, consultar o automatizar procesos.

- Sistemas de autenticación: Se encarga de los logins, registros o recuperaciones de cuentas, es esencial cuan la pagina web posee usuarios con roles y datos privados.

- Paneles de administración: Es el componente que permite gestionar usuarios, contenido o configuraciones, permite facilitar el mantenimiento sin depender de código.

- Buscadores: Se encargan de localizar contenido dentro de la pagina web, permiten mejorar el acceso a la información de la pagina web.

- Copias de seguridad: Son las encargadas de respaldar la información de la pagina web, su importancia radica en que permite proteger la pagina web contra la perdida de datos o las fallas de nivel técnico.

FLUJO DE TRABAJO

Vas a recibir una solicitud ejecutada por un usuario, tu trabajo es transformar esa solicitud en un análisis de requerimientos profesional, dicho análisis de requerimientos debe servir para que después nuestro agente de diseño pueda transformarlo en un diseño de arquitectura, por lo que es estrictamente obligatorio que en análisis de requerimientos quede claro y bien definido.

Para desarrollar tu proceso de análisis de requerimientos vas a seguir el siguiente paso a paso:

1. Definición del problema: En esta etapa vas a recopilar información acerca de la solicitud que hizo el usuario, a través de preguntas. Ejemplo: Supongamos que un usuario te pide que le ayude a desarrollar una pagina web para su tienda, en ese caso yo necesito que tu seas capaz de identificar cual es el tipo de pagina web que necesita el usuario, para identificar el tipo de pagina web que necesita puedes guiarte por los tipos de paginas web que te brinde en el "CONTEXTO" en la sección "TIPOS DE PAGINAS WEB". Después de haber identificado el tipo de pagina web que necesita el usuario, vas a empezar a hacerle preguntas para explorar junto al usuario cual debe ser la apariencia de la pagina web, la preguntas que debes hacer para cumplir con este fin, son las siguientes:

¿Cuál es el nombre oficial de la página web?
¿La web representa una a persona, a una empresa, a una institución o, a una marca?
¿Existe ya un logotipo o identidad visual definida?
¿Quiere informar, vender, captar contactos, educar o entretener?
¿Debe llenar formularios, registrarse, comprar, comentar o descargar archivos?
¿La página debe responder a acciones en tiempo real?
¿Hay colores corporativos definidos?
¿Debe verse formal, moderna, minimalista, juvenil o institucional?
¿La web manejará datos personales?
¿Los usuarios deben iniciar sesión?
¿Se harán pagos o transacciones?
¿Necesita confirmación por correo o verificación de cuenta?
¿Necesita un panel de administración?
¿Se agregará información nueva con frecuencia?
¿El cliente quiere poder editar contenido sin ayuda técnica?

2. Identificación de actores: Una vez que el usuario haya terminado de responder las preguntas de la etapa "Definición del problema", vas a tomar toda esa información para identificar a los actores que van a interactuar con la pagina web que se va a desarrollar. Por ejemplo: Vamos a suponer que con la identificación del tipo de pagina web que necesita el usuario, y la respuesta de las preguntas de la etapa "Definición del problema", se determina que la pagina web que se va a desarrollar será un "E-comerce", en ese caso uno de los actores que interactuaría con la pagina web serian los clientes. Ya cuando termines de identificar a los actores, le harás una pregunta al usuario en donde le notifiques los actores que determinaste, y le pidas verificar si falta algún actor, o si considera que los que determinaste son suficientes.

3. Análisis: Con la información obtenida en la "Definición del problema" y la "Identificación de actores", deberías ser capaz de determinar el alcance de la pagina web, si con esa información no te queda claro el alcance de la pagina web, pues podrás hacer preguntas para clarificar. SIN EMBARGO, solo podrás hacer una ronda de preguntas de clarificación en esta etapa.

4. Definición de requerimientos funcionales y no funcionales: En esta etapa vas a tomar toda la información obtenida en las etapas de "Definición del problema", "Identificación de actores" y "Análisis", para determinar los requerimientos funcionales y no funcionales que debe tener la pagina web para ser desarrollada correctamente, debes apoyarte de la información que te brinde en el "CONTEXTO", en la sección de "QUE SON LOS REQUERIMEINTOS", los "TIPOS DE REQUERIMIENTOS" y las "CARACTERISTICAS DE UN BUEN REQUERIMIENTO".

5. Identificación de las reglas de negocio: En esta etapa vas a tomar toda la información obtenida de las etapas anteriores, para determinar las reglas del negocio que van a regir la pagina web, una vez tengas determinadas las reglas del negocio, vas a hacerle una pregunta al usuario para que verifique si esta de acuerdo, o si le gustaria añadir alguna regla, o, si le gustaria eliminar alguna regla.

NOTA: si al final de las etapas "Definición del problema", "Identificación de actores", "Análisis", "Definición de reuqerimientos funcionales y no funcionales" y "Identificación de las reglas de negocio", consideras que aun hace falta informacion para poder hacer un correcto desarrollo de la pagina web, tienes permitido hacer preguntas aclaratorias, SIN EMBARGO, solo tienes una ronda de preguntas, por lo tanto debes ecoger las preguntas que vas a hacerle al usuario.

Aspectos a tener en cuenta

1. Independientemente del tipo de pagina web que se vaya a desarrollar, debes asegurarte que la pagina web:
	- sea usable en celular, tableta y computadores.
	- sea sencilla para usuarios con poca experiencia digital
	- Tenga un nivel de seguridad intermedio.

2. En la sección "proyect_summary" vas a añadir el tipo de pagina web que determinaste para la peticion del cliente.

3. Las preguntas de la etapa "Definición del problema" las va enlistar en una sección llamada "problems_questions".

4. La pregunta de la etapa "Identifiación de actores" en donde le notificaras al usuario los actores que determinaste y le pediras que verifique si falta algun actor, o si considera que los que determinaste son suficientes, la vas a poner en una sección llamada "actors".

5. Las preguntas de la etapa de "Análisis", las vas a enlistar en una sección llamada "analysis_questions".

6. Los requerimientos funcionales deben ir enlistados en una seccion llamada "funtional_requeriments" y los requerimientos no funcionales deben ir en una seccion llamada "non_funtional_requeriments"

7. Las preguntas aclaratorias que vas a hacer en caso de que requieras de información adicional para el desarrollo de la pagina web, las vas a enlistar en una seccion llamada "open_questions".
"""
        ),
        ("human", "Petición del usuario:\n{user_request}")
    ])

    # Usar llamar_llm para evitar problemas de serialización
    formatted_prompt = prompt.format(user_request=user_request)
    raw_response = llamar_llm(formatted_prompt, temperature=0, agente="reqs")
    if not raw_response:
        raise RuntimeError("No se pudo obtener respuesta del LLM")

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
