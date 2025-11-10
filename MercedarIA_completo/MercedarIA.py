import streamlit as st
import requests
import json
import os

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # ⚠ reemplazá con tu API key real
ARCHIVO_BD = "base_datos.json"
CONTRASEÑA_EDICION = "mercedaria2025"  # 🔐 cambiá esta contraseña

# ==============================
# FUNCIONES DE BASE DE DATOS
# ==============================
def cargar_base():
    if os.path.exists(ARCHIVO_BD):
        with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return [
            ("hola", "Hola, ¿cómo estás?"),
            ("quien eres", "Soy un asistente IA diseñado para responder preguntas de la escuela."),
            ("como te llamas", "Me llamo MercedarIA, soy tu asistente virtual."),
            ("como estas", "Estoy funcionando perfectamente, gracias por preguntar."),
            ("adios", "¡Hasta luego! Que tengas un buen día."),
            ("cuando empiezan las clases", "Las clases comienzan el primer día hábil de marzo."),
            ("cuando terminan las clases", "Las clases terminan a mediados de diciembre."),
            ("cuando son las vacaciones de invierno", "Empiezan a mediados de julio y duran dos semanas."),
            ("cuando son las vacaciones de verano", "Empiezan en diciembre y terminan en marzo."),
            ("quien es el director", "El director es el responsable de la institución. Su nombre es Marisa."),
            ("donde esta la biblioteca", "En el primer piso, al lado de la preceptoría."),
            ("cuanto dura un modulo de clase", "Cada módulo dura 40 minutos."),
            ("que pasa si llego tarde", "Debés avisar en la preceptoría y puede quedar registrado como tardanza."),
            ("puedo usar el celular", "No, salvo con permiso del profesor o autoridad."),
            ("que hago si me enfermo en clase", "Debés avisar al profesor y luego a preceptoría."),
            ("cuando es la entrega de boletines", "Generalmente al final de cada cuatrimestre."),
            ("cuando son los recreos", "Mañana: 8:35, 10:00 y 11:35. Tarde: 14:40, 16:05 y 17:50."),
            ("como se llama la directora", "Marisa Brizzio."),
            ("donde queda la escuela", "Ciudad de Arroyito, Córdoba, en la calle 9 de Julio 456.")
        ]

def guardar_base(lista):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

def obtener_contexto(lista):
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(lista, 1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto

# ==============================
# FUNCIÓN IA (sin streaming)
# ==============================
def consultar_deepseek(pregunta, api_key, contexto):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sos MercedarIA, el asistente educativo del Colegio Mercedaria. "
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

# ==============================
# INTERFAZ STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="centered")

st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption("Conocimiento local + DeepSeek AI (sin streaming)")

if "base_datos" not in st.session_state:
    st.session_state.base_datos = cargar_base()
if "historial" not in st.session_state:
    st.session_state.historial = []
if "acceso_edicion" not in st.session_state:
    st.session_state.acceso_edicion = False

contexto = obtener_contexto(st.session_state.base_datos)

# ==============================
# CHAT
# ==============================
st.subheader("💬 Chat con tu mama")
pregunta = st.text_input("Escribí tu pregunta:")

if st.button("Enviar"):
    if pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        pregunta_normalizada = pregunta.lower().strip()

        # Buscar coincidencia local
        respuesta = None
        for p, r in st.session_state.base_datos:
            if p.lower() in pregunta_normalizada:
                respuesta = r
                break

        if not respuesta:
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)

        st.session_state.historial.append(("🤖 MercedarIA", respuesta))

for rol, msg in st.session_state.historial:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"🧍 *{rol}:* {msg}")
    else:
        st.markdown(f"🧠 <span style='color:#00FFAA'><b>{rol}:</b></span> {msg}", unsafe_allow_html=True)

st.divider()

# ==============================
# EDICIÓN CON CONTRASEÑA
# ==============================
st.subheader("🧩 Editar base de conocimiento")

if not st.session_state.acceso_edicion:
    password = st.text_input("🔑 Ingresá la contraseña para editar:", type="password")
    if st.button("Ingresar"):
        if password == CONTRASEÑA_EDICION:
            st.session_state.acceso_edicion = True
            st.success("✅ Acceso concedido. Podés editar la base.")
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta.")
else:
    st.success("🔓 Acceso de edición habilitado.")
    for i, (p, r) in enumerate(st.session_state.base_datos):
        col1, col2, col3 = st.columns([4, 5, 1])
        with col1:
            st.session_state.base_datos[i] = (
                st.text_input(f"Pregunta {i+1}", p, key=f"p_{i}"),
                st.text_area(f"Respuesta {i+1}", r, key=f"r_{i}")
            )
        with col3:
            if st.button("🗑", key=f"del_{i}"):
                st.session_state.base_datos.pop(i)
                guardar_base(st.session_state.base_datos)
                st.rerun()

    st.markdown("---")
    nueva_pregunta = st.text_input("➕ Nueva pregunta")
    nueva_respuesta = st.text_area("Respuesta")
    if st.button("Agregar a la base"):
        if nueva_pregunta and nueva_respuesta:
            st.session_state.base_datos.append((nueva_pregunta.strip(), nueva_respuesta.strip()))
            guardar_base(st.session_state.base_datos)
            st.success("✅ Pregunta agregada correctamente.")
            st.rerun()
        else:
            st.warning("⚠ Escribí una pregunta y su respuesta antes de agregar.")

    if st.button("💾 Guardar cambios"):
        guardar_base(st.session_state.base_datos)
        st.success("✅ Base guardada permanentemente en disco.")

st.divider()

if st.button("🧹 Limpiar chat"):
    st.session_state.historial = []
    st.rerun()

st.caption("💾 Los cambios se guardan automáticamente en base_datos.json")

