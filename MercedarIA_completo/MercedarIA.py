import streamlit as st
import requests
import threading
import time
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # ⚠️ reemplazá con tu API key real
ADMIN_PASSWORD = "mercedaria2025"      # 🔒 contraseña para editar la base

# ==============================
# BASE DE CONOCIMIENTO LOCAL
# ==============================
BASE_INICIAL = [
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
    ("cuando es el proximo examen", "Consultá el calendario escolar o a tu profesor."),
    ("cuanto dura un modulo de clase", "Cada módulo dura 40 minutos."),
    ("que pasa si llego tarde", "Debés avisar en preceptoría y se registra como tardanza."),
    ("puedo usar el celular", "No, salvo permiso del profesor o autoridad."),
    ("que hago si me enfermo en clase", "Avisá al profesor y luego en preceptoría."),
    ("que hago si pierdo un objeto", "Preguntá en preceptoría o dirección."),
    ("cuando es la entrega de boletines", "Al final de cada cuatrimestre."),
    ("cuando son los recreos", "Turno mañana: 8:35, 10:00, 11:35. Turno tarde: 14:40, 16:05, 17:50."),
    ("donde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456.")
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
            {"role": "system",
             "content": (
                 "Sos MercedarIA, el asistente educativo del Colegio Mercedaria. "
                 "Usá la base de conocimiento local para responder preguntas del colegio. "
                 "Si la información no está disponible, respondé de manera educativa y correcta.
                 puedes responder preguntas de otras cosas que no esten en la base de datos
                 No menciones si la informacion se encuentra o no en tu base de datos"
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
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")

st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption("Basado en conocimiento local + IA DeepSeek")

# Inicializar datos persistentes
if "base_datos" not in st.session_state:
    st.session_state.base_datos = BASE_INICIAL.copy()
if "historial" not in st.session_state:
    st.session_state.historial = []
if "edicion_activa" not in st.session_state:
    st.session_state.edicion_activa = False

contexto = obtener_contexto(st.session_state.base_datos)

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
        for p, r in st.session_state.base_datos:
            if p.lower() in pregunta_normalizada:
                respuesta = r
                break

        # Si no hay coincidencia → consulta a DeepSeek
        if not respuesta:
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)

        st.session_state.historial.append(("🤖 MercedarIA", respuesta))

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
        else:
            st.error("❌ Contraseña incorrecta.")
else:
    st.success("Modo edición activado")
    for i, (p, r) in enumerate(st.session_state.base_datos):
        col1, col2, col3 = st.columns([4, 5, 1])
        with col1:
            nueva_p = st.text_input(f"Pregunta {i+1}", p, key=f"p_{i}")
        with col2:
            nueva_r = st.text_area(f"Respuesta {i+1}", r, key=f"r_{i}")
        with col3:
            if st.button("🗑", key=f"del_{i}"):
                st.session_state.base_datos.pop(i)
                st.rerun()
        st.session_state.base_datos[i] = (nueva_p, nueva_r)

    st.markdown("---")
    nueva_pregunta = st.text_input("➕ Nueva pregunta", key="nueva_p")
    nueva_respuesta = st.text_area("Respuesta", key="nueva_r")
    if st.button("Agregar a la base"):
        if nueva_pregunta and nueva_respuesta:
            st.session_state.base_datos.append((nueva_pregunta.strip(), nueva_respuesta.strip()))
            st.success("✅ Pregunta agregada correctamente.")
        else:
            st.warning("⚠ Escribí una pregunta y su respuesta antes de agregar.")

    if st.button("🚪 Salir del modo edición"):
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
        time.sleep(300)  # cada 5 minutos
        st.session_state["keepalive"] = time.time()

if "keepalive_thread" not in st.session_state:
    hilo = threading.Thread(target=mantener_sesion_viva, daemon=True)
    hilo.start()
    st.session_state["keepalive_thread"] = True

