import os
import requests
from datetime import datetime
import streamlit as st

# ==============================
# CONFIGURACIÓN
# ==============================
ARCHIVO = "preguntas_respuestas.txt"
DEEPSEEK_API_KEY = "TU_API_KEY_AQUI"  # ⚠️ Reemplaza con tu clave de DeepSeek

# ==============================
# FUNCIONES PRINCIPALES
# ==============================

def cargar_preguntas_respuestas(nombre_archivo):
    preguntas, respuestas = [], []
    if not os.path.exists(nombre_archivo):
        return preguntas, respuestas
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            if ";" in linea:
                partes = linea.strip().split(";", 1)
                if len(partes) == 2:
                    preguntas.append(partes[0].strip().lower().replace(" ", ""))
                    respuestas.append(partes[1].strip())
    return preguntas, respuestas


def guardar_preguntas_respuestas(nombre_archivo, lista):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for pregunta, respuesta in lista:
            archivo.write(f"{pregunta};{respuesta}\n")


def obtener_contexto_archivo(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        return "No hay archivo de preguntas cargado."
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()
        for i, linea in enumerate(lineas, 1):
            if ";" in linea:
                partes = linea.strip().split(";", 1)
                if len(partes) == 2:
                    contexto += f"Pregunta {i}: {partes[0].strip()}\nRespuesta {i}: {partes[1].strip()}\n\n"
    return contexto


def consultar_deepseek(pregunta, api_key, contexto=""):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",
             "content": """Eres un asistente educativo del Colegio Mercedaria. 
             Usa la base local para responder primero; si no hay respuesta, usa tu conocimiento general. 
             Sé amable, educativo y breve."""},
            {"role": "user", "content": f"{contexto}\n\nPregunta: {pregunta}"}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error al conectar con DeepSeek: {e}"


def mostrar_fecha_hora():
    ahora = datetime.now()
    return ahora.strftime("Hoy es %A %d de %B de %Y, %H:%M:%S")


# ==============================
# INTERFAZ STREAMLIT
# ==============================

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")

# Tabs: Chatbot y Editor
tab1, tab2 = st.tabs(["💬 Chatbot", "✏️ Editor de Preguntas"])

# =====================================
# TAB 1 - CHATBOT
# =====================================
with tab1:
    st.title("🤖 Chatbot del Colegio Mercedaria")
    st.markdown("Conocimiento Local + DeepSeek AI")

    preguntas, respuestas = cargar_preguntas_respuestas(ARCHIVO)
    contexto = obtener_contexto_archivo(ARCHIVO)

    if "historial" not in st.session_state:
        st.session_state.historial = []

    usuario = st.text_input("Escribí tu pregunta:")
    if st.button("Enviar"):
        if usuario.strip():
            st.session_state.historial.append(("👨‍🎓 Vos", usuario))
            usuario_normalizado = usuario.lower().replace(" ", "")
            respuesta = None

            # Buscar en base local
            for i, preg in enumerate(preguntas):
                if preg in usuario_normalizado:
                    respuesta = respuestas[i]
                    break

            if respuesta:
                st.session_state.historial.append(("🤖 MercedarIA", respuesta))
            elif DEEPSEEK_API_KEY.strip():
                st.session_state.historial.append(("🤖 MercedarIA", "Pensando..."))
                respuesta = consultar_deepseek(usuario, DEEPSEEK_API_KEY, contexto)
                st.session_state.historial.pop()
                st.session_state.historial.append(("🤖 MercedarIA", respuesta))
            else:
                st.session_state.historial.append(("🤖 MercedarIA", "⚠️ No tengo información para eso."))

    st.divider()
    for rol, msg in st.session_state.historial:
        if rol == "👨‍🎓 Vos":
            st.markdown(f"**{rol}:** {msg}")
        else:
            st.markdown(f"<span style='color:#00FFAA'><b>{rol}:</b></span> {msg}", unsafe_allow_html=True)

    st.divider()
    st.caption(f"🕐 {mostrar_fecha_hora()}")

# =====================================
# TAB 2 - EDITOR
# =====================================
with tab2:
    st.title("✏️ Editor de Preguntas y Respuestas")
    st.caption("Modificá la base local `preguntas_respuestas.txt` que usa el chatbot")

    if "datos" not in st.session_state:
        st.session_state.datos = cargar_preguntas_respuestas(ARCHIVO)

    st.subheader("📋 Preguntas actuales")
    if not st.session_state.datos:
        st.info("No hay preguntas cargadas todavía.")
    else:
        for i, (preg, resp) in enumerate(st.session_state.datos, start=1):
            with st.expander(f"{i}. {preg}"):
                st.markdown(f"**Respuesta:** {resp}")

    st.divider()
    st.subheader("➕ Agregar nueva pregunta")
    col1, col2 = st.columns(2)
    with col1:
        nueva_preg = st.text_input("Nueva pregunta:")
    with col2:
        nueva_resp = st.text_input("Nueva respuesta:")

    if st.button("Guardar nueva pregunta"):
        if nueva_preg and nueva_resp:
            st.session_state.datos.append((nueva_preg.strip(), nueva_resp.strip()))
            guardar_preguntas_respuestas(ARCHIVO, st.session_state.datos)
            st.success("✅ Pregunta agregada correctamente.")
            st.experimental_rerun()
        else:
            st.warning("⚠️ Completá ambos campos antes de guardar.")

    st.divider()
    st.subheader("✏️ Modificar o eliminar")

    if st.session_state.datos:
        indices = [f"{i+1}. {preg}" for i, (preg, _) in enumerate(st.session_state.datos)]
        seleccion = st.selectbox("Seleccioná la pregunta:", indices)

        if seleccion:
            idx = int(seleccion.split(".")[0]) - 1
            preg_actual, resp_actual = st.session_state.datos[idx]

            nueva_pregunta = st.text_input("Modificar pregunta:", preg_actual, key="mod_preg")
            nueva_respuesta = st.text_area("Modificar respuesta:", resp_actual, key="mod_resp")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Guardar cambios"):
                    st.session_state.datos[idx] = (nueva_pregunta, nueva_respuesta)
                    guardar_preguntas_respuestas(ARCHIVO, st.session_state.datos)
                    st.success("✅ Cambios guardados.")
                    st.experimental_rerun()

            with col2:
                if st.button("🗑️ Eliminar"):
                    st.session_state.datos.pop(idx)
                    guardar_preguntas_respuestas(ARCHIVO, st.session_state.datos)
                    st.success("🗑️ Pregunta eliminada correctamente.")
                    st.experimental_rerun()

    st.divider()
    if st.button("🔄 Recargar archivo"):
        st.session_state.datos = cargar_preguntas_respuestas(ARCHIVO)
        st.info("Archivo recargado correctamente.")
        st.experimental_rerun()
