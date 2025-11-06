import streamlit as st
import requests
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "TU_API_KEY_AQUI"  # 🔑 reemplazá con tu API Key real

# ==============================
# BASE DE CONOCIMIENTO LOCAL
# ==============================
BASE_LOCAL = [
    ("como se llama la directora?", "Marisa Brizzio"),
    ("donde queda el colegio?", "El Colegio Mercedaria se encuentra en Córdoba, Argentina."),
    ("cuantos años tiene la secundaria?", "La secundaria tiene 6 años en total."),
    ("que orientación tiene el colegio?", "El colegio ofrece orientaciones en Informática y Humanidades.")
]

def obtener_contexto():
    """Convierte la base local en texto legible para enviar al modelo."""
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(BASE_LOCAL, start=1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto.strip()

# ==============================
# FUNCIONES DE IA
# ==============================
def consultar_deepseek(pregunta, api_key, contexto):
    """Consulta a DeepSeek sin streaming, usando la base local completa."""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sos MercedarIA, el asistente educativo oficial del Colegio Mercedaria. "
                    "Usá la base de conocimiento local para responder preguntas. "
                    "Si no está en la base, usá tu conocimiento general, pero mantené un tono educativo. "
                    "No digas 'según la base de conocimiento'."
                )
            },
            {
                "role": "user",
                "content": f"{contexto}\n\nPregunta: {pregunta}"
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error al conectar con DeepSeek: {e}"

# ==============================
# FUNCIONES EXTRA
# ==============================
def mostrar_fecha_hora():
    return datetime.now().strftime("📅 Hoy es %A %d de %B de %Y - %H:%M:%S")

# ==============================
# INTERFAZ STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")

st.title("🎓 Chat con MercedarIA")
st.caption("Asistente educativo del Colegio Mercedaria")

# Inicializar sesión
if "historial" not in st.session_state:
    st.session_state.historial = []
if "contexto" not in st.session_state:
    st.session_state.contexto = obtener_contexto()

# Entrada de usuario
st.subheader("💬 Escribí tu pregunta:")
pregunta = st.text_input("")

if st.button("Enviar"):
    if pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, st.session_state.contexto)
        st.session_state.historial.append(("🤖 MercedarIA", respuesta))

# Mostrar conversación
for rol, msg in st.session_state.historial:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"🧍 **{rol}:** {msg}")
    else:
        st.markdown(f"🧠 <span style='color:#00FFAA'><b>{rol}:</b></span> {msg}", unsafe_allow_html=True)

st.divider()
st.subheader("🧩 Herramientas adicionales")

col1, col2 = st.columns(2)

with col1:
    if st.button("📅 Ver fecha y hora"):
        st.success(mostrar_fecha_hora())

with col2:
    with st.expander("➕ Editar base local (solo visible para el creador)"):
        st.info("Podés agregar nuevas preguntas o editar las existentes aquí abajo.")
        for i, (p, r) in enumerate(BASE_LOCAL):
            BASE_LOCAL[i] = (
                st.text_input(f"Pregunta {i+1}", p, key=f"preg_{i}"),
                st.text_area(f"Respuesta {i+1}", r, key=f"resp_{i}")
            )
        if st.button("💾 Actualizar base"):
            st.session_state.contexto = obtener_contexto()
            st.success("✅ Base actualizada correctamente.")

st.caption("Las preguntas y respuestas están guardadas dentro del programa (no en archivo externo).")
