import streamlit as st
import json
import os
import re

# ==========================================================
#               ESCRIBE TU API KEY DE DEEPSEEK AQUÍ
# ==========================================================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"   # <<<<<< PONELA ACÁ


# ==========================================================
#               BASE DE DATOS LOCAL ORIGINAL
# ==========================================================
base = {
    "general": [
        ("hola", "Hola, ¿cómo estás?"),
        ("quién eres", "Soy MercedarIA, tu asistente del Colegio Mercedaria."),
        ("cómo te llamas", "Me llamo MercedarIA, tu asistente virtual."),
        ("cómo estás", "Estoy funcionando perfectamente, gracias por preguntar."),
        ("adiós", "¡Hasta luego! Que tengas un buen día."),
        ("quién es la directora", "La directora es Marisa Brizzio."),
        ("cuándo son los recreos", "Turno mañana: 8:35, 10:00, 11:35. Turno tarde: 14:40, 16:05, 17:50."),
        ("dónde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456."),
        ("cuándo empieza el ciclo lectivo", "El ciclo lectivo comienza el primer día hábil de marzo."),
        ("cuándo terminan las clases", "Generalmente a mediados de diciembre.")
    ],
    "especificas": {
        "1° A": [
            ("¿Qué materias tengo?", "Biología, Educación en Artes Visuales, Lengua y Literatura, Física, Geografía, Educación Tecnológica, Matemática, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés y Educación Física."),
            ("¿Cuáles son mis contraturnos?", "Educación Física y Educación Tecnológica."),
            ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs.")
        ],
        "1° B": [
            ("¿Qué materias tengo?", "Física, Matemática, Educación en Artes Visuales, Inglés, Educación Religiosa Escolar, Lengua y Literatura, Geografía, Ciudadanía y Participación, Educación Tecnológica, Biología y Educación Física."),
            ("¿Cuáles son mis contraturnos?", "Educación Tecnológica y Educación Física."),
            ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs.")
        ],
        "2° A": [
            ("¿Qué materias tengo?", "Matemática, Lengua y Literatura, Educación Religiosa Escolar, Música, Historia, Educación Tecnológica, Química, Computación, Ciudadanía y Participación, Biología, Inglés y Educación Física."),
            ("¿Cuáles son mis contraturnos?", "Educación Física."),
            ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs.")
        ],
        "2° B": [
            ("¿Qué materias tengo?", "Música, Historia, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés, Matemática, Lengua y Literatura, Educación Tecnológica, Química, Biología y Educación Física."),
            ("¿Cuáles son mis contraturnos?", "Educación Física."),
            ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs.")
        ],
        "3° A": [
            ("¿Qué materias tengo?", "Lengua y Literatura, Inglés, Historia, Geografía, Química, Educación Tecnológica, Física, Educación Religiosa Escolar, Formación para la Vida y el Trabajo, Matemática, Educación Artística Visual, Música, Computación y Educación Física."),
            ("¿Cuáles son mis contraturnos?", "Educación Física y Formación para la Vida y el Trabajo."),
            ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs.")
        ],
        "3° B": [
            ("¿Qué materias tengo?", "Lengua y Literatura, Formación para la Vida y el Trabajo, Física, Historia, Geografía, Educación Artística Visual, Música, Matemática, Educación Tecnológica, Química, Computación, Educación Religiosa Escolar, Educación Física e Inglés."),
            ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
            ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs.")
        ],
        "4° A": [
            ("¿Qué materias tengo?", "Historia, Lengua y Literatura, Biología, ERE, Matemática, Geografía, Educ. Artística, FVT, TIC, Sociedad y Comunicación, Antropología, Educación Física e Inglés."),
            ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
            ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs.")
        ],
        "4° B": [
            ("¿Qué materias tengo?", "Lengua y Literatura, Biología, ERE, Historia, Programación, Geografía, Matemática, Sistemas Digitales, FVT, Educación Artística, Educación Física e Inglés."),
            ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
            ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs.")
        ],
        "5° A": [
            ("¿Qué materias tengo?", "Metodología, Historia, Física, Geografía, Arte Cultural y Social, ERE, Lengua y Literatura, FVT, Matemática, EF, Psicología, Sociología e Inglés."),
            ("¿Cuáles son mis contraturnos?", "EF, Psicología, Sociología e Inglés."),
            ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs.")
        ],
        "5° B": [
            ("¿Qué materias tengo?", "Robótica, Música, Física, Matemática, Historia, Lengua y Literatura, FVT, Sistemas Digitales, Geografía, Psicología, EF, Desarrollo Informático e Inglés."),
            ("¿Cuáles son mis contraturnos?", "EF, Sistemas Digitales, Desarrollo Informático e Inglés."),
            ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs.")
        ],
        "6° A": [
            ("¿Qué materias tengo?", "Ciudadanía y Política, Economía Política, Matemática, Geografía, Filosofía, Química, Lengua y Literatura, Historia, ERE, Sociedad y Comunicación, Teatro, FVT, EF e Inglés."),
            ("¿Cuáles son mis contraturnos?", "EF, Sociedad y Comunicación e Inglés."),
            ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs.")
        ],
        "6° B": [
            ("¿Qué materias tengo?", "Lengua y Literatura, Comunicación Audiovisual, Desarrollo de Soluciones Informáticas, Informática Aplicada, Filosofía, Formación para la Vida y el Trabajo, Química, Matemática, ERE, Ciudadanía y Política, Teatro, EF, Aplicaciones Informáticas e Inglés."),
            ("¿Cuáles son mis contraturnos?", "EF, Aplicaciones Informáticas e Inglés."),
            ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs.")
        ]
    }
}

# ====================================================================
#                          PERSISTENCIA REAL
# ====================================================================
def guardar_base(nueva_base):
    """Reescribe el archivo app.py reemplazando el diccionario 'base' completo."""
    with open("app.py", "r", encoding="utf-8") as f:
        contenido = f.read()

    patron = r"base\s*=\s*\{[\s\S]*?\}\n"
    reemplazo = "base = " + json.dumps(nueva_base, indent=4, ensure_ascii=False) + "\n"

    nuevo_contenido = re.sub(patron, reemplazo, contenido, count=1)

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(nuevo_contenido)


# ====================================================================
#                           CHATBOT
# ====================================================================
def responder_local(pregunta, curso_activo):
    p = pregunta.lower()

    # Primero revisar la base general
    for q, r in base["general"]:
        if q in p:
            return r

    # Luego revisar la base específica del curso elegido
    if curso_activo and curso_activo in base["especificas"]:
        for q, r in base["especificas"][curso_activo]:
            if q.lower() in p:
                return r

    return None


def responder_deepseek(pregunta):
    import requests
    url = "https://api.deepseek.com/chat/completions"

    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": pregunta}]
    }

    r = requests.post(url, json=data, headers=headers)
    return r.json()["choices"][0]["message"]["content"]


# ====================================================================
#                           INTERFAZ STREAMLIT
# ====================================================================
st.title("💬 Chat con MercedarIA")
st.write("¡Bienvenido! Preguntame lo que necesites sobre el colegio.")

# Curso activo
st.sidebar.title("Seleccionar curso")
curso_activo = st.sidebar.selectbox("Elegí tu curso:", ["Ninguno"] + list(base["especificas"].keys()))
if curso_activo == "Ninguno":
    curso_activo = None

if "chat" not in st.session_state:
    st.session_state.chat = []


# ========================
# FORMULARIO DEL CHAT
# ========================
pregunta = st.text_input("Escribe tu pregunta:")

if st.button("Enviar"):
    if pregunta.strip() != "":
        st.session_state.chat.append(("Tú", pregunta))

        resp = responder_local(pregunta, curso_activo)
        if not resp:
            resp = responder_deepseek(pregunta)

        st.session_state.chat.append(("MercedarIA", resp))


# Mostrar chat
for emisor, texto in st.session_state.chat:
    st.markdown(f"**{emisor}:** {texto}")

st.markdown("---")


# ====================================================================
#       ADMINISTRACIÓN: VER Y MODIFICAR BASES (CON CONTRASEÑA)
# ====================================================================
st.subheader("🔐 Administración de base de datos")

password = st.text_input("Contraseña:", type="password")

if password == "mercedaria2025":

    st.success("Acceso concedido ✔")

    # ============================
    # VER Y MODIFICAR BASE GENERAL
    # ============================
    st.markdown("## 📁 Base General")

    nueva_general = []
    for i, (preg, resp) in enumerate(base["general"]):
        st.markdown(f"### Entrada {i+1}")
        nueva_p = st.text_input(f"Pregunta {i+1}", preg, key=f"gp_{i}")
        nueva_r = st.text_area(f"Respuesta {i+1}", resp, key=f"gr_{i}")
        nueva_general.append((nueva_p, nueva_r))

    # ============================
    # VER Y MODIFICAR BASE ESPECÍFICA
    # ============================
    st.markdown("---")
    st.markdown("## 🏫 Base por Curso")

    nueva_especifica = {}

    for curso, pares in base["especificas"].items():
        st.markdown(f"### 📘 {curso}")

        nueva_especifica[curso] = []
        for i, (preg, resp) in enumerate(pares):
            nueva_p = st.text_input(f"{curso} - Pregunta {i+1}", preg, key=f"ep_{curso}_{i}")
            nueva_r = st.text_area(f"{curso} - Respuesta {i+1}", resp, key=f"er_{curso}_{i}")
            nueva_especifica[curso].append((nueva_p, nueva_r))

    # ============================
    # BOTÓN PARA GUARDAR TODO
    # ============================
    if st.button("💾 Guardar cambios"):
        nueva_base = {
            "general": nueva_general,
            "especificas": nueva_especifica
        }
        guardar_base(nueva_base)
        st.success("Base actualizada. Recargá la página.")

    # ============================
    # AGREGAR NUEVA ENTRADA
    # ============================
    st.markdown("---")
    st.subheader("➕ Agregar nueva entrada")

    p_nueva = st.text_input("Nueva pregunta:")
    r_nueva = st.text_area("Nueva respuesta:")

    tipo = st.radio("¿A qué base querés agregar?", ["General", "Específica"])

    if tipo == "Específica":
        curso_sel = st.selectbox("Seleccioná curso:", list(base["especificas"].keys()))
    else:
        curso_sel = None

    if st.button("Agregar"):
        nueva_base = base.copy()

        if tipo == "General":
            nueva_base["general"] = base["general"] + [(p_nueva, r_nueva)]
        else:
            nueva_base["especificas"][curso_sel] = base["especificas"][curso_sel] + [(p_nueva, r_nueva)]

        guardar_base(nueva_base)
        st.success("Entrada agregada. Recargá la página.")

else:
    if password != "":
        st.error("Contraseña incorrecta.")
