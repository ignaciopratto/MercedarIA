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
# HELPERS
# ============================================

def normalizar(texto: str) -> str:
    if not texto:
        return ""
    return texto.replace("\u00a0", " ").strip()


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
    except Exception:
        return ""


def escribir_archivo_github(path, contenido):
    url = github_api_url(path)
    try:
        r_get = requests.get(
            url,
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
            },
            timeout=10,
        )
        sha = r_get.json().get("sha") if r_get.status_code == 200 else None
    except Exception:
        sha = None

    data = {
        "message": f"Actualizando {path}",
        "content": base64.b64encode(contenido.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        data["sha"] = sha

    r_put = requests.put(
        url,
        json=data,
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        timeout=10,
    )
    return r_put.status_code in (200, 201)


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
        usuarios.append(
            {
                "email": email.strip(),
                "nombre": nombre.strip(),
                "apellido": apellido.strip(),
                "rol": rol.strip(),
                "curso": normalizar(curso.strip()),
                "password": pw.strip(),
            }
        )
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
        cursos.append(
            {
                "id": id_.strip(),
                "curso": normalizar(curso.strip()),
                "materia": normalizar(materia.strip()),
                "email": email_prof.strip(),
            }
        )
    return cursos


def guardar_cursos(lista):
    contenido = "\n".join(
        f"{c['id']};{c['curso']};{c['materia']};{c['email']}" for c in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/courses.txt", contenido)


# ============================================
# TASKS
# ============================================

def generar_id_unico(tareas):
    usados = {int(t["id"]) for t in tareas if t["id"].isdigit()}
    nuevo = 1
    while nuevo in usados:
        nuevo += 1
    return str(nuevo)


def cargar_tareas():
    texto = leer_archivo_github(f"{BASES_ROOT}/tasks.txt")
    tareas = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        id_, curso, materia, titulo, descr, creador, fecha = linea.split(";", 6)
        tareas.append(
            {
                "id": id_.strip(),
                "curso": normalizar(curso.strip()),
                "materia": normalizar(materia.strip()),
                "titulo": titulo.strip(),
                "descripcion": descr.strip(),
                "creador": creador.strip(),
                "fecha_limite": fecha.strip(),
            }
        )
    return tareas


def guardar_tareas(lista):
    contenido = "\n".join(
        f"{t['id']};{t['curso']};{t['materia']};{t['titulo']};"
        f"{t['descripcion']};{t['creador']};{t['fecha_limite']}"
        for t in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/tasks.txt", contenido)


# ============================================
# ARCHIVOS POR MATERIA
# ============================================

def archivo_base_curso_materia(curso, materia):
    cid = normalizar(curso).replace("°", "").replace(" ", "")
    mid = re.sub(r"[^a-z0-9]", "", normalizar(materia).lower())
    return f"{BASES_ROOT}/{cid}_{mid}.txt"


# ============================================
# BASES GENERAL Y ESPECÍFICAS (EN MEMORIA)
# ============================================

BASE_GENERAL_DEFAULT = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quién eres", "Soy MercedarIA, tu asistente del Colegio Mercedaria."),
    ("cómo te llamas", "Me llamo MercedarIA, tu asistente virtual."),
    ("cómo estás", "Estoy funcionando perfectamente, gracias por preguntar."),
    ("adiós", "¡Hasta luego! Que tengas un buen día."),
    ("quién es la directora", "La directora es Marisa Brizzio."),
    (
        "cuándo son los recreos",
        "Turno mañana: 8:35, 10:00, 11:35. Turno tarde: 14:40, 16:05, 17:50.",
    ),
    ("dónde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456."),
    ("cuándo empieza el ciclo lectivo", "El ciclo lectivo comienza el primer día hábil de marzo."),
    ("cuándo terminan las clases", "Generalmente a mediados de diciembre."),
]

BASES_ESPECIFICAS_DEFAULT = {
    "1° A": [
        (
            "¿Qué materias tengo?",
            "Biología, Educación en Artes Visuales, Lengua y Literatura, Física, Geografía, Educación Tecnológica, Matemática, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés y Educación Física.",
        ),
        ("¿Cuáles son mis contraturnos?", "Educación Física y Educación Tecnológica."),
        ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."),
    ],
    "1° B": [
        (
            "¿Qué materias tengo?",
            "Física, Matemática, Educación en Artes Visuales, Inglés, Educación Religiosa Escolar, Lengua y Literatura, Geografía, Ciudadanía y Participación, Educación Tecnológica, Biología y Educación Física.",
        ),
        ("¿Cuáles son mis contraturnos?", "Educación Tecnológica y Educación Física."),
        ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."),
    ],
    "2° A": [
        (
            "¿Qué materias tengo?",
            "Matemática, Lengua y Literatura, Educación Religiosa Escolar, Música, Historia, Educación Tecnológica, Química, Computación, Ciudadanía y Participación, Biología, Inglés y Educación Física.",
        ),
        ("¿Cuáles son mis contraturnos?", "Educación Física."),
        ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."),
    ],
    "2° B": [
        (
            "¿Qué materias tengo?",
            "Música, Historia, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés, Matemática, Lengua y Literatura, Educación Tecnológica, Química, Biología y Educación Física.",
        ),
        ("¿Cuáles son mis contraturnos?", "Educación Física."),
        ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."),
    ],
    "3° A": [
        (
            "¿Qué materias tengo?",
            "Lengua y Literatura, Inglés, Historia, Geografía, Química, Educación Tecnológica, Física, Educación Religiosa Escolar, Formación para la Vida y el Trabajo, Matemática, Educación Artística Visual, Música, Computación y Educación Física.",
        ),
        ("¿Cuáles son mis contraturnos?", "Educación Física y Formación para la Vida y el Trabajo."),
        ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."),
    ],
    "3° B": [
        (
            "¿Qué materias tengo?",
            "Lengua y Literatura, Formación para la Vida y el Trabajo, Física, Historia, Geografía, Educación Artística Visual, Música, Matemática, Educación Tecnológica, Química, Computación, Educación Religiosa Escolar, Educación Física e Inglés.",
        ),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."),
    ],
    "4° A": [
        (
            "¿Qué materias tengo?",
            "Historia, Lengua y Literatura, Biología, ERE, Matemática, Geografía, Educ. Artística, FVT, TIC, Sociedad y Comunicación, Antropología, Educación Física e Inglés.",
        ),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."),
    ],
    "4° B": [
        (
            "¿Qué materias tengo?",
            "Lengua y Literatura, Biología, ERE, Historia, Programación, Geografía, Matemática, Sistemas Digitales, FVT, Educación Artística, Educación Física e Inglés.",
        ),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."),
    ],
    "5° A": [
        (
            "¿Qué materias tengo?",
            "Metodología, Historia, Física, Geografía, Arte Cultural y Social, ERE, Lengua y Literatura, FVT, Matemática, EF, Psicología, Sociología e Inglés.",
        ),
        ("¿Cuáles son mis contraturnos?", "EF, Psicología, Sociología e Inglés."),
        ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."),
    ],
    "5° B": [
        (
            "¿Qué materias tengo?",
            "Robótica, Música, Física, Matemática, Historia, Lengua y Literatura, FVT, Sistemas Digitales, Geografía, Psicología, EF, Desarrollo Informático e Inglés.",
        ),
        ("¿Cuáles son mis contraturnos?", "EF, Sistemas Digitales, Desarrollo Informático e Inglés."),
        ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."),
    ],
    "6° A": [
        (
            "¿Qué materias tengo?",
            "Ciudadanía y Política, Economía Política, Matemática, Geografía, Filosofía, Química, Lengua y Literatura, Historia, ERE, Sociedad y Comunicación, Teatro, FVT, EF e Inglés.",
        ),
        ("¿Cuáles son mis contraturnos?", "EF, Sociedad y Comunicación e Inglés."),
        ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."),
    ],
    "6° B": [
        (
            "¿Qué materias tengo?",
            "Lengua y Literatura, Comunicación Audiovisual, Desarrollo de Soluciones Informáticas, Informática Aplicada, Filosofía, Formación para la Vida y el Trabajo, Química, Matemática, ERE, Ciudadanía y Política, Teatro, EF, Aplicaciones Informáticas e Inglés.",
        ),
        ("¿Cuáles son mis contraturnos?", "EF, Aplicaciones Informáticas e Inglés."),
        ("¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."),
    ],
}

# Estado en memoria
if "base_general" not in st.session_state:
    st.session_state.base_general = BASE_GENERAL_DEFAULT.copy()

if "bases_por_curso" not in st.session_state:
    st.session_state.bases_por_curso = {
        c: v.copy() for c, v in BASES_ESPECIFICAS_DEFAULT.items()
    }


# ============================================
# CARGA INICIAL Y CONFIG PÁGINA
# ============================================

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "modo_anonimo" not in st.session_state:
    st.session_state.modo_anonimo = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🎓 MercedarIA — Asistente del Colegio INSM")


# ============================================
# LOGIN / REGISTRO / INVITADO
# ============================================

if st.session_state.usuario is None and not st.session_state.modo_anonimo:

    col_login, col_reg, col_anon = st.columns([2, 2, 1])

    # ---------- LOGIN ----------
    with col_login:
        st.subheader("🔐 Iniciar sesión")

        email = st.text_input("Email", key="login_email")
        pw = st.text_input("Contraseña", type="password", key="login_pw")

        if st.button("Ingresar", key="btn_login"):
            usuarios = cargar_usuarios()
            user = next(
                (
                    u
                    for u in usuarios
                    if u["email"].lower() == email.lower()
                    and u["password"] == pw
                ),
                None,
            )
            if user:
                st.session_state.usuario = user
                st.success(f"Bienvenido/a {user['nombre']} {user['apellido']}")
                st.rerun()
            else:
                st.error("Email o contraseña incorrectos.")
                st.stop()

    # ---------- REGISTRO ----------
    with col_reg:
        st.subheader("🧾 Crear cuenta")

        new_email = st.text_input("Nuevo email", key="reg_email")
        new_nombre = st.text_input("Nombre", key="reg_nombre")
        new_apellido = st.text_input("Apellido", key="reg_apellido")

        tipo = st.selectbox(
            "Tipo de cuenta", ["alumno", "profe"], key="reg_tipo_cuenta"
        )

        if tipo == "alumno":
            new_curso = st.selectbox(
                "Curso",
                sorted({c["curso"] for c in cursos}),
                key="reg_curso",
            )
        else:
            new_curso = "-"

        new_pw = st.text_input(
            "Contraseña", type="password", key="reg_password"
        )

        admin_key = ""
        if tipo == "profe":
            admin_key = st.text_input(
                "Contraseña de administrador",
                type="password",
                key="reg_admin_key",
            )

        if st.button("Crear cuenta", key="btn_crear_cuenta"):
            usuarios = cargar_usuarios()
            if any(u["email"].lower() == new_email.lower() for u in usuarios):
                st.error("Ya existe un usuario con ese email.")
            elif tipo == "profe" and admin_key != ADMIN_MASTER_KEY:
                st.error("Contraseña de administrador incorrecta.")
            elif not new_email or not new_nombre or not new_apellido or not new_pw:
                st.error("Completá todos los campos.")
            else:
                usuarios.append(
                    {
                        "email": new_email.strip(),
                        "nombre": new_nombre.strip(),
                        "apellido": new_apellido.strip(),
                        "rol": tipo,
                        "curso": new_curso.strip(),
                        "password": new_pw.strip(),
                    }
                )
                guardar_usuarios(usuarios)
                st.success("Cuenta creada. Ya podés iniciar sesión.")
                st.rerun()

    # ---------- INVITADO ----------
    with col_anon:
        st.subheader("👤 Invitado")
        if st.button("Entrar como invitado", key="btn_anonimo"):
            st.session_state.modo_anonimo = True
            st.rerun()

# ============================================
# USUARIO ACTUAL
# ============================================

if st.session_state.modo_anonimo:
    usuario = {
        "email": "anonimo@insm.edu",
        "nombre": "Invitado",
        "apellido": "",
        "rol": "anonimo",
        "curso": "General",
    }
else:
    usuario = st.session_state.usuario
# ============================================
# DATOS USUARIO + RECARGA BASES
# ============================================

if usuario is None:
    st.warning("Por favor, iniciá sesión o entrá como invitado.")
    st.stop()

rol = usuario["rol"]
email_usuario = usuario["email"]
curso_usuario = normalizar(usuario.get("curso", ""))

# recargar siempre desde GitHub
usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

# ============================================
# BARRA SUPERIOR + CERRAR SESIÓN
# ============================================

col_info, col_logout = st.columns([4, 1])

with col_info:
    if rol == "anonimo":
        st.info("Conectado en **modo invitado** — solo base general.")
    else:
        st.info(
            f"Conectado como **{usuario['nombre']} {usuario['apellido']}** — "
            f"Rol: **{rol}** — Curso: **{curso_usuario}**"
        )

with col_logout:
    if st.button("Cerrar sesión", key="btn_logout"):
        st.session_state.usuario = None
        st.session_state.modo_anonimo = False
        st.session_state.chat_history = []
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
# CONSTRUIR CONTEXTO
# ============================================

def construir_contexto(usuario_actual, usuarios, cursos, tareas):
    rol_u = usuario_actual["rol"]
    curso_u = normalizar(usuario_actual.get("curso", ""))

    # INVITADO
    if rol_u == "anonimo":
        contexto = (
            "Estás respondiendo a un usuario INVITADO.\n"
            "Solo podés usar la BASE GENERAL del colegio.\n"
            "No inventes datos personales ni de cursos específicos.\n\n"
        )
        contexto += "BASE GENERAL DEL COLEGIO:\n"
        for p, r in st.session_state.base_general:
            contexto += f"{p} -> {r}\n"
        return contexto

    # LOGUEADO
    contexto = "INFORMACIÓN DEL USUARIO LOGUEADO:\n"
    contexto += f"- Nombre: {usuario_actual['nombre']} {usuario_actual['apellido']}\n"
    contexto += f"- Rol: {rol_u}\n"
    contexto += f"- Email: {usuario_actual['email']}\n"
    contexto += f"- Curso: {curso_u}\n\n"

    contexto += "BASE GENERAL DEL COLEGIO:\n"
    for p, r in st.session_state.base_general:
        contexto += f"{p} -> {r}\n"

    base_curso = st.session_state.bases_por_curso.get(curso_u, [])
    if base_curso:
        contexto += f"\nBASE ESPECÍFICA DEL CURSO {curso_u}:\n"
        for p, r in base_curso:
            contexto += f"{p} -> {r}\n"

    contexto += "\nUSUARIOS REGISTRADOS:\n"
    for u in usuarios:
        contexto += (
            f"- {u['nombre']} {u['apellido']} ({u['email']}), "
            f"rol: {u['rol']}, curso: {u['curso']}.\n"
        )

    contexto += f"\nMATERIAS DEL CURSO {curso_u}:\n"
    materias_curso = [c for c in cursos if c["curso"] == curso_u]
    for c in materias_curso:
        contexto += f"- {c['materia']} dictada por {c['email']}.\n"

    contexto += f"\nTAREAS DEL CURSO {curso_u}:\n"
    tareas_curso = [t for t in tareas if t["curso"] == curso_u]
    for t in tareas_curso:
        contexto += (
            f"- [{t['materia']}] {t['titulo']} — vence {t['fecha_limite']} — "
            f"creada por {t['creador']}.\n"
        )

    contexto += (
        f"\nBASES TXT POR MATERIA DEL CURSO {curso_u}:\n"
        "(formato: pregunta;respuesta por línea)\n"
    )
    for c in materias_curso:
        path = archivo_base_curso_materia(c["curso"], c["materia"])
        contenido = leer_archivo_github(path)
        if contenido.strip():
            contexto += f"\n[MATERIA: {c['materia']}]\n{contenido}\n"

    contexto += (
        "\nINSTRUCCIONES:\n"
        "- Respondé siempre pensando en el curso del usuario.\n"
        "- Si pregunta por otros cursos, aclarar que solo tenés info de su curso.\n"
        "- No inventes datos que no estén en el contexto.\n"
    )
    return contexto


# ============================================
# CHAT CON BURBUJAS
# ============================================

st.subheader("💬 Chat con MercedarIA")

col_inp, col_btn = st.columns([4, 1])

with col_inp:
    pregunta = st.text_input("Escribí tu pregunta:", key="campo_pregunta")

with col_btn:
    if st.button("Enviar", key="btn_enviar_chat"):
        if pregunta.strip():
            contexto = construir_contexto(usuario, usuarios, cursos, tareas)
            respuesta = consultar_deepseek(pregunta, contexto)

            st.session_state.chat_history.append(
                {"role": "user", "content": pregunta.strip()}
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": respuesta}
            )
            st.rerun()

# Render historial
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        # BURBUJA USUARIO
        st.markdown(
            f"""
<div style="text-align:right; margin:6px 0;">
  <div style="
      display:inline-block;
      background-color:#71b548;
      color:#ffffff;
      padding:10px 14px;
      border-radius:16px;
      max-width:75%;
      box-shadow:0 0 6px rgba(0,0,0,0.25);
      word-wrap:break-word;
      white-space:pre-wrap;
  ">
    {msg["content"]}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        # BURBUJA IA
        st.markdown(
            f"""
<div style="text-align:left; margin:6px 0;">
  <div style="
      display:inline-block;
      background-color:#23263d;
      color:#ffffff;
      padding:10px 14px;
      border-radius:16px;
      max-width:75%;
      box-shadow:0 0 6px rgba(0,0,0,0.25);
      word-wrap:break-word;
      white-space:pre-wrap;
  ">
    {msg["content"]}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown("---")
# ============================================
# TAREAS / PANEL POR ROL
# ============================================

st.header("📝 Tareas")

# INVITADO
if rol == "anonimo":
    st.info("🔒 Iniciá sesión para ver tus tareas.")
    st.stop()

# ================= ALUMNO ====================

if rol == "alumno":

    st.subheader("📘 Tareas de tu curso")

    tareas_curso = [t for t in tareas if t["curso"] == curso_usuario]

    if not tareas_curso:
        st.info("No hay tareas asignadas a tu curso.")
    else:
        for t in tareas_curso:
            st.markdown(
                f"""
### 📚 {t['titulo']}
**Materia:** {t['materia']}  
**Descripción:** {t['descripcion']}  
**Fecha límite:** {t['fecha_limite']}  
**Profesor:** {t['creador']}  
---
"""
            )

# ================= PROFESOR ==================

elif rol == "profe":

    st.subheader("📘 Mis materias asignadas")

    materias_mias = [c for c in cursos if c["email"] == email_usuario]

    if not materias_mias:
        st.info("No tenés materias asignadas en courses.txt.")
    else:
        # CREAR TAREA
        st.markdown("## ➕ Crear nueva tarea")

        opcion = st.selectbox(
            "Elegí curso — materia",
            [f"{c['curso']} — {c['materia']}" for c in materias_mias],
            key="select_curso_materia_tarea",
        )

        curso_sel, materia_sel = opcion.split(" — ", 1)

        titulo = st.text_input("Título de la tarea", key="nuevo_titulo_tarea")
        descr = st.text_area("Descripción", key="nuevo_descr_tarea")
        fecha = st.date_input("Fecha límite", key="nuevo_fecha_tarea")

        if st.button("Agregar tarea", key="btn_agregar_tarea"):
            tareas = cargar_tareas()
            nuevo_id = generar_id_unico(tareas)

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
            st.success("📌 Tarea agregada correctamente.")
            st.rerun()

        st.markdown("---")
        st.markdown("## ✏️ Editar / borrar mis tareas")

        tareas_mias = [t for t in tareas if t["creador"] == email_usuario]

        if not tareas_mias:
            st.info("Todavía no creaste tareas.")
        else:
            for t in tareas_mias:
                with st.expander(
                    f"{t['curso']} — {t['materia']} — {t['titulo']}",
                    expanded=False,
                ):
                    ntitulo = st.text_input(
                        "Título",
                        value=t["titulo"],
                        key=f"edit_titulo_{t['id']}",
                    )
                    ndescr = st.text_area(
                        "Descripción",
                        value=t["descripcion"],
                        key=f"edit_descr_{t['id']}",
                    )
                    nfecha = st.text_input(
                        "Fecha límite (YYYY-MM-DD)",
                        value=t["fecha_limite"],
                        key=f"edit_fecha_{t['id']}",
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            f"Guardar cambios {t['id']}",
                            key=f"btn_guardar_tarea_{t['id']}",
                        ):
                            tareas = cargar_tareas()
                            for x in tareas:
                                if x["id"] == t["id"]:
                                    x["titulo"] = ntitulo.strip()
                                    x["descripcion"] = ndescr.strip()
                                    x["fecha_limite"] = nfecha.strip()
                            guardar_tareas(tareas)
                            st.success("Tarea actualizada.")
                            st.rerun()

                    with col2:
                        if st.button(
                            f"Eliminar tarea {t['id']}",
                            key=f"btn_borrar_tarea_{t['id']}",
                        ):
                            tareas = cargar_tareas()
                            tareas = [x for x in tareas if x["id"] != t["id"]]
                            guardar_tareas(tareas)
                            st.success("Tarea eliminada.")
                            st.rerun()

# ================= ADMIN =====================

elif rol == "admin":

    st.header("⚙️ Panel de Administración")

    tab_users, tab_courses, tab_bases = st.tabs(
        ["👥 Usuarios", "📘 Cursos y materias", "📚 Bases de conocimiento"]
    )

    # ---------- TAB USUARIOS ----------
    with tab_users:
        st.subheader("Usuarios registrados")

        for u in usuarios:
            st.markdown(
                f"- **{u['email']}** — Rol: {u['rol']} — Curso: {u['curso']}"
            )

        st.markdown("---")
        st.subheader("Modificar / eliminar usuario")

        if usuarios:
            email_sel = st.selectbox(
                "Elegí un usuario",
                [u["email"] for u in usuarios],
                key="admin_select_user",
            )
            user_sel = next(u for u in usuarios if u["email"] == email_sel)

            nom_edit = st.text_input(
                "Nombre",
                value=user_sel["nombre"],
                key="admin_edit_nombre",
            )
            ape_edit = st.text_input(
                "Apellido",
                value=user_sel["apellido"],
                key="admin_edit_apellido",
            )
            rol_edit = st.selectbox(
                "Rol",
                ["alumno", "profe", "admin"],
                index=["alumno", "profe", "admin"].index(user_sel["rol"]),
                key="admin_edit_rol",
            )
            curso_edit = st.text_input(
                "Curso (para alumnos, ej: 1° B; para otros poner -)",
                value=user_sel["curso"],
                key="admin_edit_curso",
            )
            pw_edit = st.text_input(
                "Contraseña",
                value=user_sel["password"],
                key="admin_edit_pw",
            )

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                if st.button(
                    "💾 Guardar cambios usuario",
                    key="btn_admin_guardar_user",
                ):
                    usuarios = cargar_usuarios()
                    for u in usuarios:
                        if u["email"] == email_sel:
                            u["nombre"] = nom_edit.strip()
                            u["apellido"] = ape_edit.strip()
                            u["rol"] = rol_edit.strip()
                            u["curso"] = curso_edit.strip()
                            u["password"] = pw_edit.strip()
                    guardar_usuarios(usuarios)
                    st.success("Usuario actualizado.")
                    st.rerun()
            with col_u2:
                if st.button(
                    "🗑 Eliminar usuario", key="btn_admin_borrar_user"
                ):
                    usuarios = cargar_usuarios()
                    usuarios = [u for u in usuarios if u["email"] != email_sel]
                    guardar_usuarios(usuarios)
                    st.success("Usuario eliminado.")
                    st.rerun()

    # ---------- TAB CURSOS ----------
    with tab_courses:
        st.subheader("Cursos y materias existentes")

        for c_obj in cursos:
            st.markdown(
                f"- **{c_obj['curso']} — {c_obj['materia']}** "
                f"(prof: {c_obj['email']})"
            )

        st.markdown("---")
        st.subheader("Agregar curso/materia")

        idc = st.text_input("ID del curso (número)", key="admin_id_curso")
        curso_n = st.text_input("Curso (ej: 1° B)", key="admin_curso_nombre")
        materia_n = st.text_input(
            "Materia (ej: Matemática)", key="admin_materia_nombre"
        )
        prof_n = st.text_input(
            "Email del profesor", key="admin_prof_email"
        )

        if st.button("Crear materia nueva", key="btn_admin_crear_materia"):
            cursos = cargar_cursos()
            cursos.append(
                {
                    "id": idc.strip(),
                    "curso": normalizar(curso_n.strip()),
                    "materia": normalizar(materia_n.strip()),
                    "email": prof_n.strip(),
                }
            )
            guardar_cursos(cursos)
            st.success("Materia agregada.")
            st.rerun()

        st.markdown("---")
        st.subheader("Editar / eliminar materia")

        if cursos:
            mat_sel = st.selectbox(
                "Elegí materia",
                [f"{c['id']} — {c['curso']} — {c['materia']}" for c in cursos],
                key="admin_course_sel",
            )

            idsel = mat_sel.split(" — ")[0]
            course_obj = next(c for c in cursos if c["id"] == idsel)

            ec_id = st.text_input(
                "ID:", course_obj["id"], key="admin_edit_id"
            )
            ec_curso = st.text_input(
                "Curso:", course_obj["curso"], key="admin_edit_curso2"
            )
            ec_mat = st.text_input(
                "Materia:", course_obj["materia"], key="admin_edit_materia"
            )
            ec_prof = st.text_input(
                "Profesor:", course_obj["email"], key="admin_edit_prof"
            )

            colc1, colc2 = st.columns(2)

            with colc1:
                if st.button(
                    "Guardar materia", key="btn_admin_guardar_materia"
                ):
                    cursos = cargar_cursos()
                    for c in cursos:
                        if c["id"] == idsel:
                            c["id"] = ec_id.strip()
                            c["curso"] = normalizar(ec_curso.strip())
                            c["materia"] = normalizar(ec_mat.strip())
                            c["email"] = ec_prof.strip()
                    guardar_cursos(cursos)
                    st.success("Materia actualizada.")
                    st.rerun()

            with colc2:
                if st.button(
                    "Eliminar materia", key="btn_admin_borrar_materia"
                ):
                    cursos = cargar_cursos()
                    cursos = [c for c in cursos if c["id"] != idsel]
                    guardar_cursos(cursos)
                    st.success("Materia eliminada.")
                    st.rerun()

    # ---------- TAB BASES ----------
    with tab_bases:
        st.subheader("📖 Base general (en memoria)")

        texto_base_general = "\n".join(
            f"{p};{r}" for p, r in st.session_state.base_general
        )

        texto_base_general_edit = st.text_area(
            "Editar base general:",
            value=texto_base_general,
            height=250,
            key="admin_base_general",
        )

        if st.button(
            "💾 Guardar base general", key="btn_admin_guardar_base_general"
        ):
            nueva = []
            for linea in texto_base_general_edit.splitlines():
                if ";" not in linea:
                    continue
                p, r = linea.split(";", 1)
                nueva.append((p.strip(), r.strip()))
            if nueva:
                st.session_state.base_general = nueva
                st.success("Base general actualizada (en esta sesión).")
                st.rerun()
            else:
                st.error(
                    "No se detectaron líneas válidas (formato pregunta;respuesta)."
                )

        st.markdown("---")
        st.subheader("📘 Base específica por curso (en memoria)")

        cursos_base = sorted(st.session_state.bases_por_curso.keys())
        if cursos_base:
            curso_base_sel = st.selectbox(
                "Curso a editar",
                cursos_base,
                key="admin_select_curso_base",
            )
            lista_faq = st.session_state.bases_por_curso.get(
                curso_base_sel, []
            )
            texto_faq = "\n".join(f"{p};{r}" for p, r in lista_faq)

            texto_faq_edit = st.text_area(
                f"Editar base específica de {curso_base_sel}:",
                value=texto_faq,
                height=250,
                key="admin_texto_base_especifica",
            )

            if st.button(
                "💾 Guardar base específica del curso",
                key="btn_admin_guardar_base_curso",
            ):
                nueva_faq = []
                for linea in texto_faq_edit.splitlines():
                    if ";" not in linea:
                        continue
                    p, r = linea.split(";", 1)
                    nueva_faq.append((p.strip(), r.strip()))
                st.session_state.bases_por_curso[curso_base_sel] = nueva_faq
                st.success(
                    "Base específica actualizada (solo en esta sesión)."
                )
                st.rerun()
        else:
            st.info("No hay bases específicas cargadas en memoria.")
