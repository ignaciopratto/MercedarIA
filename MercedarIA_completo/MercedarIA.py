import streamlit as st
import requests
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "TU_API_KEY_AQUI"  # ⚠️ reemplazá con tu API key real

# ==============================
# BASE DE CONOCIMIENTO LOCAL (editable)
# ==============================
BASE_INICIAL = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quien eres", "Soy un asistente IA diseñado para responder preguntas de la escuela."),
    ("como te llamas", "Me llamo MercedarIA, soy tu asistente virtual, estoy aquí para ayudarte en lo que necesites."),
    ("como estas", "Estoy funcionando perfectamente, gracias por preguntar."),
    ("adios", "¡Hasta luego! Que tengas un buen día."),
    ("cuando empiezan las clases", "Las clases comienzan el primer día hábil de marzo."),
    ("cuando terminan las clases", "Las clases terminan a mediados de diciembre."),
    ("cuando son las vacaciones de invierno", "Empiezan a mediados de julio y duran dos semanas."),
    ("cuando son las vacaciones de verano", "Empiezan en diciembre y terminan en marzo."),
    ("quien es el director", "El director es el responsable de la institución educativa. Su nombre es Marisa."),
    ("donde esta la biblioteca", "La biblioteca está en el primer piso del colegio, al lado de la preceptoría."),
    ("cuando es el proximo examen", "Consultá el calendario escolar o preguntale a tu profesor."),
    ("cual es el proximo acto escolar", "Por favor especificá."),
    ("cuanto dura un modulo de clase", "Cada módulo dura 40 minutos."),
    ("que pasa si llego tarde", "Debés avisar en la preceptoría y puede quedar registrado como tardanza."),
    ("puedo usar el celular", "No, el uso del celular está estrictamente prohibido, salvo con permiso del profesor o autoridad."),
    ("que hago si me enfermo en clase", "Debés avisar al profesor y luego dirigirte a la preceptoría para avisar a tus padres/tutor."),
    ("que hago si pierdo un objeto", "Debés preguntar en preceptoría o en dirección, allí guardan los objetos perdidos."),
    ("cuando es la entrega de boletines", "Generalmente al final de cada cuatrimestre."),
    ("cuando son los recreos", "En el turno mañana los recreos son a las 8:35, 10:00 y 11:35; en el turno tarde son a las 14:40, 16:05 y 17:50."),
    ("como se llama la directora", "Marisa Brizzio."),
    ("donde queda la escuela", "Ciudad de Arroyito, Córdoba, en la calle 9 de Julio 456.")
]

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
            {
                "role": "system",
                "content": (
                    "Sos MercedarIA, el asistente educativo oficial del Colegio Mercedaria. "
                    "Usá la base de conocimiento local para responder preguntas sobre el colegio. "
                    "Si la pregunta no está en la base, respondé con tu conocimiento general pero mantené un tono educativo."
                )
            },
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


def mostrar_fecha_hora():
    return datetime.now().strftime("📅 Hoy es %A %d de %B de %Y - %H:%M:%S")

# ==============================
# INTERFAZ STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")

st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption("Basado en conocimiento local + IA DeepSeek")

# Inicializar datos persistentes
if "base_datos" not in st.session_state:
    st.session_state.base_datos = BASE_INICIAL.copy()
if "historial" not in st.session_state:
    st.session_state.historial = []

contexto = obtener_contexto(st.session_state.base_datos)

# ==============================
# SECCIÓN DE CHAT
# ==============================
st.subheader("💬 Chat con MercedarIA")
pregunta = st.text_input("Escribí tu pregunta:")

if st.button("Enviar"):
    if pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        pregunta_normalizada = pregunta.lower().strip()

        # Buscar coincidencia en base local
        respuesta = None
        for p, r in st.session_state.base_datos:
            if p.lower() in pregunta_normalizada:
                respuesta = r
                break

        if not respuesta:
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)

        st.session_state.historial.append(("🤖 MercedarIA", respuesta))

# Mostrar conversación
for rol, msg in st.session_state.historial:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"🧍 **{rol}:** {msg}")
    else:
        st.markdown(f"🧠 <span style='color:#00FFAA'><b>{rol}:</b></span> {msg}", unsafe_allow_html=True)

st.divider()

# ==============================
# SECCIÓN DE EDICIÓN DE BASE
# ==============================
st.subheader("🧩 Editar base de conocimiento")
st.markdown("Cualquier usuario puede agregar, modificar o eliminar preguntas directamente desde aquí.")

for i, (p, r) in enumerate(st.session_state.base_datos):
    col1, col2, col3 = st.columns([4, 5, 1])
    with col1:
        st.session_state.base_datos[i] = (
            st.text_input(f"Pregunta {i+1}", p, key=f"p_{i}"),
            st.text_area(f"Respuesta {i+1}", r, key=f"r_{i}")
        )
    with col3:
        if st.button("🗑️", key=f"del_{i}"):
            st.session_state.base_datos.pop(i)
            st.experimental_rerun()

# Agregar nueva
st.markdown("---")
nueva_pregunta = st.text_input("➕ Nueva pregunta")
nueva_respuesta = st.text_area("Respuesta")
if st.button("Agregar a la base"):
    if nueva_pregunta and nueva_respuesta:
        st.session_state.base_datos.append((nueva_pregunta.strip(), nueva_respuesta.strip()))
        st.success("✅ Pregunta agregada correctamente.")
        st.experimental_rerun()
    else:
        st.warning("⚠️ Escribí una pregunta y su respuesta antes de agregar.")

st.markdown("---")
if st.button("🧹 Limpiar chat"):
    st.session_state.historial = []
    st.rerun()

if st.button("📅 Ver fecha y hora"):
    st.info(mostrar_fecha_hora())

st.caption("💡 Todos los cambios se guardan temporalmente mientras la aplicación esté activa.")

