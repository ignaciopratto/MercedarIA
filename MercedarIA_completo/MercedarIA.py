import streamlit as st
import requests
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # ⚠️ Reemplazá con tu API Key real
ADMIN_PASSWORD = "mercedaria2025"      # 🔒 Contraseña para editar la base

# ==============================
# BASE DE CONOCIMIENTO GENERAL
# ==============================
BASE_GENERAL = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quien eres", "Soy MercedarIA, tu asistente del colegio."),
    ("como te llamas", "Me llamo MercedarIA, tu asistente virtual."),
    ("como estas", "Estoy funcionando perfectamente, gracias por preguntar."),
    ("adios", "¡Hasta luego! Que tengas un buen día."),
    ("cuando empiezan las clases", "Las clases comienzan el primer día hábil de marzo."),
    ("cuando terminan las clases", "Las clases terminan a mediados de diciembre."),
    ("cuando son las vacaciones de invierno", "Empiezan a mediados de julio y duran dos semanas."),
    ("cuando son las vacaciones de verano", "Empiezan en diciembre y terminan en marzo."),
    ("quien es la directora", "La directora es Marisa Brizzio."),
    ("donde esta la biblioteca", "Está en el primer piso, al lado de preceptoría."),
    ("cuanto dura un módulo de clase", "Cada módulo dura 40 minutos."),
    ("que pasa si llego tarde", "Debés avisar en preceptoría y se registra como tardanza."),
    ("puedo usar el celular", "No, salvo permiso del profesor o autoridad."),
    ("que hago si me enfermo en clase", "Avisá al profesor y luego en preceptoría."),
    ("que hago si pierdo un objeto", "Preguntá en preceptoría o dirección."),
    ("cuando es la entrega de boletines", "Al final de cada cuatrimestre."),
    ("donde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456."),
]

# ==============================
# BASES ESPECÍFICAS POR CURSO
# ==============================
BASES_ESPECIFICAS = {
    "1° A": [("que materias tengo", "Biología, Educación en Artes Visuales, Lengua y Literatura, Física, Geografía, Educación Tecnológica, Matemática, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés y Educación Física."),
             ("cuáles son mis contraturnos", "Educación Física y Educación Tecnológica."),
             ("a qué hora son los recreos", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")],
    "1° B": [("que materias tengo", "Física, Matemática, Educación en Artes Visuales, Inglés, Educación Religiosa Escolar, Lengua y Literatura, Geografía, Ciudadanía y Participación, Educación Tecnológica, Biología y Educación Física."),
             ("cuáles son mis contraturnos", "Educación Tecnológica y Educación Física."),
             ("a qué hora son los recreos", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")],
    # (Los demás cursos los agregás igual que estos)
}

# ==============================
# FUNCIONES
# ==============================
def obtener_contexto(lista_general, lista_especifica=None):
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(lista_general, 1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    if lista_especifica:
        contexto += "\nBASE DE CONOCIMIENTO ESPECÍFICA DEL CURSO:\n\n"
        for i, (p, r) in enumerate(lista_especifica, 1):
            contexto += f"Pregunta curso {i}: {p}\nRespuesta curso {i}: {r}\n\n"
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
                 Usá la base de conocimiento local y la específica del curso para responder preguntas.
                 Si la información no está disponible, respondé de manera educativa y correcta.
                 Podés responder preguntas generales de otros temas si son apropiadas para estudiantes."""
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
# INTERFAZ STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")

st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption("Basado en conocimiento local + IA DeepSeek")

# Estado persistente
if "curso" not in st.session_state:
    st.session_state.curso = "General"
if "base_datos" not in st.session_state:
    st.session_state.base_datos = BASE_GENERAL.copy()
if "historial" not in st.session_state:
    st.session_state.historial = []
if "edicion_activa" not in st.session_state:
    st.session_state.edicion_activa = False

# Selector de curso
st.subheader("📘 Elegí tu curso")
cursos = ["General"] + list(BASES_ESPECIFICAS.keys())
curso_sel = st.selectbox("Seleccioná tu curso:", cursos, index=cursos.index(st.session_state.curso))

if curso_sel != st.session_state.curso:
    st.session_state.curso = curso_sel
    st.session_state.historial = []
    st.rerun()  # 🔁 Actualiza al instante

# Armar contexto
base_curso = BASES_ESPECIFICAS.get(st.session_state.curso, [])
contexto = obtener_contexto(BASE_GENERAL, base_curso)

# ==============================
# CHAT
# ==============================
st.subheader("💬 Chat con MercedarIA")
pregunta = st.text_input("Escribí tu pregunta:")

if st.button("Enviar"):
    if pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        pregunta_normalizada = pregunta.lower().strip()
        respuesta = None

        # Buscar coincidencia local
        for p, r in BASE_GENERAL + base_curso:
            if p.lower() in pregunta_normalizada:
                respuesta = r
                break

        # Si no hay coincidencia → consulta a DeepSeek
        if not respuesta:
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)

        st.session_state.historial.append(("🤖 MercedarIA", respuesta))
        st.rerun()  # 🔁 Actualiza chat inmediatamente

# Mostrar historial
for rol, msg in st.session_state.historial:
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
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta.")
else:
    st.success(f"Modo edición activado ({st.session_state.curso})")

    # Lista de preguntas editables
    base_objetivo = BASES_ESPECIFICAS.get(st.session_state.curso, BASE_GENERAL)

    for i, (p, r) in enumerate(base_objetivo):
        col1, col2, col3 = st.columns([4, 5, 1])
        with col1:
            nueva_p = st.text_input(f"Pregunta {i+1}", p, key=f"p_{i}")
        with col2:
            nueva_r = st.text_area(f"Respuesta {i+1}", r, key=f"r_{i}")
        with col3:
            if st.button("🗑", key=f"del_{i}"):
                base_objetivo.pop(i)
                st.rerun()
        base_objetivo[i] = (nueva_p, nueva_r)

    # Agregar nueva pregunta
    st.markdown("---")
    nueva_pregunta = st.text_input("➕ Nueva pregunta", key="nueva_p")
    nueva_respuesta = st.text_area("Respuesta", key="nueva_r")
    if st.button("Agregar a la base"):
        if nueva_pregunta and nueva_respuesta:
            base_objetivo.append((nueva_pregunta.strip(), nueva_respuesta.strip()))
            st.success("✅ Pregunta agregada correctamente.")
            st.rerun()
        else:
            st.warning("⚠ Escribí una pregunta y su respuesta antes de agregar.")

    if st.button("🚪 Salir del modo edición"):
        st.session_state.edicion_activa = False
        st.info("🔒 Modo edición cerrado.")
        st.rerun()

st.divider()

# ==============================
# FUNCIONES EXTRA
# ==============================
if st.button("🧹 Limpiar chat"):
    st.session_state.historial = []
    st.rerun()

st.caption("💡 Todos los cambios se mantienen temporalmente mientras la app esté activa. Si se reinicia, vuelve la base original.")

