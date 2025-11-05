import os
import json
import requests
import streamlit as st
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
ARCHIVO = "preguntas_respuestas.txt"  # archivo local
DEEPSEEK_API_KEY = "TU_API_KEY_AQUI"  # 🔑 reemplazá con tu API Key real

# ==============================
# FUNCIONES DE BASE DE CONOCIMIENTO
# ==============================

def cargar_preguntas_respuestas(nombre_archivo):
    """Carga todas las preguntas y respuestas del archivo."""
    lista = []
    if not os.path.exists(nombre_archivo):
        return lista
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            if ";" in linea:
                partes = linea.strip().split(";", 1)
                if len(partes) == 2:
                    lista.append((partes[0].strip(), partes[1].strip()))
    return lista


def obtener_contexto_completo(nombre_archivo):
    """Convierte toda la base de conocimiento en un bloque de texto para el prompt."""
    if not os.path.exists(nombre_archivo):
        return "No hay base de conocimiento cargada."
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        for i, linea in enumerate(archivo, start=1):
            if ";" in linea:
                partes = linea.strip().split(";", 1)
                if len(partes) == 2:
                    contexto += f"Pregunta {i}: {partes[0].strip()}\n"
                    contexto += f"Respuesta {i}: {partes[1].strip()}\n\n"
    return contexto.strip()


def guardar_pregunta_respuesta(pregunta, respuesta):
    """Guarda una nueva pregunta y respuesta al archivo."""
    try:
        with open(ARCHIVO, "a", encoding="utf-8") as f:
            f.write(f"\n{pregunta};{respuesta}")
        return True
    except Exception:
        return False

# ==============================
# CONSULTA A DEEPSEEK (STREAMING)
# ==============================

def consultar_deepseek_streaming(pregunta, api_key, contexto):
    """Envía la base completa + pregunta al modelo DeepSeek y muestra respuesta en streaming."""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    mensajes = [
        {
            "role": "system",
            "content": (
                "Sos MercedarIA, asistente educativo del Colegio Mercedaria. "
                "Respondé con lenguaje claro, educativo y breve. "
                "Usá el contexto local del colegio cuando corresponda. "
                "No menciones si la respuesta proviene de la base de conocimiento."
            )
        },
        {
            "role": "user",
            "content": f"{contexto}\n\nPregunta: {pregunta}"
        }
    ]

    data = {
        "model": "deepseek-chat",
        "messages": mensajes,
        "max_tokens": 500,
        "temperature": 0.7,
        "stream": True
    }

    try:
        respuesta = ""
        message_placeholder = st.empty()
        with requests.post(url, headers=headers, json=data, stream=True, timeout=60) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                payload = line[len("data: "):].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        respuesta += delta
                        message_placeholder.markdown(f"🤖 **MercedarIA:** {respuesta}")
                except json.JSONDecodeError:
                    continue

        if not respuesta.strip():
            return "⚠️ No se recibió texto del modelo. Revisá tu API key o límites de uso."
        return respuesta

    except requests.exceptions.RequestException as e:
        return f"❌ Error de conexión: {e}"

# ==============================
# FUNCIONES EXTRA
# ==============================

def mostrar_fecha_hora():
    return datetime.now().strftime("📅 Hoy es %A %d de %B de %Y - %H:%M:%S")


# ==============================
# INTERFAZ STREAMLIT
# ==============================

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")

st.title("🎓 Chatbot del Colegio Mercedaria")
st.caption("IA con base de conocimiento local + DeepSeek AI")

# Cargar base al iniciar
if "contexto" not in st.session_state:
    st.session_state.contexto = obtener_contexto_completo(ARCHIVO)
    st.session_state.historial = []

st.divider()
st.subheader("💬 Chat con MercedarIA")

pregunta_usuario = st.text_input("Escribí tu pregunta:")

if st.button("Enviar"):
    if pregunta_usuario.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta_usuario))
        respuesta = consultar_deepseek_streaming(
            pregunta_usuario, DEEPSEEK_API_KEY, st.session_state.contexto
        )
        st.session_state.historial.append(("🤖 MercedarIA", respuesta))

# Mostrar historial
for rol, msg in st.session_state.historial:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"**{rol}:** {msg}")
    else:
        st.markdown(f"<span style='color:#00FFAA'><b>{rol}:</b></span> {msg}", unsafe_allow_html=True)

st.divider()
st.subheader("🧩 Herramientas adicionales")

col1, col2 = st.columns(2)
with col1:
    if st.button("Ver fecha y hora"):
        st.success(mostrar_fecha_hora())

with col2:
    with st.expander("➕ Agregar nueva pregunta/respuesta"):
        nueva_p = st.text_input("Nueva pregunta:")
        nueva_r = st.text_area("Nueva respuesta:")
        if st.button("Guardar en base"):
            if nueva_p.strip() and nueva_r.strip():
                if guardar_pregunta_respuesta(nueva_p, nueva_r):
                    st.success("✅ Guardado correctamente.")
                    st.session_state.contexto = obtener_contexto_completo(ARCHIVO)
                else:
                    st.error("❌ Error al guardar.")
            else:
                st.warning("⚠️ Completá ambos campos.")

st.caption("Todos los datos locales se guardan en preguntas_respuestas.txt")
