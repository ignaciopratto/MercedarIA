import requests
import streamlit as st
from datetime import datetime

# ==========================
# CONFIGURACIÓN
# ==========================
DEEPSEEK_API_KEY = ""  # opcional, dejar vacío si no usas IA

COLORES = {
    "primario": "#FF6B6B",
    "secundario": "#4ECDC4",
    "texto": "#2C3E50",
    "fondo": "#F8F9FA"
}

# ==========================
# BASE DE CONOCIMIENTO
# ==========================
BASE_CONOCIMIENTO = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quien eres", "Soy un asistente IA diseñado para responder preguntas de la escuela."),
    ("como te llamas", "Me llamo MercedarIA, soy tu asistente virtual, estoy aquí para ayudarte en lo que necesites."),
    ("como estas", "Estoy funcionando perfectamente, gracias por preguntar."),
    ("adios", "¡Hasta luego! Que tengas un buen día."),
    ("cuando empiezan las clases", "Las clases comienzan el primer día hábil de marzo."),
    ("cuando terminan las clases", "Las clases terminan a mediados de diciembre."),
    ("cuando son las vacaciones de invierno", "Empiezan a mediados de julio y duran dos semanas."),
    ("cuando son las vacaciones de verano", "Empiezan en diciembre y terminan en marzo."),
    ("quien es el director", "El director es el responsable de la institución educativa, su nombre es Marisa."),
    ("donde esta la biblioteca", "La biblioteca está en el primer piso del colegio, al lado de la preceptoría."),
    ("cuando es el proximo examen", "Consulta el calendario escolar o pregúntale a tu profesor."),
    ("cual es el proximo acto escolar", "Por favor especificar."),
    ("cuanto dura un modulo de clase", "Cada módulo dura 40 minutos."),
    ("que pasa si llego tarde", "Debes avisar en la preceptoría y puede quedar registrado como tardanza."),
    ("puedo usar el celular", "No, el uso del celular está estrictamente prohibido, a menos que sea con permiso del profesor u otra persona de autoridad."),
    ("que hago si me enfermo en clase", "Debes avisar al profesor y luego dirigirte a la preceptoría para avisar a tus padres/tutor."),
    ("que hago si pierdo un objeto", "Debes preguntar en preceptoría o en dirección, allí guardan los objetos perdidos."),
    ("cuando es la entrega de boletines", "Generalmente al final de cada cuatrimestre."),
    ("cuando son los recreos", "En el turno mañana los recreos son a las 8:35, 10:00 y 11:35, mientras que en el turno tarde son más tarde."),
    ("como se llama la directora", "Marisa Brizzio."),
    ("donde queda la escuela", "La escuela queda en la ciudad de Arroyito, Córdoba, en la calle 9 de julio 456.")
]

# ==========================
# FUNCIONES AUXILIARES
# ==========================
def aplicar_estilos():
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }}
    .chat-message {{
        padding: 1rem; border-radius: 15px; margin: 0.8rem 0;
    }}
    .user-message {{
        background: {COLORES['secundario']}; color: white; margin-left: 20%;
    }}
    .bot-message {{
        background: {COLORES['primario']}; color: white; margin-right: 20%;
    }}
    </style>
    """, unsafe_allow_html=True)


def buscar_respuesta_local(consulta: str):
    consulta = consulta.lower().strip()
    for pregunta, respuesta in BASE_CONOCIMIENTO:
        if any(palabra in consulta for palabra in pregunta.split()):
            return respuesta
    return None


def generar_contexto():
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n"
    for pregunta, respuesta in BASE_CONOCIMIENTO:
        contexto += f"P: {pregunta}\nR: {respuesta}\n\n"
    return contexto


def consultar_ia(pregunta, api_key, contexto=""):
    if not api_key:
        return "⚠️ No hay clave API configurada para usar IA."

    try:
        res = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Sos un asistente educativo del Colegio Mercedaria."},
                    {"role": "user", "content": f"{contexto}\nUsuario: {pregunta}"}
                ]
            },
            timeout=30
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error al consultar IA: {e}"


def obtener_fecha_hora():
    ahora = datetime.now()
    return f"📅 {ahora.strftime('%d/%m/%Y')} • 🕐 {ahora.strftime('%H:%M')}"

# ==========================
# INTERFAZ PRINCIPAL
# ==========================
def main():
    st.set_page_config(page_title="MercedarIA", page_icon="🎓")
    aplicar_estilos()

    st.markdown("<h1 style='text-align:center;'>🎓 MercedarIA</h1>", unsafe_allow_html=True)

    # Inicializar historial solo una vez
    if "historial" not in st.session_state:
        st.session_state.historial = [
            ("bot", "¡Hola! Soy MercedarIA, tu asistente educativo del Colegio Mercedaria. ¿En qué puedo ayudarte hoy?")
        ]

    consulta = st.text_input("✏️ Escribí tu pregunta:", key="input_chat")
    if st.button("📤 Enviar") and consulta.strip():
        st.session_state.historial.append(("usuario", consulta))
        respuesta_local = buscar_respuesta_local(consulta)

        if respuesta_local:
            respuesta = f"{respuesta_local}\n\n📚 *Respuesta de base local*"
        else:
            contexto = generar_contexto()
            respuesta = f"{consultar_ia(consulta, DEEPSEEK_API_KEY, contexto)}\n\n🤖 *Respuesta IA*"

        st.session_state.historial.append(("bot", respuesta))
        st.rerun()

    # Mostrar historial
    for rol, msg in st.session_state.historial:
        clase = "user-message" if rol == "usuario" else "bot-message"
        st.markdown(f"<div class='chat-message {clase}'>{msg}</div>", unsafe_allow_html=True)

    st.markdown(f"<div style='text-align:center;color:gray;margin-top:1rem;'>{obtener_fecha_hora()}</div>", unsafe_allow_html=True)

    if st.button("🗑️ Limpiar chat"):
        st.session_state.historial = [
            ("bot", "¡Hola! Soy MercedarIA, tu asistente educativo del Colegio Mercedaria. ¿En qué puedo ayudarte hoy?")
        ]
        st.rerun()

# ==========================
# EJECUCIÓN
# ==========================
if __name__ == "__main__":
    main()
