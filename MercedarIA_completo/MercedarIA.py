import streamlit as st
import requests
import json
import os

# ===========================================
# CONFIGURACIÓN INICIAL
# ===========================================

st.set_page_config(page_title="Chatbot DeepSeek", layout="wide")

API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # ← PONÉ TU LLAVE AQUÍ
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

# Archivo donde se guardan las preguntas/respuestas
ARCHIVO_DB = "preguntas_respuestas.txt"

# ===========================================
# CARGAR Y GUARDAR LA BASE
# ===========================================

def cargar_base():
    """Carga la base desde el archivo TXT en formato JSON."""
    if not os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
            json.dump({"general": [], "especifica": []}, f, ensure_ascii=False, indent=4)

    try:
        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "general" not in data or "especifica" not in data:
                raise ValueError("El archivo no tiene el formato esperado.")
            return data
    except Exception:
        # Si se rompe el archivo, lo reescribo limpio
        data = {"general": [], "especifica": []}
        with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data


def guardar_base(data):
    """Guarda toda la base sobrescribiendo el archivo."""
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Cargar memoria al iniciar
base = cargar_base()

# ===========================================
# FUNCIÓN PARA CONSULTAR DEEPSEEK
# ===========================================

def consultar_deepseek(mensaje):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content":
             "Eres un asistente útil. NO filtres preguntas. Responde TODO lo mejor posible."},
            {"role": "user", "content": mensaje}
        ]
    }

    try:
        r = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
        r.raise_for_status()
        respuesta = r.json()["choices"][0]["message"]["content"]
        return respuesta
    except Exception as e:
        return f"Error al conectar con DeepSeek: {str(e)}"
# ===========================================
# FUNCIÓN PARA BUSCAR RESPUESTAS EN LAS BASES
# ===========================================

def buscar_respuesta_local(pregunta):
    """
    Busca coincidencias exactas en la base general o específica.
    """
    pregunta_lower = pregunta.strip().lower()

    # Buscar en específica
    for item in base["especifica"]:
        if item["pregunta"].lower() == pregunta_lower:
            return item["respuesta"]

    # Buscar en general
    for item in base["general"]:
        if item["pregunta"].lower() == pregunta_lower:
            return item["respuesta"]

    return None


# ===========================================
# INTERFAZ — SIDEBAR
# ===========================================

with st.sidebar:
    st.title("⚙️ Configuración")

    st.markdown("### Base general")
    st.write("Preguntas y respuestas que aplican a todo.")

    for i, item in enumerate(base["general"]):
        st.write(f"**{i+1}.** {item['pregunta']}")
        if st.button(f"❌ Borrar {i+1}", key=f"gen_del_{i}"):
            base["general"].pop(i)
            guardar_base(base)
            st.rerun()

    st.markdown("---")
    st.markdown("### Base específica")
    st.write("Información concreta agregada por vos.")

    for i, item in enumerate(base["especifica"]):
        st.write(f"**{i+1}.** {item['pregunta']}")
        if st.button(f"❌ Borrar {i+1}", key=f"esp_del_{i}"):
            base["especifica"].pop(i)
            guardar_base(base)
            st.rerun()

    st.markdown("---")
    st.markdown("### ➕ Agregar nueva entrada")

    nueva_preg = st.text_input("Pregunta:")
    nueva_resp = st.text_area("Respuesta:")

    tipo = st.radio("Guardar en:", ["General", "Específica"])

    if st.button("Guardar entrada"):
        if nueva_preg.strip() and nueva_resp.strip():
            if tipo == "General":
                base["general"].append({"pregunta": nueva_preg, "respuesta": nueva_resp})
            else:
                base["especifica"].append({"pregunta": nueva_preg, "respuesta": nueva_resp})

            guardar_base(base)
            st.success("Guardado correctamente.")
            st.rerun()
        else:
            st.error("Debes completar ambos campos.")
# ===========================================
# SECCIÓN DE CHAT
# ===========================================

st.title("🤖 Asistente con DeepSeek + Base local")

st.write("Escribe tu pregunta y el sistema responderá usando primero la base local y, si no encuentra coincidencias, DeepSeek.")


if "mensajes" not in st.session_state:
    st.session_state["mensajes"] = []


# Mostrar historial
for rol, texto in st.session_state["mensajes"]:
    if rol == "user":
        st.chat_message("user").markdown(texto)
    else:
        st.chat_message("assistant").markdown(texto)


# Input del usuario
prompt = st.chat_input("Escribe aquí...")

if prompt:
    st.session_state["mensajes"].append(("user", prompt))
    st.chat_message("user").markdown(prompt)

    # 1. Buscar en base local
    respuesta_local = buscar_respuesta_local(prompt)

    if respuesta_local:
        respuesta = respuesta_local

    else:
        # 2. Si no está, usar DeepSeek
        st.toast("Usando DeepSeek...")

        try:
            DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"

            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Eres un asistente útil que responde de forma clara y precisa."},
                    {"role": "user", "content": prompt}
                ]
            }

            resp = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=data,
                timeout=20
            )

            respuesta = resp.json()["choices"][0]["message"]["content"]

        except Exception as e:
            respuesta = "⚠️ Error al consultar DeepSeek."

    # Mostrar respuesta
    st.session_state["mensajes"].append(("assistant", respuesta))
    st.chat_message("assistant").markdown(respuesta)
# ===========================================
# PERSISTENCIA — REESCRIBIR EL ARCHIVO app.py
# ===========================================

def guardar_base(nueva_base):
    """
    Reescribe el archivo app.py conservando todo el código
    pero actualizando las bases GENERAL y ESPECIFICA.
    """
    with open("app.py", "r", encoding="utf-8") as f:
        contenido = f.read()

    # Encontrar las listas originales
    inicio = contenido.index("base = {")
    fin = contenido.index("}", inicio) + 1

    # Crear texto reemplazado
    reemplazo = f'base = {json.dumps(nueva_base, indent=4, ensure_ascii=False)}'

    nuevo_contenido = contenido[:inicio] + reemplazo + contenido[fin:]

    # Reescribir archivo
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(nuevo_contenido)
