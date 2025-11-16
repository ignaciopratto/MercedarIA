import streamlit as st
import requests
import threading
import time
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"   # ⚠️ reemplazá con tu API key real
ADMIN_PASSWORD = "mercedaria2025"      # 🔒 contraseña para editar la base

# APIs externas
API_USERS = "https://mi-insm.onrender.com/users"
API_TASKS = "https://mi-insm.onrender.com/tasks"
API_COURSES = "https://mi-insm.onrender.com/courses"


# ==============================
# BASE LOCAL GENERAL
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


# ==============================
# BASE LOCAL POR CURSO
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


# -------------------------------------------------------------------
# ==============================
# FUNCIONES AUXILIARES
# ==============================
# -------------------------------------------------------------------

def obtener_contexto(lista):
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(lista, 1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto


def consultar_deepseek(pregunta, api_key, contexto):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",
             "content": (
                 "Sos MercedarIA, el asistente educativo del Colegio Mercedaria. "
                 "Usá la base de conocimiento local para responder preguntas del colegio. "
                 "Si la información no está disponible, respondé de manera educativa y correcta."
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


# -------------------------------------------------------------------
# ==============================
# CONFIG STREAMLIT
# ==============================
# -------------------------------------------------------------------

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")


# -------------------------------------------------------------------
# ==============================
# LOGIN POR DNI
# ==============================
# -------------------------------------------------------------------

if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.tasks = []
    st.session_state.courses = []


st.title("🔐 Inicio de sesión")

if st.session_state.user is None:
    dni = st.text_input("Ingresá tu DNI para continuar:")

    if st.button("Ingresar"):
        try:
            users = requests.get(API_USERS).json()
            usuario = next((u for u in users if str(u["dni"]) == dni), None)

            if usuario:
                st.session_state.user = usuario
                st.success(f"Bienvenido {usuario['name']} ({usuario['course']})")

                # Cargar tareas y cursos
                st.session_state.tasks = requests.get(API_TASKS).json()
                st.session_state.courses = requests.get(API_COURSES).json()

                st.experimental_rerun()

            else:
                st.error("DNI no encontrado en la base de datos.")
        except Exception as e:
            st.error(f"❌ Error al conectar con la API: {e}")

    st.stop()  # Impide que avance si no inicia sesión


# -------------------------------------------------------------------
# ==============================
# DESPUÉS DEL LOGIN → CHAT COMPLETO
# ==============================
# -------------------------------------------------------------------

st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption(f"Alumno: **{st.session_state.user['name']}** — Curso: **{st.session_state.user['course']}**")


# ==============================
# SESIONES INTERNAS
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


# ==============================
# SELECCIÓN DE CURSO
# ==============================
CURSOS = ["General"] + list(BASES_ESPECIFICAS.keys())

curso_seleccionado = st.sidebar.selectbox("📘 Seleccioná el curso", CURSOS, index=0)

if curso_seleccionado not in st.session_state.bases:
    st.session_state.bases[curso_seleccionado] = []

base_completa = BASE_GENERAL + st.session_state.bases[curso_seleccionado]
contexto = obtener_contexto(base_completa)


# -------------------------------------------------------------------
# ==============================
# CHAT
# ==============================
# -------------------------------------------------------------------
st.subheader(f"💬 Chat con MercedarIA ({curso_seleccionado})")

pregunta = st.text_input("Escribí tu pregunta:")
enviar = st.button("Enviar", key=f"enviar_{curso_seleccionado}")

if enviar:
    if pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        pregunta_normalizada = pregunta.lower().strip()
        respuesta = None

        # ----------------------------------------------
        # 1) CONSULTA DE TAREAS (del curso + personales)
        # ----------------------------------------------
        if "tarea" in pregunta_normalizada or "tareas" in pregunta_normalizada:
            curso_usuario = st.session_state.user["course"]
            id_usuario = st.session_state.user["id"]

            tareas_curso = [t for t in st.session_state.tasks if t["course"] == curso_usuario]
            tareas_personales = [t for t in st.session_state.tasks if t.get("user_id") == id_usuario]

            texto = "📘 **Tareas del curso:**\n"
            if tareas_curso:
                for t in tareas_curso:
                    texto += f"- {t['title']}\n"
            else:
                texto += "- No hay tareas cargadas.\n"

            texto += "\n👤 **Tus tareas personales:**\n"
            if tareas_personales:
                for t in tareas_personales:
                    texto += f"- {t['title']}\n"
            else:
                texto += "- No tenés tareas personales.\n"

            respuesta = texto

        # ----------------------------------------------
        # 2) CONSULTA DE PROFESORES
        # ----------------------------------------------
        elif "profesor" in pregunta_normalizada or "docente" in pregunta_normalizada:
            curso_usuario = st.session_state.user["course"]
            registros = [c for c in st.session_state.courses if c["course"] == curso_usuario]

            if "de" in pregunta_normalizada:
                materia = pregunta_normalizada.split("de", 1)[1].strip()
                encontrado = next((c for c in registros if materia in c["subject"].lower()), None)

                if encontrado:
                    respuesta = (
                        f"👨‍🏫 El profesor de **{encontrado['subject']}** es:\n"
                        f"📧 **{encontrado['teacher']}**"
                    )
                else:
                    respuesta = "No encontré profesor para esa materia."
            else:
                respuesta = "👨‍🏫 **Profesores de tu curso:**\n\n"
                for c in registros:
                    respuesta += f"- **{c['subject']}** → {c['teacher']}\n"

        # ------------------------------------------------
        # 3) CONSULTA CON BASE LOCAL (PREGUNTAS PREDEFINIDAS)
        # ------------------------------------------------
        if not respuesta:
            for p, r in base_completa:
                if p.lower() in pregunta_normalizada:
                    respuesta = r
                    break

        # ----------------------------------------------
        # 4) CONSULTA A DEEPSEEK (IA)
        # ----------------------------------------------
        if not respuesta:
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)

        st.session_state.historial.append(("🤖 MercedarIA", respuesta))


# Mostrar historial
for rol, msg in st.session_state.historial[-20:]:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"🧍 *{rol}:* {msg}")
    else:
        st.markdown(f"🧠 <span style='color:#00FFAA'><b>{rol}:</b></span> {msg}", unsafe_allow_html=True)

st.divider()


# -------------------------------------------------------------------
# ==============================
# PANEL DE EDICIÓN PROTEGIDO
# ==============================
# -------------------------------------------------------------------

st.subheader("🧩 Panel de Edición (solo personal autorizado)")

if not st.session_state.edicion_activa:
    password = st.text_input("🔒 Ingresá la contraseña para editar", type="password", key="pass")
    if st.button("Acceder", key="login"):
        if password == ADMIN_PASSWORD:
            st.session_state.edicion_activa = True
            st.success("✅ Acceso concedido.")
        else:
            st.error("❌ Contraseña incorrecta.")
else:
    st.success(f"Modo edición activado para: {curso_seleccionado}")

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
    nueva_pregunta = st.text_input("➕ Nueva pregunta", key=f"nueva_p_{curso_seleccionado}")
    nueva_respuesta = st.text_area("Respuesta", key=f"nueva_r_{curso_seleccionado}")
    if st.button("Agregar a la base", key=f"add_{curso_seleccionado}"):
        if nueva_pregunta and nueva_respuesta:
            base_editable.append((nueva_pregunta.strip(), nueva_respuesta.strip()))
            st.success("✅ Pregunta agregada correctamente.")
        else:
            st.warning("⚠ Escribí una pregunta y su respuesta antes de agregar.")

    if st.button("🚪 Salir del modo edición", key=f"exit_{curso_seleccionado}"):
        st.session_state.edicion_activa = False
        st.info("🔒 Modo edición cerrado.")

st.divider()


# ==============================
# LIMPIAR CHAT
# ==============================
if st.button("🧹 Limpiar chat", key="clear"):
    st.session_state.historial = []
    st.info("💬 Chat limpiado correctamente.")

st.caption("💡 Los cambios se mantienen mientras la app esté activa. Si se reinicia, se vuelve a la base original.")


# -------------------------------------------------------------------
# ==============================
# MANTENER SESIÓN VIVA
# ==============================
# -------------------------------------------------------------------

def mantener_sesion_viva():
    while True:
        time.sleep(300)
        st.session_state["keepalive"] = time.time()

if "keepalive_thread" not in st.session_state:
    hilo = threading.Thread(target=mantener_sesion_viva, daemon=True)
    hilo.start()
    st.session_state["keepalive_thread"] = True

