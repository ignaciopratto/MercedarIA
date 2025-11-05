import os
import requests
from datetime import datetime
import streamlit as st

# ==============================
# CONFIGURACIÓN
# ==============================
ARCHIVO = "preguntas_respuestas.txt"
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # tu API Key de DeepSeek

# ==============================
# FUNCIONES BASE
# ==============================
def cargar_preguntas_respuestas(nombre_archivo):
    """Lee las preguntas y respuestas del archivo local."""
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


def obtener_contexto_archivo(nombre_archivo):
    """Convierte todo el archivo en texto legible para el prompt."""
    if not os.path.exists(nombre_archivo):
        return "No hay archivo de preguntas cargado."
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        for i, linea in enumerate(archivo.readlines(), 1):
            if ";" in linea:
                partes = linea.strip().split(";", 1)
                if len(partes) == 2:
                    contexto += f"Pregunta {i}: {partes[0].strip()}\n"
                    contexto += f"Respuesta {i}: {partes[1].strip()}\n\n"
    return contexto


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
                "Respondé de forma clara, educativa y breve. "
                "Usá el contexto local del colegio para dar prioridad a respuestas internas. "
                "No menciones si la respuesta proviene del contexto."
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
        "temperature": 0.6,
        "stream": True
    }

    try:
        with requests.post(url, headers=headers, json=data, stream=True, timeout=60) as response:
            response.raise_for_status()
            respuesta = ""
            message_placeholder = st.empty()
            for line in response.iter_lines():
                if line:
                    if line.decode().startswith("data: "):
                        chunk = line.decode().replace("data: ", "").strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            content = requests.utils.json.loads(chunk)
                            delta = content["choices"][0]["delta"].get("content", "")
                            if delta:
                                respuesta += delta
                                message_placeholder.markdown(f"🤖 **MercedarIA:** {respuesta}")
                        except Exception:
                            continue
            return respuesta or "No se recibió respuesta del modelo."
    except Exception as e:
        return f"❌ Error al conectar con DeepSeek: {e}"


def mostrar_fecha_hora():
    ahora = datetime.now()
    return ahora.strftime("📅 %A %d de %B de %Y - 🕒 %H:%M:%S")


def guardar_preguntas_respuestas(nombre_archivo, lista):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for pregunta, respuesta in lista:
            archivo.write(f"{pregunta};{respuesta}\n")


# ==============================
# INTERFAZ STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")
st.title("🎓 MercedarIA - Chatbot del Colegio Mercedaria")

# Inicialización
if "datos" not in st.session_state:
    st.session_state.datos = cargar_preguntas_respuestas(ARCHIVO)
if "historial" not in st.session_state:
    st.session_state.historial = []

# Sidebar
st.sidebar.header("🛠 Menú principal")
modo = st.sidebar.radio("Seleccioná modo:", ["💬 Chat IA", "✏️ Modificar base de datos"])

# ==============================
# MODO CHAT
# ==============================
if modo == "💬 Chat IA":
    st.subheader("💬 Chat con la IA del Colegio")
    contexto = obtener_contexto_archivo(ARCHIVO)
    st.caption("📚 El archivo de conocimiento se incluye automáticamente con cada pregunta.")

    usuario = st.text_input("Escribí tu pregunta:")

    if st.button("Enviar"):
        if usuario.strip():
            st.session_state.historial.append(("👨‍🎓 Vos", usuario))
            respuesta = consultar_deepseek_streaming(usuario, DEEPSEEK_API_KEY, contexto)
            st.session_state.historial.append(("🤖 MercedarIA", respuesta))

    # Mostrar historial completo
    for rol, msg in st.session_state.historial:
        color = "#00FFAA" if rol != "👨‍🎓 Vos" else "#FFFFFF"
        st.markdown(f"<span style='color:{color}'><b>{rol}:</b> {msg}</span>", unsafe_allow_html=True)

    if st.button("🗑 Limpiar conversación"):
        st.session_state.historial = []
        st.success("Conversación reiniciada.")

# ==============================
# MODO EDITOR
# ==============================
else:
    st.subheader("📘 Gestor de Preguntas y Respuestas")
    if not st.session_state.datos:
        st.warning("No hay preguntas cargadas.")
    else:
        for i, (preg, resp) in enumerate(st.session_state.datos, start=1):
            with st.expander(f"🔹 {i}. {preg}"):
                nueva_preg = st.text_input(f"Pregunta {i}", preg, key=f"preg_{i}")
                nueva_resp = st.text_area(f"Respuesta {i}", resp, key=f"resp_{i}")
                st.session_state.datos[i - 1] = (nueva_preg, nueva_resp)

    st.markdown("---")
    st.subheader("➕ Agregar nueva pregunta")
    nueva_pregunta = st.text_input("Nueva pregunta:")
    nueva_respuesta = st.text_area("Nueva respuesta:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Agregar"):
            if nueva_pregunta and nueva_respuesta:
                st.session_state.datos.append((nueva_pregunta, nueva_respuesta))
                guardar_preguntas_respuestas(ARCHIVO, st.session_state.datos)
                st.success("✅ Pregunta agregada correctamente.")
            else:
                st.warning("Completá ambos campos.")

    with col2:
        if st.button("💾 Guardar cambios"):
            guardar_preguntas_respuestas(ARCHIVO, st.session_state.datos)
            st.success("Cambios guardados correctamente.")

    with col3:
        if st.button("🔄 Recargar archivo"):
            st.session_state.datos = cargar_preguntas_respuestas(ARCHIVO)
            st.success("Archivo recargado.")

