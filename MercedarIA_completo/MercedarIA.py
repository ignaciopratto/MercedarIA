import streamlit as st
import requests
import threading
import time
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = ""  # Colocar tu API key real
ADMIN_PASSWORD = "mercedaria2025"

# URLs de API externas
API_USERS = "https://mi-insm.onrender.com/users"
API_TASKS = "https://mi-insm.onrender.com/tasks"
API_COURSES = "https://mi-insm.onrender.com/courses"

# ==============================
# BASE LOCAL GENERAL (SE MANTIENE)
# ==============================
BASE_GENERAL = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quién eres", "Soy MercedarIA, tu asistente del Colegio Mercedaria."),
    ("cómo te llamas", "Me llamo MercedarIA, tu asistente virtual."),
    ("cómo estás", "Estoy funcionando perfectamente, gracias por preguntar."),
    ("adiós", "¡Hasta luego! Que tengas un buen día."),
    ("quién es la directora", "La directora es Marisa Brizzio."),
    ("cuándo son los recreos", "Turno mañana: 8:35, 10:00, 11:35. Turno tarde: 14:40, 16:05, 17:50."),
    ("dónde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456."),
    ("cuándo empieza el ciclo lectivo", "El ciclo lectivo comienza el primer día hábil de marzo."),
    ("cuándo terminan las clases", "Generalmente a mediados de diciembre."),
]

# ==============================
# BASES POR CURSO (SE MANTIENEN)
# ==============================
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
        ("¿Cuáles son mis contraturnos?", "Educación Física, Sistemas Digitales de Información, Desarrollo de Soluciones Informáticas e Inglés."),
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

# =====================================
# FUNCIÓN PARA ARMAR CONTEXTO A IA
# =====================================
def obtener_contexto(lista):
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(lista, 1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto
# =====================================
# CONSULTA A LA IA DEEPSEEK
# =====================================
def consultar_deepseek(pregunta, api_key, contexto):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",
             "content": (
                 "Sos MercedarIA, el asistente educativo del Colegio Mercedaria. "
                 "Usá exclusivamente la base de conocimiento local y los datos "
                 "de la API del colegio. Si la información no está disponible, "
                 "respondé de manera educativa, respetuosa y clara."
             )},
            {"role": "user", "content": f"{contexto}\n\nPregunta: {pregunta}"}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"❌ Error al conectar con DeepSeek: {e}"


# =====================================
# FUNCIONES DE API EXTERNA
# =====================================
def cargar_users():
    try:
        return requests.get(API_USERS, timeout=15).json()
    except:
        return []


def cargar_tasks():
    try:
        return requests.get(API_TASKS, timeout=15).json()
    except:
        return []


def cargar_courses():
    try:
        return requests.get(API_COURSES, timeout=15).json()
    except:
        return []


# =====================================
# FUNCIÓN PARA NORMALIZAR CURSO
# Entrada:  "1b", "1B", " 1 b "
# Salida:   "1° B"
# =====================================
def normalizar_curso(curso_raw):
    if not curso_raw:
        return None

    curso_raw = curso_raw.strip().lower()

    if len(curso_raw) < 2:
        return None

    numero = curso_raw[0]
    division = curso_raw[-1].upper()

    return f"{numero}° {division}"


# =====================================
# INICIALIZACIÓN STREAMLIT
# =====================================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")

st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption("Basado en conocimiento local + API del colegio + IA DeepSeek")

# =====================================
# LOGIN POR DNI
# =====================================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.subheader("🔐 Inicio de sesión")

    dni_ingresado = st.text_input("Ingresá tu DNI para continuar:")

    if st.button("Ingresar"):
        usuarios = cargar_users()

        usuario = next((u for u in usuarios if u["dni"] == dni_ingresado), None)

        if usuario:
            st.session_state.usuario = usuario
            st.success(f"Bienvenido/a {usuario['nombre']} {usuario['apellido']}.")
        else:
            st.error("❌ DNI no encontrado en la base de datos.")

    st.stop()


# =====================================
# DATOS DEL USUARIO YA LOGUEADO
# =====================================
usuario = st.session_state.usuario
email_usuario = usuario["email"]
curso_usuario_raw = usuario["curso"]
curso_usuario = normalizar_curso(curso_usuario_raw)

if not curso_usuario:
    st.error("❌ Error: No se pudo interpretar el curso del usuario.")
    st.stop()

st.info(f"📘 Estás en el curso: **{curso_usuario}**")
# =====================================
# INICIALIZAR BASES LOCALES
# (Se mantiene el sistema que ya tenías)
# =====================================
if "bases" not in st.session_state:
    st.session_state.bases = {
        "General": BASE_GENERAL.copy(),
        **{curso: BASES_ESPECIFICAS.get(curso, []).copy() for curso in BASES_ESPECIFICAS}
    }

if "historial" not in st.session_state:
    st.session_state.historial = []

if "edicion_activa" not in st.session_state:
    st.session_state.edicion_activa = False


# =====================================
# FORZAR QUE EL CHAT USE SIEMPRE EL CURSO DEL USUARIO (OPCIÓN A)
# =====================================
curso_seleccionado = curso_usuario  # 🔒 El alumno NO puede cambiar de curso.


# =====================================
# ARMAR CONTEXTO PARA LA IA
# =====================================
base_completa = BASE_GENERAL + st.session_state.bases.get(curso_seleccionado, [])
contexto = obtener_contexto(base_completa)


# =====================================
# CARGAR TAREAS Y CURSOS DESDE LA API
# =====================================
lista_tareas = cargar_tasks()
lista_cursos_api = cargar_courses()

# Filtrar tareas del curso
tareas_curso = [
    t for t in lista_tareas
    if t.get("curso", "").lower() == usuario["curso"].lower()
]

# Filtrar tareas personales (dos formas posibles)
tareas_personales = [
    t for t in lista_tareas
    if t.get("personal") is True or t.get("creador") == email_usuario
]

# Evitar duplicados si una tarea cumple ambas condiciones
ids_personales = {t["id"] for t in tareas_personales}
tareas_curso = [t for t in tareas_curso if t["id"] not in ids_personales]


# =====================================
# FUNCIÓN PARA MOSTRAR TAREAS EN EL CHAT
# =====================================
def obtener_texto_tareas():
    texto = ""

    # TAREAS DEL CURSO
    texto += "📚 **Tareas del curso:**\n"
    if tareas_curso:
        for t in tareas_curso:
            titulo = t.get("titulo", "Sin título")
            fecha = t.get("fecha_limite", "")
            texto += f"- {titulo} — *{fecha}*\n"
    else:
        texto += "*(No hay tareas cargadas para tu curso)*\n"

    texto += "\n"

    # TAREAS PERSONALES
    texto += "🧍‍♂️ **Tus tareas personales:**\n"
    if tareas_personales:
        for t in tareas_personales:
            titulo = t.get("titulo", "Sin título")
            fecha = t.get("fecha_limite", "")
            texto += f"- {titulo} — *{fecha}*\n"
    else:
        texto += "*(No tenés tareas personales cargadas)*\n"

    return texto


# =====================================
# FUNCIÓN PARA RESPONDER SOBRE PROFESORES
# =====================================
def obtener_profesores():
    curso_raw = usuario["curso"]  # ejemplo: "1b"

    materias = [
        c for c in lista_cursos_api
        if c.get("curso", "").lower() == curso_raw.lower()
    ]

    if not materias:
        return "❌ No se encontró información de profesores para tu curso."

    texto = "📘 **Profesores de tu curso:**\n\n"
    for m in materias:
        materia = m.get("materia", "Materia desconocida")
        profe = m.get("mail_profesor", "Sin profesor")
        texto += f"- **{materia}** — {profe}\n"

    return texto


# =====================================
# INTERFAZ DE CHAT
# =====================================
st.subheader(f"💬 Chat con MercedarIA ({curso_seleccionado})")

pregunta = st.text_input("Escribí tu pregunta:")

if st.button("Enviar"):
    if pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        pregunta_norm = pregunta.lower().strip()

        respuesta = None

        # Buscar en base local
        for p, r in base_completa:
            if p.lower() in pregunta_norm:
                respuesta = r
                break

        # Preguntar por tareas
        if not respuesta and ("tarea" in pregunta_norm or "tareas" in pregunta_norm):
            respuesta = obtener_texto_tareas()

        # Preguntar por profesores
        if not respuesta and ("profe" in pregunta_norm or "profesor" in pregunta_norm or "profesores" in pregunta_norm):
            respuesta = obtener_profesores()

        # Si falla, usar DeepSeek
        if not respuesta:
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)

        st.session_state.historial.append(("🤖 MercedarIA", respuesta))
# =====================================
# MOSTRAR HISTORIAL
# =====================================
for rol, msg in st.session_state.historial[-20:]:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"🧍 *{rol}:* {msg}")
    else:
        st.markdown(
            f"🧠 <span style='color:#00FFAA'><b>{rol}:</b></span> {msg}",
            unsafe_allow_html=True
        )

st.divider()


# =====================================
# PANEL DE EDICIÓN (PROFESORES Y ADMIN)
# =====================================
st.subheader("🧩 Panel de Edición (solo personal autorizado)")

if not st.session_state.edicion_activa:
    password = st.text_input("🔒 Ingresá la contraseña para editar", type="password")

    if st.button("Acceder"):
        if password == ADMIN_PASSWORD:
            st.session_state.edicion_activa = True
            st.success("✅ Acceso concedido.")
        else:
            st.error("❌ Contraseña incorrecta.")

else:
    st.success(f"Modo edición activado para el curso: {curso_seleccionado}")

    base_editable = st.session_state.bases[curso_seleccionado]

    for i, (p, r) in enumerate(base_editable):
        col1, col2, col3 = st.columns([4, 5, 1])

        with col1:
            nueva_p = st.text_input(f"Pregunta {i+1}", p, key=f"p_{curso_seleccionado}_{i}")

        with col2:
            nueva_r = st.text_area(f"Respuesta {i+1}", r, key=f"r_{curso_seleccionado}_{i}")

        with col3:
            if st.button("🗑", key=f"del_{curso_seleccionado}_{i}"):
                base_editable.pop(i)
                st.experimental_rerun()

        base_editable[i] = (nueva_p, nueva_r)

    st.markdown("---")

    nueva_pregunta = st.text_input("➕ Nueva pregunta")
    nueva_respuesta = st.text_area("Respuesta")

    if st.button("Agregar a la base"):
        if nueva_pregunta and nueva_respuesta:
            base_editable.append((nueva_pregunta.strip(), nueva_respuesta.strip()))
            st.success("✅ Pregunta agregada correctamente.")
        else:
            st.warning("⚠ Escribí una pregunta y su respuesta antes de agregar.")

    if st.button("🚪 Salir del modo edición"):
        st.session_state.edicion_activa = False
        st.info("🔒 Modo edición cerrado.")

st.divider()


# =====================================
# BOTÓN PARA LIMPIAR CHAT
# =====================================
if st.button("🧹 Limpiar chat"):
    st.session_state.historial = []
    st.info("💬 Chat limpiado correctamente.")

st.caption("💡 Los cambios se mantienen mientras la app esté activa. Si se reinicia, se restaura la base original.")


# =====================================
# MANTENER SESIÓN VIVA
# =====================================
def mantener_sesion_viva():
    while True:
        time.sleep(300)
        st.session_state["keepalive"] = time.time()

if "keepalive_thread" not in st.session_state:
    hilo = threading.Thread(target=mantener_sesion_viva, daemon=True)
    hilo.start()
    st.session_state.keepalive_thread = True
