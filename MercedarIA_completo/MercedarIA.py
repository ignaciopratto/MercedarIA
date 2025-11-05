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


def guardar_preguntas_respuestas(nombre_archivo, lista):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for pregunta, respuesta in lista:
            archivo.write(f"{pregunta};{respuesta}\n")


def obtener_contexto_archivo(nombre_archivo):
    """Convierte todo el archivo en un bloque de texto (prompt base)."""
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


def consultar_deepseek(mensaje, api_key, contexto=""):
    """Envía la pregunta (con contexto) a la API de DeepSeek."""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Eres un asistente educativo del Colegio Mercedaria. "
                    "Usa la base de conocimiento cargada para responder preguntas. "
                    "Si algo no está en la base, usa conocimiento general. "
                    "Nunca digas 'no lo sé', intenta dar una respuesta útil y educativa."
                ),
            },
            {"role": "user", "content": mensaje if not contexto else f"{contexto}\n\n{mensaje}"},
        ],
        "max_tokens": 600,
        "temperature": 0.6,
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error al conectar con DeepSeek: {e}"


def mostrar_fecha_hora():
    ahora = datetime.now()
    return ahora.strftime("📅 %A %d de %B de %Y - 🕒 %H:%M:%S")

# ==============================
# INTERFAZ STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")
st.title("🎓 MercedarIA - Chatbot del Colegio")

# Inicialización de estado
if "datos" not in st.session_state:
    st.session_state.datos = cargar_preguntas_respuestas(ARCHIVO)
if "historial" not in st.session_state:
    st.session_state.historial = []
if "contexto" not in st.session_state:
    st.session_state.contexto = obtener_contexto_archivo(ARCHIVO)
if "base_cargada" not in st.session_state:
    st.session_state.base_cargada = False

# ==============================
# CARGA INICIAL DE CONTEXTO EN DEEPSEEK
# ==============================
if not st.session_state.base_cargada:
    st.info("📚 Cargando base de conocimiento en DeepSeek...")
    base = st.session_state.contexto + "\n\nConfirma que has cargado correctamente esta base de conocimiento."
    respuesta_inicial = consultar_deepseek(base, DEEPSEEK_API_KEY)
    if "✅" in respuesta_inicial or "cargada" in respuesta_inicial.lower():
        st.success("✅ Base de conocimiento cargada correctamente.")
    else:
        st.warning("⚠️ No se pudo confirmar la carga, pero el contexto fue enviado.")
    st.session_state.base_cargada = True

# ==============================
# SIDEBAR
# ==============================
st.sidebar.header("🛠 Menú principal")
modo = st.sidebar.radio("Seleccioná modo:", ["💬 Chat IA", "✏️ Modificar base de datos"])

# ==============================
# CHATBOT
# ==============================
if modo == "💬 Chat IA":
    st.subheader("💬 Chat con la IA del Colegio Mercedaria")
    usuario = st.text_input("Escribí tu pregunta:")

    if st.button("Enviar"):
        if usuario.strip():
            st.session_state.historial.append(("👨‍🎓 Vos", usuario))
            contexto = st.session_state.contexto
            respuesta = consultar_deepseek(usuario, DEEPSEEK_API_KEY, contexto)
            st.session_state.historial.append(("🤖 MercedarIA", respuesta))

    # Mostrar historial
    for rol, msg in st.session_state.historial:
        color = "#00FFAA" if rol != "👨‍🎓 Vos" else "#FFFFFF"
        st.markdown(f"<span style='color:{color}'><b>{rol}:</b> {msg}</span>", unsafe_allow_html=True)

    if st.button("🗑 Limpiar conversación"):
        st.session_state.historial = []
        st.success("Conversación reiniciada.")

# ==============================
# GESTOR DE PREGUNTAS
# ==============================
else:
    st.subheader("📘 Gestor de Preguntas y Respuestas")
    st.info("Editá directamente las preguntas y respuestas que usa la IA como base de conocimiento.")

    # Mostrar lista editable
    if not st.session_state.datos:
        st.warning("No hay preguntas cargadas. Podés agregar nuevas abajo.")
    else:
        for i, (preg, resp) in enumerate(st.session_state.datos, start=1):
            with st.expander(f"🔹 {i}. {preg}"):
                nueva_preg = st.text_input(f"Editar pregunta {i}", preg, key=f"preg_{i}")
                nueva_resp = st.text_area(f"Editar respuesta {i}", resp, key=f"resp_{i}")
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
                st.success("✅ Pregunta agregada.")
            else:
                st.warning("Completá ambos campos.")

    with col2:
        if st.button("💾 Guardar cambios"):
            guardar_preguntas_respuestas(ARCHIVO, st.session_state.datos)
            st.session_state.contexto = obtener_contexto_archivo(ARCHIVO)
            st.session_state.base_cargada = False
            st.success("Cambios guardados. Se recargará la base de conocimiento al reiniciar.")

    with col3:
        if st.button("🔄 Recargar archivo"):
            st.session_state.datos = cargar_preguntas_respuestas(ARCHIVO)
            st.session_state.contexto = obtener_contexto_archivo(ARCHIVO)
            st.success("Archivo recargado correctamente.")

    st.markdown("---")
    st.caption("🧠 Todos los cambios se guardan en preguntas_respuestas.txt y se cargan al iniciar la IA.")
