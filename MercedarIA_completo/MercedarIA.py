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

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")

# ============================================
# HELPERS DE NORMALIZACIÓN
# ============================================

def normalizar_curso(curso: str) -> str:
    if not curso:
        return ""
    s = str(curso)
    s = s.replace("\u00a0", " ")      # NBSP → espacio normal
    s = re.sub(r"\s+", " ", s)       # colapsar espacios
    return s.strip()

def normalizar_materia(materia: str) -> str:
    if not materia:
        return ""
    s = str(materia)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def slug_materia(materia: str) -> str:
    s = (materia or "").lower()
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", "_", s)
    reemplazar = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}
    for o, d in reemplazar.items():
        s = s.replace(o, d)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s or "general"

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

# Inicializar en sesión con claves de curso normalizadas
if "base_general" not in st.session_state:
    st.session_state.base_general = BASE_GENERAL_DEFAULT.copy()

if "bases_especificas" not in st.session_state:
    st.session_state.bases_especificas = {
        normalizar_curso(k): v.copy() for k, v in BASES_ESPECIFICAS_DEFAULT.items()
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
        r = requests.get(github_raw_url(path), timeout=10)
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
# FUNCIONES DE DATOS (USERS / COURSES / TASKS)
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
            "curso": normalizar_curso(curso.strip()),
            "password": pw.strip()
        })
    return usuarios

def guardar_usuarios(lista):
    contenido = "\n".join(
        f"{u['email']};{u['nombre']};{u['apellido']};{u['rol']};{u['curso']};{u['password']}"
        for u in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/users.txt", contenido)

def cargar_cursos():
    texto = leer_archivo_github(f"{BASES_ROOT}/courses.txt")
    cursos = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        id_, curso, materia, email_prof = linea.split(";", 3)
        cursos.append({
            "id": id_.strip(),
            "curso": normalizar_curso(curso.strip()),
            "materia": normalizar_materia(materia.strip()),
            "email": email_prof.strip()
        })
    return cursos

def guardar_cursos(lista):
    contenido = "\n".join(
        f"{c['id']};{c['curso']};{c['materia']};{c['email']}" for c in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/courses.txt", contenido)

def cargar_tareas():
    texto = leer_archivo_github(f"{BASES_ROOT}/tasks.txt")
    tareas = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        id_, curso, materia, titulo, descr, creador, fecha = linea.split(";", 6)
        tareas.append({
            "id": id_.strip(),
            "curso": normalizar_curso(curso.strip()),
            "materia": normalizar_materia(materia.strip()),
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

def archivo_base_curso_materia(curso, materia):
    cid = normalizar_curso(curso).replace("°", "").replace(" ", "")
    mid = slug_materia(materia)
    return f"{BASES_ROOT}/{cid}_{mid}.txt"

# ============================================
# CARGA INICIAL + ESTADO
# ============================================

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "modo_anonimo" not in st.session_state:
    st.session_state.modo_anonimo = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🎓 MercedarIA — Asistente del Colegio INSM")

# ============================================
# LOGIN / REGISTRO / MODO INVITADO
# ============================================

if st.session_state.usuario is None and not st.session_state.modo_anonimo:
    st.subheader("🔐 Iniciar sesión")

    col_login, col_reg, col_anon = st.columns([2, 2, 1])

    # ---------- LOGIN ----------
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

    # ---------- REGISTRO ----------
    with col_reg:
        st.subheader("🧾 Crear cuenta")
    
        new_email = st.text_input("Nuevo email", key="reg_email_main")
        new_nombre = st.text_input("Nombre", key="reg_nombre_main")
        new_apellido = st.text_input("Apellido", key="reg_apellido_main")
    
        tipo = st.selectbox("Tipo de cuenta", ["alumno", "profe"], key="reg_tipo_main")
    
        if tipo == "alumno":
            new_curso = st.selectbox(
                "Curso",
                sorted({c["curso"] for c in cursos}),
                key="reg_curso_main"
            )
        else:
            new_curso = "-"
    
        new_pw = st.text_input("Contraseña", type="password", key="reg_pw_main")
    
        admin_key = ""
        if tipo == "profe":
            admin_key = st.text_input(
                "Contraseña de administrador",
                type="password",
                key="reg_admin_pw_main"
            )
    
        if st.button("Crear cuenta", key="reg_btn_main"):
            usuarios = cargar_usuarios()
    
            if any(u["email"].lower() == new_email.lower() for u in usuarios):
                st.error("Ese email ya existe")
            elif tipo == "profe" and admin_key != ADMIN_MASTER_KEY:
                st.error("Contraseña admin incorrecta")
            else:
                usuarios.append({
                    "email": new_email.strip(),
                    "nombre": new_nombre.strip(),
                    "apellido": new_apellido.strip(),
                    "rol": tipo,
                    "curso": new_curso,
                    "password": new_pw.strip()
                })
                guardar_usuarios(usuarios)
                st.success("Cuenta creada correctamente.")
                st.rerun()


    # ---------- MODO ANÓNIMO ----------
    with col_anon:
        st.markdown("### 👤 Invitado")
        if st.button("Entrar como invitado"):
            st.session_state.modo_anonimo = True
            st.session_state.usuario = None
            st.session_state.chat_history = []
            st.rerun()

# ============================================
# CREAR USUARIO LÓGICO (ALUMNO/PROFE/ADMIN/ANÓNIMO)
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

rol = usuario["rol"]
email_usuario = usuario["email"]
curso_usuario = normalizar_curso(usuario["curso"])

# refrescar listas (por si hubo cambios)
usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

# ============================================
# BARRA SUPERIOR: INFO USUARIO + LOGOUT
# ============================================

col_info, col_logout = st.columns([4, 1])

with col_info:
    if rol == "anonimo":
        st.info("Conectado en **modo invitado** — solo se usa la base general de conocimiento.")
    else:
        st.info(
            f"Conectado como **{usuario['nombre']} {usuario['apellido']}** — "
            f"Rol: **{rol}** — Curso: **{curso_usuario}**"
        )

with col_logout:
    if st.button("Cerrar sesión"):
        st.session_state.chat_history = []
        st.session_state.usuario = None
        st.session_state.modo_anonimo = False
        st.rerun()
# ============================================
# FUNCIÓN DEEPSEEK
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
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error consultando DeepSeek: {e}"

# ============================================
# CONSTRUCCIÓN DEL CONTEXTO DEL CHATBOT
# ============================================

def construir_contexto(usuario_actual):

    # ---------- MODO INVITADO ----------
    if usuario_actual["rol"] == "anonimo":
        contexto = (
            "Estás respondiendo a un usuario invitado. "
            "Solo podés usar la BASE GENERAL del colegio.\n\n"
        )
        contexto += "BASE GENERAL:\n"
        for p, r in st.session_state.base_general:
            contexto += f"{p} -> {r}\n"
        return contexto

    curso_u = normalizar_curso(usuario_actual["curso"])

    contexto = "INFORMACIÓN DEL USUARIO:\n"
    contexto += f"Nombre: {usuario_actual['nombre']} {usuario_actual['apellido']}\n"
    contexto += f"Rol: {usuario_actual['rol']}\n"
    contexto += f"Email: {usuario_actual['email']}\n"
    contexto += f"Curso: {curso_u}\n\n"

    # ---------- BASE GENERAL ----------
    contexto += "BASE GENERAL DEL COLEGIO:\n"
    for p, r in st.session_state.base_general:
        contexto += f"{p} -> {r}\n"

    # ---------- BASE ESPECÍFICA DEL CURSO ----------
    base_curso = st.session_state.bases_especificas.get(curso_u, [])
    if base_curso:
        contexto += f"\nBASE ESPECÍFICA DEL CURSO {curso_u}:\n"
        for p, r in base_curso:
            contexto += f"{p} -> {r}\n"

    # ---------- USERS (solo para roles y cursos) ----------
    contexto += "\nUSUARIOS (solo para saber roles y cursos):\n"
    for u in usuarios:
        contexto += (
            f"{u['nombre']} {u['apellido']} ({u['email']}), "
            f"rol: {u['rol']}, curso: {u['curso']}.\n"
        )

    # ---------- COURSES (del curso del usuario) ----------
    contexto += f"\nMATERIAS DEL CURSO {curso_u}:\n"
    for c in cursos:
        if c["curso"] == curso_u:
            contexto += f"{c['materia']} dictada por {c['email']}.\n"

    # ---------- TASKS (solo del curso del usuario) ----------
    contexto += f"\nTAREAS DEL CURSO {curso_u}:\n"
    for t in tareas:
        if t["curso"] == curso_u:
            contexto += (
                f"[{t['materia']}] {t['titulo']} — "
                f"vence {t['fecha_limite']} — creada por {t['creador']}.\n"
            )

    # ---------- BASES TXT POR MATERIA (del curso del usuario) ----------
    contexto += f"\nBASES POR MATERIA (archivos txt) DEL CURSO {curso_u}:\n"
    for c in cursos:
        if c["curso"] == curso_u:
            path = archivo_base_curso_materia(c["curso"], c["materia"])
            contenido = leer_archivo_github(path)
            if contenido.strip():
                contexto += f"\n[{c['materia']}]\n{contenido}\n"

    contexto += (
        "\nIMPORTANTE: respondé SIEMPRE pensando en el curso del usuario. "
        "Si pregunta algo de otro curso, aclarar que solo tenés información de su curso.\n"
    )

    return contexto

# ============================================
# CHAT CON BURBUJAS (OPCIÓN B)
# ============================================

st.subheader("💬 Chat con MercedarIA")

col_in, col_btn = st.columns([4, 1])

with col_in:
    pregunta = st.text_input("Escribí tu pregunta:", key="input_pregunta")

with col_btn:
    if st.button("Enviar", key="btn_enviar"):
        if pregunta.strip():
            contexto = construir_contexto(usuario)
            respuesta = consultar_deepseek(pregunta, contexto)

            st.session_state.chat_history.append(
                {"role": "user", "content": pregunta.strip()}
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": respuesta}
            )
            st.rerun()

# Render del historial en burbujas
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(
            f"""
<div style="text-align:right; margin:4px 0;">
  <div style="
      display:inline-block;
      background:#71b548;
      color:#ffffff;
      padding:10px 14px;
      border-radius:16px;
      max-width:70%;
      box-shadow:0 0 6px rgba(0,0,0,0.25);
      word-wrap:break-word;
  ">
    {msg["content"]}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
<div style="text-align:left; margin:4px 0;">
  <div style="
      display:inline-block;
      background:#23263d;
      color:#ffffff;
      padding:10px 14px;
      border-radius:16px;
      max-width:70%;
      box-shadow:0 0 6px rgba(0,0,0,0.25);
      word-wrap:break-word;
  ">
    {msg["content"]}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown("---")
# ============================================
# 📝 TAREAS — ALUMNO / PROFE / ADMIN
# ============================================

st.header("📝 Tareas")
# ---------- ANONIMO ----------
if rol == "anonimo":
    st.info("🔐 Iniciá sesión como alumno para ver tus tareas.")
    st.stop()

# ---------- ALUMNO ----------
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
---
""")

# ---------- PROFESOR ----------
elif rol == "profe":

    st.subheader("Crear nueva tarea")

    materias_mias = [c for c in cursos if c["email"] == email_usuario]

    if not materias_mias:
        st.info("No tenés materias asignadas.")
    else:
        opcion = st.selectbox(
            "Elegí curso y materia",
            [f"{c['curso']} — {c['materia']}" for c in materias_mias],
            key="select_curso_materia_tarea"
        )

        curso_sel, materia_sel = opcion.split(" — ", 1)
        curso_sel = normalizar_curso(curso_sel)
        materia_sel = normalizar_materia(materia_sel)

        titulo = st.text_input("Título de la tarea", key="new_titulo_tarea")
        descr = st.text_area("Descripción", key="new_descr_tarea")
        fecha = st.date_input("Fecha límite", key="new_fecha_tarea")

        if st.button("Agregar tarea", key="btn_add_tarea"):
            if not titulo.strip():
                st.warning("Tenés que poner un título.")
            else:
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
            st.info("Todavía no creaste tareas.")
        else:
            for t in mis_tareas:
                with st.expander(f"{t['curso']} — {t['materia']} — {t['titulo']}", expanded=False):
                    nt = st.text_input("Título", value=t["titulo"], key=f"edit_t_{t['id']}")
                    nd = st.text_area("Descripción", value=t["descripcion"], key=f"edit_d_{t['id']}")
                    nf = st.text_input("Fecha límite (YYYY-MM-DD)", value=t["fecha_limite"], key=f"edit_f_{t['id']}")

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Guardar cambios", key=f"btn_save_{t['id']}"):
                            t["titulo"] = nt.strip()
                            t["descripcion"] = nd.strip()
                            t["fecha_limite"] = nf.strip()
                            guardar_tareas(tareas)
                            st.success("Tarea actualizada.")
                            st.rerun()

                    with col2:
                        if st.button("Eliminar tarea", key=f"btn_del_{t['id']}"):
                            tareas = [x for x in tareas if x["id"] != t["id"]]
                            guardar_tareas(tareas)
                            st.success("Tarea eliminada.")
                            st.rerun()

# ---------- ADMIN ----------
elif rol == "admin":
    st.subheader("Todas las tareas (modo admin)")
    if not tareas:
        st.info("No hay tareas cargadas.")
    else:
        for t in tareas:
            st.markdown(f"""
**[{t['id']}] {t['titulo']}**  
🏫 Curso: {t['curso']} — 📚 Materia: {t['materia']}  
📌 {t['descripcion']}  
⏳ Vence: {t['fecha_limite']}  
👨‍🏫 Creador: {t['creador']}  
---
""")


# ============================================
# ⚙️ PANEL DEL ADMINISTRADOR
# ============================================

if rol == "admin":

    st.header("⚙️ Panel de Administración")

    tab_users, tab_courses, tab_bases = st.tabs(
        ["👥 Usuarios", "📘 Cursos y materias", "📚 Bases de conocimiento"]
    )

    # ---------- TAB USUARIOS ----------
    with tab_users:
        st.subheader("Usuarios existentes")

        for u in usuarios:
            st.markdown(f"- **{u['email']}** — Rol: {u['rol']} — Curso: {u['curso']}")

        st.markdown("---")
        st.subheader("Modificar / eliminar usuario")

        if usuarios:
            email_sel = st.selectbox(
                "Elegí un usuario",
                [u["email"] for u in usuarios],
                key="admin_sel_user"
            )
            user_sel = next(u for u in usuarios if u["email"] == email_sel)

            nn = st.text_input("Nombre", user_sel["nombre"], key="admin_u_nom")
            na = st.text_input("Apellido", user_sel["apellido"], key="admin_u_ape")
            nr = st.selectbox(
                "Rol",
                ["alumno", "profe", "admin"],
                index=["alumno", "profe", "admin"].index(user_sel["rol"]),
                key="admin_u_rol"
            )
            nc = st.text_input("Curso (para alumnos, ej: 6° B; para otros -)", user_sel["curso"], key="admin_u_curso")
            npw = st.text_input("Contraseña", user_sel["password"], key="admin_u_pw")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Guardar cambios usuario", key="btn_admin_save_user"):
                    user_sel["nombre"] = nn.strip()
                    user_sel["apellido"] = na.strip()
                    user_sel["rol"] = nr.strip()
                    user_sel["curso"] = normalizar_curso(nc.strip())
                    user_sel["password"] = npw.strip()
                    guardar_usuarios(usuarios)
                    st.success("Usuario actualizado.")
                    st.rerun()

            with col2:
                if st.button("🗑 Eliminar usuario", key="btn_admin_del_user"):
                    usuarios = [u for u in usuarios if u["email"] != email_sel]
                    guardar_usuarios(usuarios)
                    st.success("Usuario eliminado.")
                    st.rerun()

    # ---------- TAB CURSOS ----------
    with tab_courses:
        st.subheader("Cursos y materias actuales")

        for c in cursos:
            st.markdown(
                f"- **{c['id']} — {c['curso']} — {c['materia']}** (prof: {c['email']})"
            )

        st.markdown("---")
        st.subheader("Agregar curso/materia")

        nid = st.text_input("ID", key="admin_c_id")
        ncurso = st.text_input("Curso (ej: 6° B)", key="admin_c_curso")
        nmat = st.text_input("Materia", key="admin_c_mat")
        nprof = st.text_input("Email del profesor", key="admin_c_prof")

        if st.button("Crear materia nueva", key="btn_admin_add_course"):
            cursos.append({
                "id": nid.strip(),
                "curso": normalizar_curso(ncurso.strip()),
                "materia": normalizar_materia(nmat.strip()),
                "email": nprof.strip()
            })
            guardar_cursos(cursos)
            st.success("Materia agregada.")
            st.rerun()

        st.markdown("---")
        st.subheader("Editar / eliminar materia")

        if cursos:
            sel = st.selectbox(
                "Elegí materia",
                [f"{c['id']} — {c['curso']} — {c['materia']}" for c in cursos],
                key="admin_sel_course"
            )
            idsel = sel.split(" — ")[0]
            cobj = next(c for c in cursos if c["id"] == idsel)

            ei = st.text_input("ID", cobj["id"], key="admin_edit_c_id")
            ec = st.text_input("Curso", cobj["curso"], key="admin_edit_c_curso")
            em = st.text_input("Materia", cobj["materia"], key="admin_edit_c_mat")
            ep = st.text_input("Profesor (email)", cobj["email"], key="admin_edit_c_prof")

            colc1, colc2 = st.columns(2)

            with colc1:
                if st.button("💾 Guardar cambios materia", key="btn_admin_save_course"):
                    cobj["id"] = ei.strip()
                    cobj["curso"] = normalizar_curso(ec.strip())
                    cobj["materia"] = normalizar_materia(em.strip())
                    cobj["email"] = ep.strip()
                    guardar_cursos(cursos)
                    st.success("Materia actualizada.")
                    st.rerun()

            with colc2:
                if st.button("🗑 Eliminar materia", key="btn_admin_del_course"):
                    cursos = [c for c in cursos if c["id"] != idsel]
                    guardar_cursos(cursos)
                    st.success("Materia eliminada.")
                    st.rerun()

    # ---------- TAB BASES ----------
    with tab_bases:
        st.subheader("📖 Base general (pregunta;respuesta por línea)")

        texto_bg = "\n".join(f"{p};{r}" for p, r in st.session_state.base_general)

        edit_bg = st.text_area(
            "Editar base general:",
            value=texto_bg,
            height=200,
            key="admin_bg_text"
        )

        if st.button("💾 Guardar base general", key="btn_admin_save_bg"):
            nueva = []
            for linea in edit_bg.splitlines():
                if ";" in linea:
                    p, r = linea.split(";", 1)
                    nueva.append((p.strip(), r.strip()))
            if nueva:
                st.session_state.base_general = nueva
                st.success("Base general actualizada (se guarda solo en sesión).")
            else:
                st.error("No se detectaron líneas válidas.")

        st.markdown("---")
        st.subheader("📘 Base específica por curso (pregunta;respuesta por línea)")

        cursos_base = sorted(st.session_state.bases_especificas.keys())

        if cursos_base:
            curso_base_sel = st.selectbox(
                "Curso a editar",
                cursos_base,
                key="admin_sel_base_curso"
            )
            lista_faq = st.session_state.bases_especificas.get(curso_base_sel, [])
            texto_faq = "\n".join(f"{p};{r}" for p, r in lista_faq)

            edit_faq = st.text_area(
                f"Editar base específica de {curso_base_sel}:",
                value=texto_faq,
                height=200,
                key="admin_texto_base_especifica"
            )

            if st.button("💾 Guardar base específica del curso", key="btn_admin_save_base_curso"):
                nueva_faq = []
                for linea in edit_faq.splitlines():
                    if ";" in linea:
                        p, r = linea.split(";", 1)
                        nueva_faq.append((p.strip(), r.strip()))
                st.session_state.bases_especificas[curso_base_sel] = nueva_faq
                st.success("Base específica actualizada (solo en sesión).")
        else:
            st.info("No hay bases específicas por curso cargadas.")

        st.markdown("---")
        st.subheader("📂 Bases por materia (archivos txt en GitHub)")

        cursos_unicos = sorted({c["curso"] for c in cursos})
        if cursos_unicos:
            curso_sel_bases = st.selectbox(
                "Curso",
                cursos_unicos,
                key="admin_sel_curso_txt"
            )
            materias_sel = [c for c in cursos if c["curso"] == curso_sel_bases]

            for c in materias_sel:
                cname = f"{c['curso']} — {c['materia']}"
                st.markdown(f"### {cname}")

                path = archivo_base_curso_materia(c["curso"], c["materia"])
                contenido_m = leer_archivo_github(path)

                edit_m = st.text_area(
                    f"Contenido de {c['materia']} (txt en GitHub):",
                    value=contenido_m,
                    height=160,
                    key=f"admin_txt_{c['id']}"
                )

                if st.button(f"💾 Guardar {cname}", key=f"btn_admin_save_txt_{c['id']}"):
                    escribir_archivo_github(path, edit_m)
                    st.success(f"Base de {cname} actualizada.")
                    st.rerun()
        else:
            st.info("No hay cursos en courses.txt.")

