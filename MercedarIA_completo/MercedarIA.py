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

# ==============================
# BASE DE CONOCIMIENTO POR CURSO
# ==============================
BASE_GENERAL = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quien eres", "Soy MercedarIA, tu asistente del colegio."),
    ("como te llamas", "Me llamo MercedarIA, tu asistente virtual."),
    ("como estas", "Estoy funcionando perfectamente, gracias por preguntar."),
    ("adios", "¡Hasta luego! Que tengas un buen día."),
    ("quien es la directora", "La directora es Marisa Brizzio."),
    ("cuando son los recreos", "Turno mañana: 8:35, 10:00, 11:35. Turno tarde: 14:40, 16:05, 17:50."),
    ("donde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456."),
    ("cuando empieza el ciclo lectivo", "El ciclo lectivo comienza el primer día hábil de marzo."),
    ("cuando terminan las clases", "Generalmente a mediados de diciembre."),
]

BASES_ESPECIFICAS = {
    "1° A": [
        ("¿Qué materias tengo?", "Biología, Educación en Artes Visuales, Lengua y Literatura, Física, Geografía, Educación Tecnológica, Matemática, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física y Educación Tecnológica."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")],
    "1° B": [
        ("¿Qué materias tengo?", "Física, Matemática, Educación en Artes Visuales, Inglés, Educación Religiosa Escolar, Lengua y Literatura, Geografía, Ciudadanía y Participación, Educación Tecnológica, Biología y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Tecnológica y Educación Física."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")],
    "2° A": [
        ("¿Qué materias tengo?", "Matemática, Lengua y Literatura, Educación Religiosa Escolar, Música, Historia, Educación Tecnológica, Química, Computación, Ciudadanía y Participación, Biología, Inglés y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")],
    "2° B": [
        ("¿Qué materias tengo?", "Música, Historia, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés, Matemática, Lengua y Literatura, Educación Tecnológica, Química, Biología y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")],
    "3° A": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Inglés, Historia, Geografía, Química, Educación Tecnológica, Física, Educación Religiosa Escolar, Formación para la Vida y el Trabajo, Matemática, Educación Artística Visual, Música, Computación y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física y Formación para la Vida y el Trabajo."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")],
    "3° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Formación para la Vida y el Trabajo, Física, Historia, Geografía, Educación Artística Visual, Música, Matemática, Educación Tecnológica, Química, Computación, Educación Religiosa Escolar, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")],
    "4° A": [
        ("¿Qué materias tengo?", "Historia, Lengua y Literatura, Biología, Educación Religiosa Escolar, Matemática, Geografía, Educación Artística, Formación para la Vida y el Trabajo, Tecnologías de la Información y la Comunicación (TIC), Sociedad, Cultura y Comunicación, Antropología, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")],
    "4° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Biología, Educación Religiosa Escolar, Historia, Tecnología y Lenguajes de Programación, Geografía, Matemática, Sistemas Digitales de Información, Formación para la Vida y el Trabajo, Educación Artística, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")],
    "5° A": [
        ("¿Qué materias tengo?", "Metodología, Historia, Física, Geografía, Arte Cultural y Social, Educación Religiosa Escolar, Lengua y Literatura, Formación para la Vida y el Trabajo, Matemática, Educación Física, Psicología, Sociología e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Psicología, Sociología e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")],
    "5° B": [
        ("¿Qué materias tengo?", "Robótica, Música, Física, Matemática, Historia, Lengua y Literatura, Formación para la Vida y el Trabajo, Sistemas Digitales de Información, Geografía, Psicología, Educación Física, Desarrollo de Soluciones Informáticas e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Sistemas Digitales de Información, Desarrollo de Soluciones Informáticas e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")],
    "6° A": [
        ("¿Qué materias tengo?", "Ciudadanía y Política, Economía Política, Matemática, Geografía, Filosofía, Química, Lengua y Literatura, Historia, Educación Religiosa Escolar, Sociedad, Cultura y Comunicación, Teatro, Formación para la Vida y el Trabajo, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Sociedad, Cultura y Comunicación e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")],
    "6° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Comunicación Audiovisual, Desarrollo de Soluciones Informáticas, Informática Aplicada, Filosofía, Formación para la Vida y el Trabajo, Química, Matemática, Ciudadanía y Política, Educación Religiosa Escolar, Teatro, Educación Física, Aplicaciones Informáticas e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Aplicaciones Informáticas e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")],
}

# ==============================
# FUNCIONES
# ==============================
def obtener_contexto(lista):
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(lista, 1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto


def consultar_deepseek(pregunta, api_key, contexto):
    """Consulta a DeepSeek con la base de conocimiento como contexto"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",
             "content": (
                 """Sos MercedarIA, el asistente educativo del Colegio Mercedaria.
                 Usá la base de conocimiento local para responder preguntas del colegio.
                 Si la información no está disponible, respondé de manera educativa y correcta.
                 Podés responder preguntas generales, pero mantené un tono adecuado para estudiantes."""
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

# ==============================
# CONFIG STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")

st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption("Basado en conocimiento local + IA DeepSeek")

# ==============================
# SELECCIÓN DE CURSO
# ==============================
CURSOS = ["General"] + list(BASES_ESPECIFICAS.keys())

curso_seleccionado = st.sidebar.selectbox(
    "📘 Seleccioná el curso",
    CURSOS,
    index=0
)

# Inicializar bases en sesión
if "bases" not in st.session_state:
    st.session_state.bases = {
        "General": BASE_GENERAL.copy(),
        **{curso: BASES_ESPECIFICAS.get(curso, []).copy() for curso in BASES_ESPECIFICAS}
    }
if "historial" not in st.session_state:
    st.session_state.historial = []
if "edicion_activa" not in st.session_state:
    st.session_state.edicion_activa = False

# Combinar base general + específica
base_completa = BASE_GENERAL + st.session_state.bases.get(curso_seleccionado, [])
contexto = obtener_contexto(base_completa)

# ==============================
# CHAT
# ==============================
st.subheader(f"💬 Chat con MercedarIA ({curso_seleccionado})")
pregunta = st.text_input("Escribí tu pregunta:")

if st.button("Enviar", key="enviar"):
    if pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        pregunta_normalizada = pregunta.lower().strip()
        respuesta = None

        # Buscar coincidencia local (base general + curso)
        for p, r in base_completa:
            if p.lower() in pregunta_normalizada:
                respuesta = r
                break

        # Si no hay coincidencia → consulta a DeepSeek
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

# ==============================
# EDICIÓN PROTEGIDA
# ==============================
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
    st.success(f"Modo edición activado para: {curso_seleccionado}")

    # Editar base específica (no la general)
    st.markdown(f"### ✏️ Editar base de {curso_seleccionado}")
    if curso_seleccionado == "General":
        base_editable = BASE_GENERAL
    else:
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
                st.rerun()
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
# FUNCIONES EXTRA
# ==============================
if st.button("🧹 Limpiar chat"):
    st.session_state.historial = []
    st.info("💬 Chat limpiado correctamente.")

st.caption("💡 Los cambios se mantienen mientras la app esté activa. Si se reinicia, se vuelve a la base original.")

# ==============================
# MANTENER SESIÓN VIVA
# ==============================
def mantener_sesion_viva():
    """Mantiene la sesión activa sin recargar la app."""
    while True:
        time.sleep(300)
        st.session_state["keepalive"] = time.time()

if "keepalive_thread" not in st.session_state:
    hilo = threading.Thread(target=mantener_sesion_viva, daemon=True)
    hilo.start()
    st.session_state["keepalive_thread"] = True

