import streamlit as st
import requests
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # ⚠️ Reemplazá con tu API key real
ADMIN_PASSWORD = "mercedaria2025"

# ==============================
# BASE GENERAL
# ==============================
BASE_GENERAL = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quién eres", "Soy MercedarIA, el asistente virtual del Colegio Mercedaria."),
    ("cómo te llamas", "Me llamo MercedarIA, tu asistente virtual."),
    ("como estás", "Estoy funcionando perfectamente, gracias por preguntar."),
    ("adiós", "¡Hasta luego! Que tengas un buen día."),
    ("cuándo empiezan las clases", "Las clases comienzan el primer día hábil de marzo."),
    ("cuándo terminan las clases", "Las clases terminan a mediados de diciembre."),
    ("quién es la directora", "La directora es Marisa Brizzio."),
    ("dónde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456."),
    ("qué pasa si llego tarde", "Debés avisar en preceptoría y se registra como tardanza."),
]

# ==============================
# BASES ESPECÍFICAS POR CURSO
# ==============================
BASES_ESPECIFICAS = {
    "1° A": [
        ("qué materias tengo", "Biología, Educación en Artes Visuales, Lengua y Literatura, Física, Geografía, Educación Tecnológica, Matemática, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés y Educación Física."),
        ("cuáles son mis contraturnos", "Educación Física y Educación Tecnológica."),
        ("a qué hora son los recreos", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "1° B": [
        ("qué materias tengo", "Física, Matemática, Educación en Artes Visuales, Inglés, Educación Religiosa Escolar, Lengua y Literatura, Geografía, Ciudadanía y Participación, Educación Tecnológica, Biología y Educación Física."),
        ("cuáles son mis contraturnos", "Educación Tecnológica y Educación Física."),
        ("a qué hora son los recreos", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    # ... (agregá las demás divisiones aquí igual que antes)
}

# ==============================
# FUNCIONES
# ==============================
def obtener_contexto(base_general, base_curso):
    """Crea un contexto unificado con la base general + la del curso"""
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(base_general + base_curso, 1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto


def consultar_deepseek(pregunta, api_key, contexto):
    """Consulta a DeepSeek usando la base local como contexto"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",
             "content": (
                 "Sos MercedarIA, el asistente educativo del Colegio Mercedaria. "
                 "Usá la base de conocimiento local y la información del curso correspondiente para responder preguntas. "
                 "Si la información no está disponible, respondé de manera educativa y adecuada, sin decir que no la sabés."
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
# STREAMLIT APP
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")
st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption("Basado en conocimiento local + IA DeepSeek")

# Sesión
if "historial" not in st.session_state:
    st.session_state.historial = []
if "curso" not in st.session_state:
    st.session_state.curso = "General"
if "base_datos" not in st.session_state:
    st.session_state.base_datos = BASE_GENERAL.copy()

# ==============================
# SELECCIÓN DE CURSO
# ==============================
st.subheader("🏫 Seleccioná tu curso")
cursos_disponibles = ["General"] + list(BASES_ESPECIFICAS.keys())
curso = st.selectbox("Curso:", cursos_disponibles, index=cursos_disponibles.index(st.session_state.curso))

if curso != st.session_state.curso:
    st.session_state.curso = curso
    st.session_state.historial = []  # resetea chat al cambiar curso

base_curso = BASES_ESPECIFICAS.get(curso, [])
contexto = obtener_contexto(BASE_GENERAL, base_curso)

# ==============================
# CHAT
# ==============================
st.subheader(f"💬 Chat con MercedarIA ({curso})")
pregunta = st.text_input("Escribí tu pregunta:")

if st.button("Enviar"):
    if pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        pregunta_normalizada = pregunta.lower().strip()
        respuesta = None

        # Buscar coincidencia en bases (curso y general)
        for p, r in base_curso + BASE_GENERAL:
            if p.lower() in pregunta_normalizada:
                respuesta = r
                break

        if not respuesta:
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)

        st.session_state.historial.append(("🤖 MercedarIA", respuesta))

# Mostrar historial
for rol, msg in st.session_state.historial:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"🧍 *{rol}:* {msg}")
    else:
        st.markdown(f"🧠 <span style='color:#00FFAA'><b>{rol}:</b></span> {msg}", unsafe_allow_html=True)

# ==============================
# ADMIN (EDICIÓN)
# ==============================
st.divider()
st.subheader("🧩 Panel de edición (solo personal autorizado)")

if "edicion_activa" not in st.session_state:
    st.session_state.edicion_activa = False

if not st.session_state.edicion_activa:
    password = st.text_input("🔒 Ingresá la contraseña", type="password")
    if st.button("Acceder"):
        if password == ADMIN_PASSWORD:
            st.session_state.edicion_activa = True
            st.success("✅ Acceso concedido.")
        else:
            st.error("❌ Contraseña incorrecta.")
else:
    st.success("Modo edición activado")
    st.markdown(f"Editando la base de datos de: **{curso}**")

    base_actual = base_curso if curso != "General" else BASE_GENERAL

    for i, (p, r) in enumerate(base_actual):
        col1, col2, col3 = st.columns([4, 5, 1])
        with col1:
            nueva_p = st.text_input(f"Pregunta {i+1}", p, key=f"p_{curso}_{i}")
        with col2:
            nueva_r = st.text_area(f"Respuesta {i+1}", r, key=f"r_{curso}_{i}")
        with col3:
            if st.button("🗑", key=f"del_{curso}_{i}"):
                base_actual.pop(i)
                st.rerun()
        base_actual[i] = (nueva_p, nueva_r)

    st.markdown("---")
    nueva_pregunta = st.text_input("➕ Nueva pregunta", key=f"nueva_p_{curso}")
    nueva_respuesta = st.text_area("Respuesta", key=f"nueva_r_{curso}")
    if st.button("Agregar", key=f"add_{curso}"):
        if nueva_pregunta and nueva_respuesta:
            base_actual.append((nueva_pregunta.strip(), nueva_respuesta.strip()))
            st.success("✅ Pregunta agregada.")
        else:
            st.warning("⚠ Escribí ambos campos antes de agregar.")

    if st.button("🚪 Salir del modo edición"):
        st.session_state.edicion_activa = False
        st.info("🔒 Modo edición cerrado.")

# ==============================
# BOTÓN EXTRA
# ==============================
st.divider()
if st.button("🧹 Limpiar chat"):
    st.session_state.historial = []
    st.info("💬 Chat limpiado correctamente.")
