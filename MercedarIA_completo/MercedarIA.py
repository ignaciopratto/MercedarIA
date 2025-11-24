import streamlit as st
import requests
import base64
import re
from datetime import datetime

# ============================================
# CONFIGURACIÓN SECRETS
# ============================================

DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USER = st.secrets["GITHUB_USER"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_BASE_FOLDER = st.secrets.get("GITHUB_BASE_FOLDER", "MercedarIA_completo")

ADMIN_MASTER_KEY = st.secrets.get("ADMIN_MASTER_KEY", "claveadmin")

BASES_ROOT = f"{GITHUB_BASE_FOLDER}/bases"


# ============================================
# BASE GENERAL DEFAULT
# ============================================

BASE_GENERAL_DEFAULT = [
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
]

# Guardar en la sesión si no existe
if "base_general" not in st.session_state:
    st.session_state.base_general = BASE_GENERAL_DEFAULT.copy()


# ============================================
# BASES ESPECÍFICAS POR CURSO DEFAULT
# ============================================

BASES_ESPECIFICAS_DEFAULT = {
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

if "bases_especificas" not in st.session_state:
    st.session_state.bases_especificas = {
        k: v.copy() for k, v in BASES_ESPECIFICAS_DEFAULT.items()
    }


# ============================================
# FUNCIONES GITHUB
# ============================================

def github_raw_url(path):
    return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{path}"

def github_api_url(path):
    return f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path}"

def leer_archivo_github(path):
    try:
        r = requests.get(github_raw_url(path))
        if r.status_code == 200:
            return r.text
        return ""
    except:
        return ""

def escribir_archivo_github(path, contenido):
    url = github_api_url(path)
    try:
        r_get = requests.get(url, headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        })
        sha = r_get.json().get("sha") if r_get.status_code == 200 else None
    except:
        sha = None

    data = {
        "message": f"Actualizando {path}",
        "content": base64.b64encode(contenido.encode("utf-8")).decode("utf-8")
    }

    if sha:
        data["sha"] = sha

    r_put = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    })

    return r_put.status_code in (200, 201)


# ============================================
# (SIGUE EN PARTE 2)
# ============================================

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")
# ============================================
# USERS
# ============================================

def cargar_usuarios():
    texto = leer_archivo_github(f"{BASES_ROOT}/users.txt")
    usuarios = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        email, nombre, apellido, rol, curso, pw = linea.split(";", 5)
        usuarios.append({
            "email": email.strip(),
            "nombre": nombre.strip(),
            "apellido": apellido.strip(),
            "rol": rol.strip(),
            "curso": curso.strip(),
            "password": pw.strip()
        })
    return usuarios


def guardar_usuarios(lista):
    contenido = "\n".join(
        f"{u['email']};{u['nombre']};{u['apellido']};{u['rol']};{u['curso']};{u['password']}"
        for u in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/users.txt", contenido)


# ============================================
# COURSES
# ============================================

def cargar_cursos():
    texto = leer_archivo_github(f"{BASES_ROOT}/courses.txt")
    cursos = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        id_, curso, materia, email_prof = linea.split(";", 3)
        cursos.append({
            "id": id_.strip(),
            "curso": curso.strip(),
            "materia": materia.strip(),
            "email": email_prof.strip()
        })
    return cursos


def guardar_cursos(lista):
    contenido = "\n".join(
        f"{c['id']};{c['curso']};{c['materia']};{c['email']}" for c in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/courses.txt", contenido)


# ============================================
# TASKS
# ============================================

def cargar_tareas():
    texto = leer_archivo_github(f"{BASES_ROOT}/tasks.txt")
    tareas = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        id_, curso, materia, titulo, descr, creador, fecha = linea.split(";", 6)
        tareas.append({
            "id": id_.strip(),
            "curso": curso.strip(),
            "materia": materia.strip(),
            "titulo": titulo.strip(),
            "descripcion": descr.strip(),
            "creador": creador.strip(),
            "fecha_limite": fecha.strip()
        })
    return tareas


def guardar_tareas(lista):
    contenido = "\n".join(
        f"{t['id']};{t['curso']};{t['materia']};{t['titulo']};"
        f"{t['descripcion']};{t['creador']};{t['fecha_limite']}"
        for t in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/tasks.txt", contenido)


# ============================================
# ARCHIVOS FAQ DE PROFESORES
# ============================================

def archivo_base_curso_materia(curso, materia):
    cid = curso.replace("°", "").replace(" ", "")
    mid = re.sub(r"[^a-z0-9]", "", materia.lower())
    return f"{BASES_ROOT}/{cid}_{mid}.txt"


def guardar_faqs_en_archivo(path, faqs):
    contenido = "\n".join(f"{f['pregunta']};{f['respuesta']}" for f in faqs)
    escribir_archivo_github(path, contenido)


# ============================================
# CARGAS INICIALES
# ============================================

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()


# ============================================
# MANEJO DE SESIÓN
# ============================================

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "modo_anonimo" not in st.session_state:
    st.session_state.modo_anonimo = False

st.title("🎓 MercedarIA — Asistente del Colegio")


# ============================================
# LOGIN / REGISTRO / MODO INVITADO
# ============================================

if st.session_state.usuario is None and not st.session_state.modo_anonimo:
    st.subheader("🔐 Iniciar sesión")

    col_login, col_reg, col_anon = st.columns([2, 2, 1])

    # ------------------------------
    # LOGIN
    # ------------------------------
    with col_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_password")

        if st.button("Ingresar"):
            usuarios = cargar_usuarios()
            user = next(
                (u for u in usuarios
                 if u["email"].lower() == email.lower()
                 and u["password"] == password),
                None
            )

            if user:
                st.session_state.usuario = user
                st.success(f"Bienvenido/a {user['nombre']} {user['apellido']}.")
                st.rerun()
            else:
                st.error("Email o contraseña incorrectos.")
                st.stop()

    # ------------------------------
    # REGISTRO
    # ------------------------------
    with col_reg:
        st.markdown("### 🧾 Crear cuenta")

        new_email = st.text_input("Email nuevo", key="reg_email")
        new_nombre = st.text_input("Nombre", key="reg_nombre")
        new_apellido = st.text_input("Apellido", key="reg_apellido")

        tipo_cuenta = st.selectbox("Tipo de cuenta", ["alumno", "profe"])
        
        # Selección de curso (solo alumno)
        if tipo_cuenta == "alumno":
            new_curso = st.selectbox(
                "Curso",
                sorted({c["curso"] for c in cursos}),
                key="reg_curso"
            )
        else:
            new_curso = "-"

        new_pw = st.text_input("Contraseña nueva", type="password", key="reg_pw")

        # Profesor → requiere clave admin
        if tipo_cuenta == "profe":
            admin_pw = st.text_input(
                "Contraseña de administrador para crear profesor",
                type="password"
            )
        else:
            admin_pw = ""

        if st.button("Crear cuenta"):
            usuarios = cargar_usuarios()

            if any(u["email"].lower() == new_email.lower() for u in usuarios):
                st.error("Ya existe un usuario con ese email.")
            elif tipo_cuenta == "profe" and admin_pw != ADMIN_MASTER_KEY:
                st.error("Contraseña de administrador incorrecta.")
            elif not new_email or not new_nombre or not new_apellido or not new_pw:
                st.error("Completá todos los campos.")
            else:
                usuarios.append({
                    "email": new_email.strip(),
                    "nombre": new_nombre.strip(),
                    "apellido": new_apellido.strip(),
                    "rol": tipo_cuenta,
                    "curso": new_curso.strip(),
                    "password": new_pw.strip(),
                })
                guardar_usuarios(usuarios)
                st.success("Cuenta creada. Podés iniciar sesión.")
                st.rerun()

    # ------------------------------
    # MODO INVITADO
    # ------------------------------
    with col_anon:
        if st.button("Entrar como invitado"):
            st.session_state.modo_anonimo = True
            st.session_state.usuario = None
            st.rerun()


# ============================================
# CREAR USUARIO INVITADO
# ============================================

if st.session_state.modo_anonimo:
    usuario = {
        "nombre": "Invitado",
        "apellido": "",
        "rol": "anonimo",
        "email": "anonimo@insm.edu",
        "curso": "General"
    }
else:
    usuario = st.session_state.usuario

if usuario is None:
    st.warning("Iniciá sesión o entrá como invitado.")
    st.stop()


# ============================================
# INFO DEL USUARIO + LOGOUT
# ============================================

rol = usuario["rol"]
email_usuario = usuario["email"]
curso_usuario = usuario["curso"]

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

col_i, col_o = st.columns([4, 1])

with col_i:
    st.info(
        f"Conectado como **{usuario['nombre']} {usuario['apellido']}** — "
        f"Rol: **{rol}** — Curso: **{curso_usuario}**"
    )

with col_o:
    if st.button("Cerrar sesión"):
        # 🔥 BORRAR CHAT Y ESTADO
        st.session_state.chat_history = []
        st.session_state.usuario = None
        st.session_state.modo_anonimo = False
        st.rerun()


# ============================================
# CHATBOT — FUNCIÓN DEEPSEEK
# ============================================

def consultar_deepseek(pregunta, contexto):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": contexto},
            {"role": "user", "content": pregunta},
        ],
        "max_tokens": 600,
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=18)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error consultando DeepSeek: {e}"


# ============================================
# CONSTRUCCIÓN DEL CONTEXTO DEL CHATBOT
# ============================================

def construir_contexto(usuario_actual):

    if usuario_actual["rol"] == "anonimo":
        return (
            "Modo anónimo: responder SOLO usando la base general.\n\n"
            + "\n".join(f"{p}: {r}" for p, r in st.session_state.base_general)
        )

    contexto = "INFORMACIÓN PARA EL CHATBOT:\n\n"

    # Base general
    contexto += "BASE GENERAL:\n"
    for p, r in st.session_state.base_general:
        contexto += f"{p} -> {r}\n"

    # Base específica curso
    if usuario_actual["curso"] in st.session_state.bases_especificas:
        contexto += f"\nBASE DEL CURSO {usuario_actual['curso']}:\n"
        for p, r in st.session_state.bases_especificas[usuario_actual["curso"]]:
            contexto += f"{p} -> {r}\n"

    # Materias y profes
    contexto += "\nMATERIAS DEL CURSO:\n"
    for c in cursos:
        if c["curso"] == usuario_actual["curso"]:
            contexto += f"{c['materia']} dictada por {c['email']}\n"

    # Tareas del curso
    contexto += "\nTAREAS DEL CURSO:\n"
    for t in tareas:
        if t["curso"] == usuario_actual["curso"]:
            contexto += f"{t['materia']} — {t['titulo']} — vence {t['fecha_limite']}\n"

    # FAQ de cada materia del curso
    for c in cursos:
        if c["curso"] == usuario_actual["curso"]:
            path = archivo_base_curso_materia(c["curso"], c["materia"])
            contenido = leer_archivo_github(path)
            if contenido.strip():
                contexto += f"\nFAQ de {c['materia']}:\n{contenido}\n"

    return contexto


# ============================================
# CHATBOX CON BURBUJAS (OPCIÓN B)
# ============================================

st.subheader("💬 Chat con MercedarIA")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

col_in, col_btn = st.columns([4, 1])

with col_in:
    pregunta = st.text_input("Escribí tu pregunta:")

with col_btn:
    if st.button("Enviar"):
        if pregunta.strip():
            contexto = construir_contexto(usuario)
            respuesta = consultar_deepseek(pregunta, contexto)

            st.session_state.chat_history.append({"role": "user", "content": pregunta})
            st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
            st.rerun()


# Renderizar estilo burbujas
for m in st.session_state.chat_history:
    if m["role"] == "user":
        st.markdown(
            f"""
<div style="
text-align:right;">
    <div style="
        display:inline-block;
        background:#71b548;
        color:white;
        padding:12px 16px;
        border-radius:16px;
        margin:6px;
        max-width:70%;
        box-shadow:0 0 6px rgba(0,0,0,0.2);
    ">
        {m['content']}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
<div style="text-align:left;">
    <div style="
        display:inline-block;
        background:#23263d;
        color:white;
        padding:12px 16px;
        border-radius:16px;
        margin:6px;
        max-width:70%;
        box-shadow:0 0 6px rgba(0,0,0,0.2);
    ">
        {m['content']}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown("---")
# ============================================
# 📝 TAREAS — ALUMNO / PROFESOR / ADMIN
# ============================================

st.header("📝 Tareas")

# ============================
# ALUMNO
# ============================

if rol == "alumno":
    st.subheader("Tareas de tu curso")

    tareas_curso = [t for t in tareas if t["curso"] == curso_usuario]

    if not tareas_curso:
        st.info("No hay tareas asignadas a tu curso.")
    else:
        for t in tareas_curso:
            st.markdown(f"""
**📌 {t['titulo']}**   
📚 *Materia:* {t['materia']}  
📝 *Descripción:* {t['descripcion']}  
⏳ *Fecha límite:* {t['fecha_limite']}  
👨‍🏫 *Profesor:* {t['creador']}  
---""")

# ============================
# PROFESOR
# ============================

elif rol == "profe":

    st.subheader("Crear nueva tarea")

    materias_mias = [c for c in cursos if c["email"] == email_usuario]

    if not materias_mias:
        st.info("No tenés materias asignadas.")
    else:
        seleccion = st.selectbox(
            "Elegí curso y materia:",
            [f"{c['curso']} — {c['materia']}" for c in materias_mias]
        )

        curso_sel, materia_sel = seleccion.split(" — ", 1)

        titulo = st.text_input("Título de la tarea")
        descr = st.text_area("Descripción")
        fecha = st.date_input("Fecha límite")

        if st.button("Agregar tarea"):
            nuevo_id = str(max([int(t["id"]) for t in tareas] + [0]) + 1)

            nueva = {
                "id": nuevo_id,
                "curso": curso_sel,
                "materia": materia_sel,
                "titulo": titulo.strip(),
                "descripcion": descr.strip(),
                "creador": email_usuario,
                "fecha_limite": str(fecha),
            }

            tareas.append(nueva)
            guardar_tareas(tareas)
            st.success("Tarea agregada correctamente.")
            st.rerun()

        st.markdown("---")
        st.subheader("Editar / borrar mis tareas")

        mis_tareas = [t for t in tareas if t["creador"] == email_usuario]

        if not mis_tareas:
            st.info("Todavía no creaste ninguna tarea.")
        else:
            for t in mis_tareas:
                with st.expander(f"{t['curso']} — {t['materia']} — {t['titulo']}"):
                    nt = st.text_input("Título", value=t["titulo"], key=f"t_{t['id']}")
                    nd = st.text_area("Descripción", value=t["descripcion"], key=f"d_{t['id']}")
                    nf = st.text_input("Fecha límite (YYYY-MM-DD)", value=t["fecha_limite"], key=f"f_{t['id']}")

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(f"Guardar cambios {t['id']}"):
                            t["titulo"] = nt
                            t["descripcion"] = nd
                            t["fecha_limite"] = nf
                            guardar_tareas(tareas)
                            st.success("Cambios guardados.")
                            st.rerun()

                    with col2:
                        if st.button(f"Eliminar {t['id']}"):
                            tareas = [x for x in tareas if x["id"] != t["id"]]
                            guardar_tareas(tareas)
                            st.success("Tarea eliminada.")
                            st.rerun()


# ============================
# ADMIN
# ============================

elif rol == "admin":
    st.subheader("Todas las tareas del sistema")

    if not tareas:
        st.info("No hay tareas cargadas actualmente.")
    else:
        for t in tareas:
            st.markdown(f"""
**[{t['id']}] {t['titulo']}**  
🏫 Curso: {t['curso']}  
📚 Materia: {t['materia']}  
📌 {t['descripcion']}  
⏳ Vence: {t['fecha_limite']}  
👨‍🏫 Creador: {t['creador']}  
---
""")


# ============================================
# 📚 PANEL DEL PROFESOR — FAQ POR MATERIA
# ============================================

if rol == "profe":

    st.header("📚 Panel del Profesor — Preguntas y Respuestas por materia")

    materias_mias = [c for c in cursos if c["email"] == email_usuario]

    if materias_mias:
        elegido = st.selectbox(
            "Elegí materia para editar:",
            [f"{c['curso']} — {c['materia']}" for c in materias_mias]
        )

        curso_edit, materia_edit = elegido.split(" — ", 1)

        path = archivo_base_curso_materia(curso_edit, materia_edit)
        contenido = leer_archivo_github(path)

        # Convertir en lista de dicts
        faqs = []
        for linea in contenido.splitlines():
            if ";" in linea:
                p, r = linea.split(";", 1)
                faqs.append({"pregunta": p.strip(), "respuesta": r.strip()})

        # --------------------
        # Agregar FAQ
        # --------------------
        st.markdown("### ➕ Agregar Pregunta/Respuesta")

        with st.form(f"add_faq_{materia_edit}"):
            preg = st.text_input("Pregunta")
            resp = st.text_area("Respuesta")
            submit = st.form_submit_button("Agregar")

            if submit:
                if preg.strip() and resp.strip():
                    faqs.append({"pregunta": preg.strip(), "respuesta": resp.strip()})
                    guardar_faqs_en_archivo(path, faqs)
                    st.success("Pregunta añadida.")
                    st.rerun()

        st.markdown("---")

        # --------------------
        # Editar o borrar FAQ
        # --------------------
        st.markdown("### ✏️ Editar o borrar preguntas existentes")

        for i, f in enumerate(faqs):
            with st.expander(f"{i+1}. {f['pregunta']}"):
                np = st.text_input("Pregunta", value=f["pregunta"], key=f"ep_{i}")
                nr = st.text_area("Respuesta", value=f["respuesta"], key=f"er_{i}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Guardar cambios {i}"):
                        faqs[i]["pregunta"] = np
                        faqs[i]["respuesta"] = nr
                        guardar_faqs_en_archivo(path, faqs)
                        st.success("Actualizado.")
                        st.rerun()

                with col2:
                    if st.button(f"Eliminar {i}"):
                        faqs = [x for j, x in enumerate(faqs) if j != i]
                        guardar_faqs_en_archivo(path, faqs)
                        st.success("Eliminado.")
                        st.rerun()


# ============================================
# ⚙️ PANEL DEL ADMINISTRADOR COMPLETO
# ============================================

if rol == "admin":

    st.header("⚙️ Panel de Administración")

    tab_usuarios, tab_cursos, tab_bases = st.tabs(
        ["👥 Usuarios", "📘 Cursos y materias", "📚 Bases de conocimiento"]
    )

    # ============================================
    # 👥 TAB 1 — GESTIÓN DE USUARIOS
    # ============================================

    with tab_usuarios:
        st.subheader("Lista de usuarios:")

        for u in usuarios:
            st.markdown(f"- **{u['email']}** — {u['rol']} — curso: {u['curso']}")

        st.markdown("---")
        st.subheader("Modificar / eliminar usuario")

        if usuarios:
            email_sel = st.selectbox(
                "Seleccionar usuario:",
                [u["email"] for u in usuarios]
            )

            user_sel = next(u for u in usuarios if u["email"] == email_sel)

            nn = st.text_input("Nombre", user_sel["nombre"])
            na = st.text_input("Apellido", user_sel["apellido"])
            nr = st.selectbox("Rol", ["alumno", "profe", "admin"], index=["alumno", "profe", "admin"].index(user_sel["rol"]))
            nc = st.text_input("Curso", user_sel["curso"])
            npw = st.text_input("Contraseña", user_sel["password"])

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Guardar cambios"):
                    user_sel["nombre"] = nn
                    user_sel["apellido"] = na
                    user_sel["rol"] = nr
                    user_sel["curso"] = nc
                    user_sel["password"] = npw
                    guardar_usuarios(usuarios)
                    st.success("Usuario modificado.")
                    st.rerun()

            with col2:
                if st.button("Eliminar usuario"):
                    usuarios = [u for u in usuarios if u["email"] != email_sel]
                    guardar_usuarios(usuarios)
                    st.success("Usuario eliminado.")
                    st.rerun()


    # ============================================
    # 📘 TAB 2 — CURSOS Y MATERIAS
    # ============================================

    with tab_cursos:

        st.subheader("Materias actuales:")

        for c in cursos:
            st.markdown(f"- **{c['id']} — {c['curso']} — {c['materia']}** (prof: {c['email']})")

        st.markdown("---")
        st.subheader("Agregar nueva materia")

        nid = st.text_input("ID")
        ncurso = st.text_input("Curso")
        nmat = st.text_input("Materia")
        nprof = st.text_input("Email del profesor")

        if st.button("Crear materia"):
            cursos.append({
                "id": nid,
                "curso": ncurso,
                "materia": nmat,
                "email": nprof
            })
            guardar_cursos(cursos)
            st.success("Materia creada.")
            st.rerun()

        st.markdown("---")
        st.subheader("Editar materia")

        if cursos:
            sel = st.selectbox(
                "Elegí materia:",
                [f"{c['id']} — {c['curso']} — {c['materia']}" for c in cursos]
            )

            idsel = sel.split(" — ")[0]
            obj = next(c for c in cursos if c["id"] == idsel)

            ei = st.text_input("ID", obj["id"])
            ec = st.text_input("Curso", obj["curso"])
            em = st.text_input("Materia", obj["materia"])
            ep = st.text_input("Profesor", obj["email"])

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Guardar cambios"):
                    obj["id"] = ei
                    obj["curso"] = ec
                    obj["materia"] = em
                    obj["email"] = ep
                    guardar_cursos(cursos)
                    st.success("Actualizado.")
                    st.rerun()

            with col2:
                if st.button("Eliminar materia"):
                    cursos = [c for c in cursos if c["id"] != idsel]
                    guardar_cursos(cursos)
                    st.success("Eliminada.")
                    st.rerun()


    # ============================================
    # 📚 TAB 3 — BASES DE CONOCIMIENTO
    # ============================================

    with tab_bases:

        st.subheader("📖 Base general")

        bg_text = "\n".join(f"{p};{r}" for p, r in st.session_state.base_general)

        edit = st.text_area("Editar base general:", bg_text)

        if st.button("Guardar base general"):
            nueva = []
            for linea in edit.splitlines():
                if ";" in linea:
                    p, r = linea.split(";", 1)
                    nueva.append((p.strip(), r.strip()))
            st.session_state.base_general = nueva
            st.success("Base general actualizada (solo en sesión)")

        st.markdown("---")

        st.subheader("📘 Base específica por materia")

        cursos_unicos = sorted({c["curso"] for c in cursos})

        curso_sel = st.selectbox("Elegir curso:", cursos_unicos)

        materias_sel = [c for c in cursos if c["curso"] == curso_sel]

        for c in materias_sel:
            cname = f"{c['curso']} — {c['materia']}"
            st.markdown(f"### {cname}")

            path = archivo_base_curso_materia(c["curso"], c["materia"])
            contenido = leer_archivo_github(path)

            edit = st.text_area(
                f"Editar {c['materia']}:",
                contenido,
                key=f"edit_base_{c['id']}"
            )

            if st.button(f"Guardar {cname}"):
                escribir_archivo_github(path, edit)
                st.success(f"{cname} actualizado.")
                st.rerun()

