import streamlit as st
import requests
import threading
import time
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
# Reemplazar con tu clave real si vas a usar DeepSeek
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"

# Contraseña de administrador para editar la base local en la aplicación
ADMIN_PASSWORD = "mercedaria2025"

# Endpoints remotos
API_USERS = "https://mi-insm.onrender.com/users"
API_COURSES = "https://mi-insm.onrender.com/courses"
API_TASKS = "https://mi-insm.onrender.com/tasks"
API_FILES = "https://mi-insm.onrender.com/files"
API_EGRESADOS = "https://mi-insm.onrender.com/egresados"

# ==============================
# BASE DE CONOCIMIENTO LOCAL (ORIGINAL)
# ==============================
BASE_GENERAL = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quién eres", "Soy MercedarIA, tu asistente del colegio."),
    ("cómo te llamas", "Me llamo MercedarIA, tu asistente virtual."),
    ("cómo estás", "Estoy funcionando perfectamente, gracias por preguntar."),
    ("adiós", "¡Hasta luego! Que tengas un buen día."),
    ("quién es la directora", "La directora es Marisa Brizzio."),
    ("cuándo son los recreos", "Turno mañana: 8:35, 10:00, 11:35. Turno tarde: 14:40, 16:05, 17:50."),
    ("dónde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456."),
    ("cuándo empieza el ciclo lectivo", "El ciclo lectivo comienza el primer día hábil de marzo."),
    ("cuándo terminan las clases", "Generalmente a mediados de diciembre."),
]

BASES_ESPECIFICAS = {
    "1° A": [
        ("¿Qué materias tengo?", "Biología, Educación en Artes Visuales, Lengua y Literatura, Física, Geografía, Educación Tecnológica, Matemática, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física y Educación Tecnológica."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "1° B": [
        ("¿Qué materias tengo?", "Física, Matemática, Educación en Artes Visuales, Inglés, Educación Religiosa Escolar, Lengua y Literatura, Geografía, Ciudadanía y Participación, Educación Tecnológica, Biología y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Tecnológica y Educación Física."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "2° A": [
        ("¿Qué materias tengo?", "Matemática, Lengua y Literatura, Educación Religiosa Escolar, Música, Historia, Educación Tecnológica, Química, Computación, Ciudadanía y Participación, Biología, Inglés y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "2° B": [
        ("¿Qué materias tengo?", "Música, Historia, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés, Matemática, Lengua y Literatura, Educación Tecnológica, Química, Biología y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "3° A": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Inglés, Historia, Geografía, Química, Educación Tecnológica, Física, Educación Religiosa Escolar, Formación para la Vida y el Trabajo, Matemática, Educación Artística Visual, Música, Computación y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física y Formación para la Vida y el Trabajo."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "3° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Formación para la Vida y el Trabajo, Física, Historia, Geografía, Educación Artística Visual, Música, Matemática, Educación Tecnológica, Química, Computación, Educación Religiosa Escolar, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "4° A": [
        ("¿Qué materias tengo?", "Historia, Lengua y Literatura, Biología, Educación Religiosa Escolar, Matemática, Geografía, Educación Artística, Formación para la Vida y el Trabajo, Tecnologías de la Información y la Comunicación (TIC), Sociedad, Cultura y Comunicación, Antropología, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "4° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Biología, Educación Religiosa Escolar, Historia, Tecnología y Lenguajes de Programación, Geografía, Matemática, Sistemas Digitales de Información, Formación para la Vida y el Trabajo, Educación Artística, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "5° A": [
        ("¿Qué materias tengo?", "Metodología, Historia, Física, Geografía, Arte Cultural y Social, Educación Religiosa Escolar, Lengua y Literatura, Formación para la Vida y el Trabajo, Matemática, Educación Física, Psicología, Sociología e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Psicología, Sociología e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "5° B": [
        ("¿Qué materias tengo?", "Robótica, Música, Física, Matemática, Historia, Lengua y Literatura, Formación para la Vida y el Trabajo, Sistemas Digitales de Información, Geografía, Psicología, Educación Física, Desarrollo de Soluciones Informáticas e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Sistemas Digitales de Información, Desarrollo de Soluciones Informáticos e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "6° A": [
        ("¿Qué materias tengo?", "Ciudadanía y Política, Economía Política, Matemática, Geografía, Filosofía, Química, Lengua y Literatura, Historia, Educación Religiosa Escolar, Sociedad, Cultura y Comunicación, Teatro, Formación para la Vida y el Trabajo, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Sociedad, Cultura y Comunicación e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "6° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Comunicación Audiovisual, Desarrollo de Soluciones Informáticas, Informática Aplicada, Filosofía, Formación para la Vida y el Trabajo, Química, Matemática, Ciudadanía y Política, Educación Religiosa Escolar, Teatro, Educación Física, Aplicaciones Informáticas e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Aplicaciones Informáticas e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ]
}

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def api_get(url):
    """
    Realiza una consulta GET al endpoint especificado y devuelve
    la respuesta parseada en formato json. Si hay error, devuelve lista vacía.
    """
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        # Acomodar respuesta si el endpoint devuelve {"data": [...]} u otras estructuras
        if isinstance(datos, dict) and "data" in datos and isinstance(datos["data"], list):
            return datos["data"]
        return datos
    except Exception as error:
        # No interrumpimos la aplicación por un fallo de la API remota
        return []

def construir_contexto_de_conocimiento(lista_preguntas_respuestas):
    """
    Construye un bloque de texto con la base de conocimiento para enviar
    a la IA cuando sea necesario.
    """
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for indice, (pregunta_texto, respuesta_texto) in enumerate(lista_preguntas_respuestas, 1):
        contexto += f"Pregunta {indice}: {pregunta_texto}\nRespuesta {indice}: {respuesta_texto}\n\n"
    return contexto

def consultar_deepseek_con_contexto(pregunta_usuario, api_key, contexto):
    """
    Consulta a DeepSeek con la base de conocimiento como contexto.
    Si no se dispone de clave, devuelve un mensaje indicando que no hay IA externa.
    """
    if not api_key:
        return "No tengo configurada la clave de DeepSeek. Respondo solo con la base local y con la información consultada en las APIs del colegio."
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",
             "content": (
                 "Sos MercedarIA, el asistente educativo del Colegio Mercedaria. "
                 "Usá la base de conocimiento local y la información de las APIs para responder preguntas del colegio. "
                 "Si la información no está disponible, respondé de manera educativa y correcta."
             )},
            {"role": "user", "content": f"{contexto}\n\nPregunta: {pregunta_usuario}"}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    try:
        respuesta_http = requests.post(url, headers=headers, json=data, timeout=60)
        respuesta_http.raise_for_status()
        respuesta_json = respuesta_http.json()
        return respuesta_json["choices"][0]["message"]["content"].strip()
    except Exception as error:
        return f"❌ Error al conectar con DeepSeek: {error}"

# ==============================
# CONFIGURACIÓN DE LA PÁGINA STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")

# ==============================
# INICIO: AUTENTICACIÓN POR DNI
# ==============================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("🔐 Ingreso al sistema de MercedarIA")
    st.write("Ingresá tu Documento Nacional de Identidad (DNI) para continuar.")
    dni_ingresado = st.text_input("Documento Nacional de Identidad (DNI):", key="dni_input")

    if st.button("Ingresar"):
        lista_usuarios = api_get(API_USERS)
        usuario_encontrado = None
        for usuario in lista_usuarios:
            # Normalizamos y comparamos como cadenas
            dni_usuario_remoto = str(usuario.get("dni", "")).strip()
            if dni_usuario_remoto == str(dni_ingresado).strip():
                usuario_encontrado = usuario
                break

        if usuario_encontrado:
            # Guardamos información básica del usuario en la sesión
            st.session_state.usuario = {
                "email": usuario_encontrado.get("email", ""),
                "nombre": usuario_encontrado.get("nombre", ""),
                "apellido": usuario_encontrado.get("apellido", ""),
                "dni": usuario_encontrado.get("dni", ""),
                "rol": usuario_encontrado.get("rol", ""),
                "curso": usuario_encontrado.get("curso", "").lower() if usuario_encontrado.get("curso") else "",
                "phone": usuario_encontrado.get("phone", ""),
                "profesor_de": usuario_encontrado.get("profesor_de", "")
            }
            st.success(f"Bienvenido/a {st.session_state.usuario['nombre']} {st.session_state.usuario['apellido']} - Curso: {st.session_state.usuario['curso'].upper() if st.session_state.usuario['curso'] else 'sin curso asignado'}")
            st.rerun()
        else:
            st.error("Documento Nacional de Identidad (DNI) no encontrado en el sistema. Verificá y volvé a intentarlo.")

    # Evitamos que se cargue el resto de la aplicación si no hay usuario logueado
    st.stop()

# ==============================
# SESIÓN ACTIVA: CARGA DE DATOS REMOTOS
# ==============================
# Cargamos las listas desde los endpoints remotos
lista_usuarios_remotos = api_get(API_USERS)
lista_cursos_remotos = api_get(API_COURSES)
lista_tareas_remotas = api_get(API_TASKS)
lista_archivos_remotos = api_get(API_FILES)
lista_egresados_remotos = api_get(API_EGRESADOS)

# Normalizamos el curso del usuario
usuario_actual = st.session_state.usuario
curso_del_usuario = (usuario_actual.get("curso") or "").lower()
dni_del_usuario = str(usuario_actual.get("dni", "")).strip()

# Filtramos las tareas que correspondan al curso del alumno y las tareas personales por dni
tareas_para_el_curso = []
tareas_personales = []
for tarea in lista_tareas_remotas or []:
    try:
        curso_tarea = str(tarea.get("curso", "")).lower()
    except Exception:
        curso_tarea = ""
    try:
        dni_tarea = str(tarea.get("dni", "")).strip()
    except Exception:
        dni_tarea = ""
    if curso_tarea and curso_tarea == curso_del_usuario:
        tareas_para_el_curso.append(tarea)
    if dni_tarea and dni_tarea == dni_del_usuario:
        tareas_personales.append(tarea)

# Filtramos los profesores del curso actual
profesores_del_curso = []
for entrada_curso in lista_cursos_remotos or []:
    try:
        curso_cadena = str(entrada_curso.get("curso", "")).lower()
    except Exception:
        curso_cadena = ""
    if curso_cadena and curso_cadena == curso_del_usuario:
        profesores_del_curso.append(entrada_curso)

# ==============================
# PANEL LATERAL Y SELECTORES
# ==============================
st.sidebar.title("📚 Menú de MercedarIA")

# Selector de curso para ver la base específica (además del curso detectado por DNI)
# Mostramos "General" y todas las claves locales y también cursos detectados remotamente
cursos_locales = ["General"] + list(BASES_ESPECIFICAS.keys())
# Extraemos cursos remotos únicos (lowercased) y los formateamos con mayúsculas y ordinales si es necesario
cursos_remotos_unicos = sorted({str(c.get("curso", "")).strip() for c in lista_cursos_remotos if c.get("curso")})
# Normalizamos presentación combinada
CURSOS_COMBINADOS = cursos_locales + cursos_remotos_unicos

curso_seleccionado_por_el_usuario = st.sidebar.selectbox("Seleccioná el curso para consultar (puede ser distinto a tu curso)", CURSOS_COMBINADOS, index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("Datos del usuario conectado")
st.sidebar.write(f"**Nombre:** {usuario_actual.get('nombre', '')} {usuario_actual.get('apellido', '')}")
st.sidebar.write(f"**Curso:** {usuario_actual.get('curso', '').upper()}")
st.sidebar.write(f"**Rol:** {usuario_actual.get('rol', '')}")
st.sidebar.write(f"**DNI:** {usuario_actual.get('dni', '')}")

st.sidebar.markdown("---")
st.sidebar.subheader("Consultas rápidas a la API")
if st.sidebar.button("Ver usuarios"):
    st.sidebar.write("Lista de usuarios cargada desde la API:")
    st.sidebar.write(lista_usuarios_remotos)

if st.sidebar.button("Ver cursos"):
    st.sidebar.write("Lista de cursos y asignaciones cargada desde la API:")
    st.sidebar.write(lista_cursos_remotos)

if st.sidebar.button("Ver tareas"):
    st.sidebar.write("Lista de tareas cargada desde la API:")
    st.sidebar.write(lista_tareas_remotas)

if st.sidebar.button("Ver archivos"):
    st.sidebar.write("Lista de archivos cargada desde la API:")
    st.sidebar.write(lista_archivos_remotos)

if st.sidebar.button("Ver egresados"):
    st.sidebar.write("Lista de egresados cargada desde la API:")
    st.sidebar.write(lista_egresados_remotos)

st.sidebar.markdown("---")
st.sidebar.subheader("Acciones de sesión")
if st.sidebar.button("Cerrar sesión"):
    # Limpiamos la sesión y recargamos
    for k in list(st.session_state.keys()):
        st.session_state.pop(k, None)
    st.rerun()

# ==============================
# INICIALIZACIÓN DE ESTADO DE APLICACIÓN
# ==============================
if "bases" not in st.session_state:
    st.session_state.bases = {
        "General": BASE_GENERAL.copy(),
        **{curso: BASES_ESPECIFICAS.get(curso, []).copy() for curso in BASES_ESPECIFICAS}
    }
if "historial" not in st.session_state:
    st.session_state.historial = []
if "edicion_activa" not in st.session_state:
    st.session_state.edicion_activa = False

# Aseguramos que el curso seleccionado exista en la base de session
if curso_seleccionado_por_el_usuario not in st.session_state.bases:
    st.session_state.bases[curso_seleccionado_por_el_usuario] = []

# Construimos la base completa que combina la base general, la base del curso seleccionado por el usuario y la información de tareas (como conocimiento)
base_completa_local = BASE_GENERAL + st.session_state.bases.get(curso_seleccionado_por_el_usuario, [])

# Agregamos la lista de tareas del curso seleccionado a la base de conocimiento como preguntas-respuestas
# Para que la IA local pueda usarlo como contexto textual
def integrar_tareas_en_base_conocimiento(lista_tareas, curso_para_integrar):
    nuevas_entradas = []
    for tarea in lista_tareas or []:
        titulo = tarea.get("titulo") or tarea.get("title") or "Tarea sin título"
        descripcion = tarea.get("descripcion") or tarea.get("description") or ""
        curso_tarea = tarea.get("curso") or ""
        dni_tarea = tarea.get("dni") or ""
        pregunta_texto = f"Tareas para {curso_tarea}"
        respuesta_texto = f"{titulo} - {descripcion} (Asignada a: {dni_tarea})"
        nuevas_entradas.append((pregunta_texto, respuesta_texto))
    return nuevas_entradas

# Integramos todas las tareas remotas a la base de conocimiento local (para el curso seleccionado en la sidebar)
entradas_de_tareas_para_el_curso = [t for t in lista_tareas_remotas if str(t.get("curso", "")).lower() == str(curso_seleccionado_por_el_usuario).lower()]
base_completa_local += integrar_tareas_en_base_conocimiento(entradas_de_tareas_para_el_curso, curso_seleccionado_por_el_usuario)

# Convertimos la base completa a texto contexto
contexto_para_ia = construir_contexto_de_conocimiento(base_completa_local)

# ==============================
# INTERFAZ PRINCIPAL CHAT
# ==============================
st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption("Responde con información local y con consultas a las APIs del colegio.")

st.subheader(f"💬 Chat con MercedarIA - Curso seleccionado: {curso_seleccionado_por_el_usuario}")

# Campo de entrada de la pregunta
pregunta_usuario = st.text_input("Escribí tu pregunta:", key="pregunta_input")

boton_enviar = st.button("Enviar", key=f"enviar_{curso_seleccionado_por_el_usuario}")

if boton_enviar and pregunta_usuario and pregunta_usuario.strip():
    # Guardamos la pregunta en el historial
    st.session_state.historial.append(("👨‍🎓 Usuario", pregunta_usuario.strip()))
    pregunta_normalizada = pregunta_usuario.lower().strip()

    respuesta_generada = None

    # 1) Búsqueda directa en la base local (coincidencia por substring)
    for pregunta_base, respuesta_base in base_completa_local:
        try:
            if pregunta_base.lower() in pregunta_normalizada:
                respuesta_generada = respuesta_base
                break
        except Exception:
            continue

    # 2) Respuestas específicas sobre tareas y profesores (prioridad antes de llamar a IA)
    # Respuestas sobre tareas: si el usuario pregunta "tarea" o "tareas" mostramos las tareas del curso detectado desde el DNI,
    # del curso seleccionado en la sidebar o tareas personales
    if not respuesta_generada:
        texto_busqueda_tareas = ["tarea", "tareas", "tengo tareas", "qué tareas", "que tareas", "tareas para", "tenes tareas", "hay tareas"]
        if any(token in pregunta_normalizada for token in texto_busqueda_tareas):
            # Si la pregunta menciona un curso explícito, intentamos extraerlo
            curso_objetivo = None
            # Buscamos patrones simples como "1b" o "primero b" o "primero b"
            palabras = pregunta_normalizada.replace("º", "").replace("°", "").split()
            for palabra in palabras:
                candidato = palabra.replace(".", "").replace(",", "").strip()
                # si el formato está como "1b" o "1°b" ya lo cubrimos; comprobamos longitud corta
                if 2 <= len(candidato) <= 3 and any(c.isdigit() for c in candidato):
                    curso_objetivo = candidato.lower()
                    break
            # Si no se detecta curso explícito usamos el curso del usuario autenticado
            if not curso_objetivo:
                curso_objetivo = curso_del_usuario

            # Recolectamos tareas del curso objetivo y tareas personales
            tareas_del_objetivo = [t for t in lista_tareas_remotas if str(t.get("curso", "")).lower() == str(curso_objetivo).lower()]
            tareas_personales_del_usuario = [t for t in lista_tareas_remotas if str(t.get("dni", "")).strip() == dni_del_usuario]

            respuesta_texto = f"📚 Tareas para el curso {curso_objetivo if curso_objetivo else 'no especificado'}:\n\n"
            if tareas_del_objetivo:
                for t in tareas_del_objetivo:
                    titulo = t.get("titulo") or t.get("title") or "Tarea sin título"
                    descripcion = t.get("descripcion") or t.get("description") or ""
                    fecha_entrega = t.get("fecha_entrega") or t.get("due_date") or ""
                    respuesta_texto += f"• {titulo} — {descripcion}"
                    if fecha_entrega:
                        respuesta_texto += f" (Entrega: {fecha_entrega})"
                    respuesta_texto += "\n"
            else:
                respuesta_texto += "No hay tareas públicas cargadas para este curso.\n"

            respuesta_texto += "\n🧍‍♂️ Tus tareas personales:\n"
            if tareas_personales_del_usuario:
                for t in tareas_personales_del_usuario:
                    titulo = t.get("titulo") or t.get("title") or "Tarea sin título"
                    descripcion = t.get("descripcion") or t.get("description") or ""
                    fecha_entrega = t.get("fecha_entrega") or t.get("due_date") or ""
                    respuesta_texto += f"• {titulo} — {descripcion}"
                    if fecha_entrega:
                        respuesta_texto += f" (Entrega: {fecha_entrega})"
                    respuesta_texto += "\n"
            else:
                respuesta_texto += "No tenés tareas personales asignadas.\n"

            respuesta_generada = respuesta_texto

    # 3) Respuestas específicas sobre profesores y mails
    if not respuesta_generada:
        tokens_consulta_profesores = ["profe", "profesor", "profesora", "mail", "correo", "correo electrónico", "mail del", "mail de"]
        if any(token in pregunta_normalizada for token in tokens_consulta_profesores):
            # Intentamos identificar la materia solicitada
            materia_solicitada = None
            # Tomamos palabras importantes
            palabras = pregunta_normalizada.replace("?", "").replace("¿", "").split()
            # Buscamos una materia conocida en la lista de cursos_remotos (comprobación simple)
            posibles_materias = {str(c.get("materia", "")).lower(): c for c in lista_cursos_remotos if c.get("materia")}
            # Heurística: buscar la palabra más larga que coincida con una materia
            palabra_materia_encontrada = None
            for palabra in palabras:
                clave = palabra.strip().lower()
                if clave in posibles_materias:
                    palabra_materia_encontrada = clave
                    break
            # Si no encontramos materia explícita, devolvemos todos los profesores del curso si coincide
            if palabra_materia_encontrada:
                entrada = posibles_materias[palabra_materia_encontrada]
                correo = entrada.get("profesor_mail") or entrada.get("mail") or entrada.get("email") or "No disponible"
                materia_nombre = entrada.get("materia") or palabra_materia_encontrada
                respuesta_texto = f"👩‍🏫 Profesor de {materia_nombre}:\nCorreo: {correo}"
            else:
                # Mostramos todos los profesores del curso del usuario
                if profesores_del_curso:
                    respuesta_texto = "👩‍🏫 Profesores y correos del curso:\n"
                    for p in profesores_del_curso:
                        materia = p.get("materia") or "Materia desconocida"
                        correo = p.get("profesor_mail") or p.get("mail") or p.get("email") or "No disponible"
                        respuesta_texto += f"• {materia}: {correo}\n"
                else:
                    respuesta_texto = "No encontré información de los profesores para tu curso."
            respuesta_generada = respuesta_texto

    # 4) Si no se generó respuesta local, consultamos la IA externa o devolvemos mensaje por defecto
    if not respuesta_generada:
        # Añadimos al contexto la información de tareas del curso del usuario para que la IA lo tenga en cuenta
        contexto_actualizado = contexto_para_ia
        # Llamada a DeepSeek si está configurado
        respuesta_ia = consultar_deepseek_con_contexto(pregunta_usuario, DEEPSEEK_API_KEY, contexto_actualizado)
        respuesta_generada = respuesta_ia

    # Guardamos la respuesta en el historial
    st.session_state.historial.append(("🤖 MercedarIA", respuesta_generada))

# Mostramos el historial (las últimas 40 entradas)
st.markdown("### Historial de conversación")
for rol, mensaje in st.session_state.historial[-40:]:
    if rol == "👨‍🎓 Usuario":
        st.markdown(f"**{rol}:** {mensaje}")
    else:
        # Resaltamos respuestas de MercedarIA
        st.markdown(f"<div style='background:#0b3d2e;padding:8px;border-radius:6px;color:#ffffff'><b>{rol}:</b> {mensaje}</div>", unsafe_allow_html=True)

st.divider()

# ==============================
# PANEL DE EDICIÓN PROTEGIDO
# ==============================
st.subheader("🧩 Panel de Edición (solo personal autorizado)")

if not st.session_state.edicion_activa:
    password_input = st.text_input("🔒 Ingresá la contraseña para editar", type="password", key="password_panel")
    if st.button("Acceder", key="login_panel"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.edicion_activa = True
            st.success("✅ Acceso concedido al modo edición.")
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta. No se ha activado el modo edición.")
else:
    st.success(f"Modo edición activado para: {curso_seleccionado_por_el_usuario}")

    base_editable = st.session_state.bases[curso_seleccionado_por_el_usuario]

    # Mostramos cada entrada editable
    for indice, (pregunta_texto, respuesta_texto) in enumerate(base_editable.copy()):
        columna1, columna2, columna3 = st.columns([4, 5, 1])
        with columna1:
            nueva_pregunta_texto = st.text_input(f"Pregunta {indice+1}", pregunta_texto, key=f"p_{curso_seleccionado_por_el_usuario}_{indice}")
        with columna2:
            nueva_respuesta_texto = st.text_area(f"Respuesta {indice+1}", respuesta_texto, key=f"r_{curso_seleccionado_por_el_usuario}_{indice}")
        with columna3:
            if st.button("🗑", key=f"del_{curso_seleccionado_por_el_usuario}_{indice}"):
                try:
                    base_editable.pop(indice)
                except Exception:
                    pass
                st.rerun()
        # Actualizamos la entrada
        base_editable[indice] = (nueva_pregunta_texto, nueva_respuesta_texto)

    st.markdown("---")
    nueva_pregunta_nueva = st.text_input("➕ Nueva pregunta", key=f"nueva_p_{curso_seleccionado_por_el_usuario}")
    nueva_respuesta_nueva = st.text_area("Respuesta", key=f"nueva_r_{curso_seleccionado_por_el_usuario}")
    if st.button("Agregar a la base", key=f"add_{curso_seleccionado_por_el_usuario}"):
        if nueva_pregunta_nueva and nueva_respuesta_nueva:
            base_editable.append((nueva_pregunta_nueva.strip(), nueva_respuesta_nueva.strip()))
            st.success("✅ Pregunta agregada correctamente a la base local.")
        else:
            st.warning("⚠ Escribí una pregunta y su respuesta antes de agregar.")

    if st.button("🚪 Salir del modo edición", key=f"exit_{curso_seleccionado_por_el_usuario}"):
        st.session_state.edicion_activa = False
        st.info("🔒 Modo edición cerrado.")
        st.rerun()

st.divider()

# ==============================
# FUNCIONES AUXILIARES FINALES
# ==============================
if st.button("🧹 Limpiar chat", key="limpiar_chat"):
    st.session_state.historial = []
    st.info("💬 Historial limpiado correctamente.")

st.caption("💡 Los cambios en la base local se mantienen mientras la aplicación esté activa. Si se reinicia, se volverá a la base original definida en el código.")

# ==============================
# MANTENER SESIÓN VIVA
# ==============================
def mantener_sesion_activa_en_segundo_plano():
    """
    Hilo que mantiene la sesión viva actualizando una clave de sesión periódicamente.
    """
    while True:
        time.sleep(300)
        st.session_state["keepalive"] = time.time()

if "keepalive_thread" not in st.session_state:
    hilo_mantener = threading.Thread(target=mantener_sesion_activa_en_segundo_plano, daemon=True)
    hilo_mantener.start()
    st.session_state["keepalive_thread"] = True

