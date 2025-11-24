import streamlit as st
import requests
import base64
import re
from datetime import datetime

# ============================================
# CONFIGURACIÓN DESDE SECRETS
# ============================================
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USER = st.secrets["GITHUB_USER"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_BASE_FOLDER = st.secrets.get("GITHUB_BASE_FOLDER", "MercedarIA_completo")

BASES_ROOT = f"{GITHUB_BASE_FOLDER}/bases"

# ============================================
# TEST DE CONEXIÓN A GITHUB (OPCIONAL)
# ============================================

def test_github_write():
    """Comprueba si el token realmente permite escribir en el repo."""
    test_path = f"{BASES_ROOT}/test_token.txt"
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{test_path}"

    contenido = "Prueba de conexión exitosa desde MercedarIA."

    # Primero obtengo el SHA del archivo (si existe)
    r_get = requests.get(url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    })

    sha = r_get.json().get("sha") if r_get.status_code == 200 else None

    data = {
        "message": "Test de escritura desde MercedarIA",
        "content": base64.b64encode(contenido.encode("utf-8")).decode("utf-8")
    }

    if sha:
        data["sha"] = sha

    r_put = requests.put(url, json=data, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    })

    if r_put.status_code in (200, 201):
        return True, "✔ TEST OK — Pude escribir en GitHub."
    else:
        return False, f"❌ ERROR {r_put.status_code}: {r_put.text}"

# Botón para probar la conexión
ok, msg = test_github_write()
st.warning("Resultado del test de GitHub:")
st.write(msg)

# ============================================
# BASES EN CÓDIGO (VALORES POR DEFECTO)
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

# ============================================
# FUNCIONES GITHUB
# ============================================

def github_raw_url(path_relativo: str) -> str:
    return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{path_relativo}"

def github_api_url(path_relativo: str) -> str:
    return f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path_relativo}"

def leer_archivo_github(path_relativo: str) -> str:
    try:
        r = requests.get(github_raw_url(path_relativo), timeout=10)
        if r.status_code == 200:
            return r.text
        return ""
    except:
        return ""

def escribir_archivo_github(path_relativo: str, contenido: str) -> (bool, str):
    url = github_api_url(path_relativo)
    try:
        r_get = requests.get(
            url,
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
            },
        )
        sha = r_get.json().get("sha") if r_get.status_code == 200 else None
    except:
        sha = None

    data = {
        "message": f"Actualizando {path_relativo} desde MercedarIA",
        "content": base64.b64encode(contenido.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        data["sha"] = sha

    try:
        r_put = requests.put(
            url,
            json=data,
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
            },
        )
        if r_put.status_code in (200, 201):
            return True, "✔ Guardado en GitHub."
        else:
            return False, f"❌ Error {r_put.status_code}: {r_put.text}"
    except Exception as e:
        return False, f"Error al guardar: {e}"

# ============================================
# HELPERS CURSO/MATERIA → ARCHIVO
# ============================================

def curso_to_id(curso: str) -> str:
    return curso.replace("°", "").replace(" ", "").strip() or "General"

def slugify_materia(materia: str) -> str:
    s = (materia or "").lower().strip()
    reemplazar = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}
    for o, d in reemplazar.items():
        s = s.replace(o, d)
    s = re.sub(r"[^a-z0-9]", "", s)
    return s or "general"

def archivo_base_curso_materia(curso: str, materia: str) -> str:
    cid = curso_to_id(curso)
    mid = slugify_materia(materia)
    return f"{BASES_ROOT}/{cid}_{mid}.txt"

# ============================================
# USERS / COURSES / TASKS / ANNOUNCEMENTS
# ============================================

# users.txt => email;nombre;apellido;rol;curso;password
def cargar_usuarios():
    texto = leer_archivo_github(f"{BASES_ROOT}/users.txt")
    usuarios = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        partes = linea.split(";", 5)
        if len(partes) != 6:
            continue
        email, nombre, apellido, rol, curso, password = partes
        usuarios.append(
            {
                "email": email.strip(),
                "nombre": nombre.strip(),
                "apellido": apellido.strip(),
                "rol": rol.strip(),
                "curso": curso.strip(),
                "password": password.strip(),
            }
        )
    return usuarios

def guardar_usuarios(lista):
    contenido = "\n".join(
        f"{u['email']};{u['nombre']};{u['apellido']};{u['rol']};{u['curso']};{u['password']}"
        for u in lista
    )
    return escribir_archivo_github(f"{BASES_ROOT}/users.txt", contenido)

# courses.txt => id;curso;materia;email_prof
def cargar_cursos():
    texto = leer_archivo_github(f"{BASES_ROOT}/courses.txt")
    cursos = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        partes = linea.split(";", 3)
        if len(partes) != 4:
            continue
        id_, curso, materia, email = partes
        cursos.append(
            {
                "id": id_.strip(),
                "curso": curso.strip(),
                "materia": materia.strip(),
                "email": email.strip(),
            }
        )
    return cursos

def guardar_cursos(lista):
    contenido = "\n".join(
        f"{c['id']};{c['curso']};{c['materia']};{c['email']}"
        for c in lista
    )
    return escribir_archivo_github(f"{BASES_ROOT}/courses.txt", contenido)

# tasks.txt => id;curso;materia;titulo;descripcion;creador;fecha_limite
def cargar_tareas():
    texto = leer_archivo_github(f"{BASES_ROOT}/tasks.txt")
    tareas = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        partes = linea.split(";", 6)
        if len(partes) != 7:
            continue
        id_, curso, materia, titulo, descr, creador, fecha = partes
        tareas.append(
            {
                "id": id_.strip(),
                "curso": curso.strip(),
                "materia": materia.strip(),
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
    return escribir_archivo_github(f"{BASES_ROOT}/tasks.txt", contenido)

# announcements.txt => id;curso;materia;titulo;contenido;creador;fecha_creacion
def cargar_anuncios():
    texto = leer_archivo_github(f"{BASES_ROOT}/announcements.txt")
    anuncios = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        partes = linea.split(";", 6)
        if len(partes) != 7:
            continue
        id_, curso, materia, titulo, contenido, creador, fecha = partes
        anuncios.append(
            {
                "id": id_.strip(),
                "curso": curso.strip(),
                "materia": materia.strip(),
                "titulo": titulo.strip(),
                "contenido": contenido.strip(),
                "creador": creador.strip(),
                "fecha": fecha.strip(),
            }
        )
    return anuncios

def guardar_anuncios(lista):
    contenido = "\n".join(
        f"{a['id']};{a['curso']};{a['materia']};{a['titulo']};"
        f"{a['contenido']};{a['creador']};{a['fecha']}"
        for a in lista
    )
    return escribir_archivo_github(f"{BASES_ROOT}/announcements.txt", contenido)

# ============================================
# CARGA INICIAL (ANTES DEL LOGIN)
# ============================================

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()
anuncios = cargar_anuncios()

# ============================================
# CONFIG STREAMLIT Y ESTADO
# ============================================

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")
st.title("🎓 MercedarIA - Asistente del Colegio INSM")

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "modo_anonimo" not in st.session_state:
    st.session_state.modo_anonimo = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# bases en estado (para que las pueda editar el admin en runtime)
if "base_general" not in st.session_state:
    st.session_state.base_general = BASE_GENERAL_DEFAULT.copy()

if "bases_especificas" not in st.session_state:
    st.session_state.bases_especificas = {
        k: v.copy() for k, v in BASES_ESPECIFICAS_DEFAULT.items()
    }

# ============================================
# LOGIN / CREAR CUENTA / MODO ANÓNIMO
# ============================================

if st.session_state.usuario is None and not st.session_state.modo_anonimo:
    st.subheader("🔐 Iniciar sesión (alumno / profe / admin)")

    col_login, col_reg, col_anon = st.columns([2, 2, 1])

    # ----- LOGIN -----
    with col_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_password")
        if st.button("Ingresar", key="btn_login"):
            usuarios = cargar_usuarios()
            user = next(
                (
                    u
                    for u in usuarios
                    if u["email"].lower() == email.lower()
                    and u["password"] == password
                ),
                None,
            )
            if user:
                st.session_state.usuario = user
                st.success(f"Bienvenido/a {user['nombre']} {user['apellido']} — Rol: {user['rol']}.")
                st.rerun()
            else:
                st.error("Email o contraseña incorrectos.")
                st.stop()

    # ----- REGISTRO ALUMNO -----
    with col_reg:
        st.markdown("### 🧾 Crear cuenta (solo alumnos)")
        new_email = st.text_input("Email nuevo", key="reg_email")
        new_nombre = st.text_input("Nombre", key="reg_nombre")
        new_apellido = st.text_input("Apellido", key="reg_apellido")
        new_curso = st.selectbox(
            "Curso",
            sorted(st.session_state.bases_especificas.keys()),
            key="reg_curso",
        )
        new_pw = st.text_input("Contraseña nueva", type="password", key="reg_pw")

        if st.button("Crear cuenta", key="btn_crear_cuenta"):
            usuarios = cargar_usuarios()
            if any(u["email"].lower() == new_email.lower() for u in usuarios):
                st.error("Ya existe un usuario con ese email.")
            else:
                usuarios.append(
                    {
                        "email": new_email,
                        "nombre": new_nombre,
                        "apellido": new_apellido,
                        "rol": "alumno",
                        "curso": new_curso,
                        "password": new_pw,
                    }
                )
                guardar_usuarios(usuarios)
                st.success("Cuenta creada. Ya podés iniciar sesión.")
                st.stop()

    # ----- MODO ANÓNIMO -----
    with col_anon:
        st.markdown("### 👤 Modo anónimo")
        if st.button("Entrar como invitado", key="btn_modo_anonimo"):
            st.session_state.modo_anonimo = True
            st.session_state.usuario = None
            st.session_state.chat_history = []
            st.rerun()

# Si está en modo anónimo: crear usuario ficticio
if st.session_state.modo_anonimo:
    usuario = {
        "nombre": "Invitado",
        "apellido": "",
        "rol": "anonimo",
        "email": "anonimo@insm.edu",
        "curso": "General",
    }
else:
    usuario = st.session_state.get("usuario", None)

if usuario is None:
    st.warning("Por favor, iniciá sesión o entrá en modo anónimo para continuar.")
    st.stop()

rol = usuario["rol"]
email_usuario = usuario["email"]
curso_usuario = usuario["curso"]

# recargar por si hubo cambios
usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()
anuncios = cargar_anuncios()

col_info, col_logout = st.columns([4, 1])
with col_info:
    if rol != "anonimo":
        st.info(
            f"Conectado como **{usuario['nombre']} {usuario['apellido']}** — "
            f"Rol: **{rol}** — Curso: **{curso_usuario}**"
        )
    else:
        st.info("Conectado en **modo anónimo** (solo base general).")
with col_logout:
    if st.button("Cerrar sesión / salir", key="btn_logout"):
        st.session_state.usuario = None
        st.session_state.modo_anonimo = False
        st.session_state.chat_history = []
        st.rerun()

# ============================================
# FUNCIÓN DE DEEPSEEK
# ============================================

def consultar_deepseek(pregunta, contexto_txt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": contexto_txt},
            {"role": "user", "content": pregunta},
        ],
        "max_tokens": 600,
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=18)
        r.raise_for_status()
        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return "Error interpretando la respuesta."
    except Exception as e:
        return f"Error al consultar DeepSeek: {e}"

# ============================================
# FUNCIÓN PARA ARMAR CONTEXTO COMPLETO
# ============================================

def construir_contexto_completo(usuario_actual, usuarios, cursos, tareas, anuncios):
    """
    Construye el contexto para DeepSeek.
    - En modo anónimo: solo base general.
    - En alumnos/profes/admin: usa users, courses, base general, base específica
      y SOLO tareas/anuncios del curso del usuario.
    """

    # MODO ANÓNIMO: solo base general
    if usuario_actual["rol"] == "anonimo":
        contexto = (
            "Sos MercedarIA, asistente del Colegio Mercedaria. "
            "Estás respondiendo en **modo anónimo**. "
            "Solo podés usar la base general del colegio y no debés inventar datos personales.\n\n"
        )
        contexto += "BASE GENERAL DEL COLEGIO:\n\n"
        for p, r in st.session_state.base_general:
            contexto += f"{p} -> {r}\n"
        return contexto

    curso_usuario = usuario_actual["curso"]

    contexto = (
        "Sos MercedarIA, asistente virtual del Colegio Mercedaria. "
        "Siempre respondés con información confiable y, cuando se trate de datos "
        "de cursos, SOLO usás información del curso actual del usuario. "
        "Si preguntan por otros cursos, aclará que solo podés responder sobre su curso.\n\n"
    )

    contexto += "INFORMACIÓN DEL USUARIO LOGUEADO:\n"
    contexto += f"Nombre: {usuario_actual['nombre']} {usuario_actual['apellido']}.\n"
    contexto += f"Rol: {usuario_actual['rol']}.\n"
    contexto += f"Email: {usuario_actual['email']}.\n"
    contexto += f"Curso: {curso_usuario}.\n\n"

    contexto += "BASE GENERAL DEL COLEGIO:\n\n"
    for p, r in st.session_state.base_general:
        contexto += f"{p} -> {r}\n"

    contexto += "\nBASE DEL CURSO DEL USUARIO (FAQ):\n"
    faqs = st.session_state.bases_especificas.get(curso_usuario, [])
    for p, r in faqs:
        contexto += f"{p} -> {r}\n"

    contexto += "\nBASE DE USUARIOS (solo para saber roles y cursos):\n"
    for u in usuarios:
        contexto += (
            f"Usuario: {u['nombre']} {u['apellido']} "
            f"({u['email']}), rol: {u['rol']}, curso: {u['curso']}.\n"
        )

    contexto += "\nBASE DE CURSOS Y PROFESORES:\n"
    for c in cursos:
        prof = next((u for u in usuarios if u["email"] == c["email"]), None)
        if prof:
            contexto += (
                f"En el curso {c['curso']}, la materia {c['materia']} "
                f"la dicta {prof['nombre']} {prof['apellido']} ({prof['email']}).\n"
            )
        else:
            contexto += (
                f"En el curso {c['curso']}, la materia {c['materia']} "
                f"la dicta el profesor con email {c['email']}.\n"
            )

    contexto += "\nTAREAS DEL CURSO DEL USUARIO:\n"
    for t in tareas:
        if t["curso"] == curso_usuario:
            contexto += (
                f"En el curso {t['curso']} hay una tarea de {t['materia']} "
                f"titulada '{t['titulo']}' con descripción '{t['descripcion']}' "
                f"y fecha límite {t['fecha_limite']}.\n"
            )

    contexto += "\nANUNCIOS DEL CURSO DEL USUARIO:\n"
    for a in anuncios:
        if a["curso"] == curso_usuario:
            contexto += (
                f"Anuncio en el curso {a['curso']} de la materia {a['materia']}: "
                f"'{a['titulo']}' — {a['contenido']} (creado el {a['fecha']}).\n"
            )

    return contexto

# ============================================
# CHAT CON HISTORIAL ESTILO BURBUJA
# ============================================

st.subheader("💬 Chat con MercedarIA")

col_input, col_btn = st.columns([4, 1])
with col_input:
    pregunta = st.text_input("Escribí tu pregunta:", key="campo_pregunta")
with col_btn:
    enviar = st.button("Enviar", key="btn_enviar_chat")

if enviar and pregunta.strip():
    contexto = construir_contexto_completo(usuario, usuarios, cursos, tareas, anuncios)
    respuesta = consultar_deepseek(pregunta, contexto)

    st.session_state.chat_history.append(
        {"role": "user", "content": pregunta.strip()}
    )
    st.session_state.chat_history.append(
        {"role": "assistant", "content": respuesta}
    )

st.markdown("### 🗨️ Historial de conversación")

for mensaje in st.session_state.chat_history:
    if mensaje["role"] == "user":
        st.markdown(
            f"""
<div style="text-align: right; margin: 4px 0;">
  <div style="
      display: inline-block;
      background-color: #D8F5C8;
      color: #111;
      padding: 8px 12px;
      border-radius: 12px;
      max-width: 80%;
  ">
    <b>Vos:</b> {mensaje["content"]}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
<div style="text-align: left; margin: 4px 0;">
  <div style="
      display: inline-block;
      background-color: #F0F0F0;
      color: #111;
      padding: 8px 12px;
      border-radius: 12px;
      max-width: 80%;
  ">
    <b>MercedarIA:</b> {mensaje["content"]}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown("---")

# ============================================
# PANEL DE TAREAS Y ANUNCIOS
# ============================================

if rol != "anonimo":
    st.header("📝 Tareas y 📢 Anuncios")

    with st.expander("Ver tareas y anuncios", expanded=False):
        # Alumno: ve tareas y anuncios de su curso
        if rol == "alumno":
            st.subheader("Tareas de tu curso")
            tareas_del_curso = [t for t in tareas if t["curso"] == curso_usuario]
            if not tareas_del_curso:
                st.write("No hay tareas cargadas para tu curso.")
            else:
                for t in tareas_del_curso:
                    st.markdown(
                        f"""
**{t['titulo']}**  
📚 **Materia:** {t['materia']}  
📌 *{t['descripcion']}*  
⏳ **Vence:** {t['fecha_limite']}  
👨‍🏫 **Profesor:** {t['creador']}  
---
"""
                    )

            st.subheader("Anuncios de tu curso")
            anuncios_del_curso = [a for a in anuncios if a["curso"] == curso_usuario]
            if not anuncios_del_curso:
                st.write("No hay anuncios para tu curso.")
            else:
                for a in anuncios_del_curso:
                    st.markdown(
                        f"""
**{a['titulo']}**  
📚 **Materia:** {a['materia']}  
🗓️ **Fecha:** {a['fecha']}  
📌 {a['contenido']}  
👨‍🏫 **Profesor:** {a['creador']}  
---
"""
                    )

        # Profesor: CRUD solo en sus materias
        if rol == "profe":
            st.subheader("Tus tareas por materia y curso")

            # Materias asignadas a este profesor
            materias_mias = [c for c in cursos if c["email"] == email_usuario]

            if not materias_mias:
                st.info("No tenés materias asignadas en courses.txt.")
            else:
                # Crear nueva tarea
                st.markdown("#### ➕ Crear nueva tarea")

                opcion_curso_materia = st.selectbox(
                    "Elegí curso y materia",
                    [f"{c['curso']} — {c['materia']}" for c in materias_mias],
                    key="select_curso_materia_tarea",
                )

                curso_sel, materia_sel = opcion_curso_materia.split(" — ", 1)

                titulo = st.text_input("Título de la tarea", key="nuevo_titulo_tarea")
                descr = st.text_area("Descripción", key="nuevo_descr_tarea")
                fecha = st.date_input("Fecha límite", key="nuevo_fecha_tarea")

                if st.button("Agregar tarea", key="btn_agregar_tarea"):
                    if titulo.strip() == "":
                        st.warning("Tenés que poner un título.")
                    else:
                        nuevo_id = (
                            str(max([int(t["id"]) for t in tareas] + [0]) + 1)
                            if tareas
                            else "1"
                        )
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
                st.markdown("#### ✏️ Editar / borrar tus propias tareas")

                # El profe solo puede editar/borrar las que creó él
                mis_tareas = [t for t in tareas if t["creador"] == email_usuario]

                if not mis_tareas:
                    st.write("Todavía no creaste tareas.")
                else:
                    for t in mis_tareas:
                        with st.expander(
                            f"{t['curso']} — {t['materia']} — {t['titulo']}",
                            expanded=False,
                        ):
                            nuevo_titulo = st.text_input(
                                "Título",
                                value=t["titulo"],
                                key=f"edit_titulo_{t['id']}",
                            )
                            nuevo_descr = st.text_area(
                                "Descripción",
                                value=t["descripcion"],
                                key=f"edit_descr_{t['id']}",
                            )
                            nuevo_fecha = st.text_input(
                                "Fecha límite (YYYY-MM-DD)",
                                value=t["fecha_limite"],
                                key=f"edit_fecha_{t['id']}",
                            )

                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                if st.button(
                                    "💾 Guardar cambios",
                                    key=f"btn_guardar_tarea_{t['id']}",
                                ):
                                    t["titulo"] = nuevo_titulo.strip()
                                    t["descripcion"] = nuevo_descr.strip()
                                    t["fecha_limite"] = nuevo_fecha.strip()
                                    guardar_tareas(tareas)
                                    st.success("Tarea actualizada.")
                                    st.rerun()
                            with col_e2:
                                if st.button(
                                    "🗑 Eliminar tarea",
                                    key=f"btn_borrar_tarea_{t['id']}",
                                ):
                                    tareas = [x for x in tareas if x["id"] != t["id"]]
                                    guardar_tareas(tareas)
                                    st.success("Tarea eliminada.")
                                    st.rerun()

                # ----- ANUNCIOS DEL PROFESOR -----
                st.markdown("---")
                st.markdown("#### 📢 Crear nuevo anuncio")

                opcion_curso_materia_anun = st.selectbox(
                    "Elegí curso y materia para el anuncio",
                    [f"{c['curso']} — {c['materia']}" for c in materias_mias],
                    key="select_curso_materia_anuncio",
                )

                curso_anun, materia_anun = opcion_curso_materia_anun.split(" — ", 1)

                titulo_anun = st.text_input("Título del anuncio", key="nuevo_titulo_anuncio")
                contenido_anun = st.text_area("Contenido del anuncio", key="nuevo_contenido_anuncio")

                if st.button("Agregar anuncio", key="btn_agregar_anuncio"):
                    if titulo_anun.strip() == "" or contenido_anun.strip() == "":
                        st.warning("Completá el título y el contenido del anuncio.")
                    else:
                        nuevo_id = (
                            str(max([int(a["id"]) for a in anuncios] + [0]) + 1)
                            if anuncios
                            else "1"
                        )
                        fecha_hoy = datetime.now().date().isoformat()
                        nuevo_anuncio = {
                            "id": nuevo_id,
                            "curso": curso_anun,
                            "materia": materia_anun,
                            "titulo": titulo_anun.strip(),
                            "contenido": contenido_anun.strip(),
                            "creador": email_usuario,
                            "fecha": fecha_hoy,
                        }
                        anuncios.append(nuevo_anuncio)
                        guardar_anuncios(anuncios)
                        st.success("Anuncio agregado correctamente.")
                        st.rerun()

                st.markdown("#### ✏️ Editar / borrar tus anuncios")

                mis_anuncios = [a for a in anuncios if a["creador"] == email_usuario]

                if not mis_anuncios:
                    st.write("Todavía no creaste anuncios.")
                else:
                    for a in mis_anuncios:
                        with st.expander(
                            f"{a['curso']} — {a['materia']} — {a['titulo']}",
                            expanded=False,
                        ):
                            nuevo_titulo_a = st.text_input(
                                "Título",
                                value=a["titulo"],
                                key=f"edit_titulo_anun_{a['id']}",
                            )
                            nuevo_contenido_a = st.text_area(
                                "Contenido",
                                value=a["contenido"],
                                key=f"edit_contenido_anun_{a['id']}",
                            )
                            nueva_fecha_a = st.text_input(
                                "Fecha (YYYY-MM-DD)",
                                value=a["fecha"],
                                key=f"edit_fecha_anun_{a['id']}",
                            )

                            col_a1, col_a2 = st.columns(2)
                            with col_a1:
                                if st.button(
                                    "💾 Guardar cambios anuncio",
                                    key=f"btn_guardar_anuncio_{a['id']}",
                                ):
                                    a["titulo"] = nuevo_titulo_a.strip()
                                    a["contenido"] = nuevo_contenido_a.strip()
                                    a["fecha"] = nueva_fecha_a.strip()
                                    guardar_anuncios(anuncios)
                                    st.success("Anuncio actualizado.")
                                    st.rerun()
                            with col_a2:
                                if st.button(
                                    "🗑 Eliminar anuncio",
                                    key=f"btn_borrar_anuncio_{a['id']}",
                                ):
                                    anuncios = [x for x in anuncios if x["id"] != a["id"]]
                                    guardar_anuncios(anuncios)
                                    st.success("Anuncio eliminado.")
                                    st.rerun()

        # Admin: puede ver todas las tareas/anuncios
        if rol == "admin":
            st.subheader("Todas las tareas (modo admin)")
            if not tareas:
                st.write("No hay tareas cargadas.")
            else:
                for t in tareas:
                    st.markdown(
                        f"""
**[{t['id']}] {t['titulo']}**  
🏫 **Curso:** {t['curso']} — 📚 **Materia:** {t['materia']}  
📌 *{t['descripcion']}*  
⏳ **Vence:** {t['fecha_limite']}  
👨‍🏫 **Creador:** {t['creador']}  
---
"""
                    )

            st.subheader("Todos los anuncios (modo admin)")
            if not anuncios:
                st.write("No hay anuncios cargados.")
            else:
                for a in anuncios:
                    st.markdown(
                        f"""
**[{a['id']}] {a['titulo']}**  
🏫 **Curso:** {a['curso']} — 📚 **Materia:** {a['materia']}  
🗓️ **Fecha:** {a['fecha']}  
📌 {a['contenido']}  
👨‍🏫 **Creador:** {a['creador']}  
---
"""
                    )

# ============================================
# PANEL DEL PROFESOR (BASES POR MATERIA)
# ============================================

if rol == "profe":
    st.header("🧑‍🏫 Panel del Profesor — Bases por materia")

    materias_mias = [c for c in cursos if c["email"] == email_usuario]

    if not materias_mias:
        st.info("No tenés materias asignadas en courses.txt.")
    else:
        materia_sel = st.selectbox(
            "Materia a editar:",
            [f"{c['curso']} — {c['materia']}" for c in materias_mias],
            key="select_materia_prof",
        )

        curso_edit, materia_edit = materia_sel.split(" — ", 1)

        path = archivo_base_curso_materia(curso_edit, materia_edit)
        contenido_actual = leer_archivo_github(path)

        nuevo = st.text_area(
            "Contenido editable del archivo (por ejemplo, pregunta;respuesta por línea, o info libre):",
            value=contenido_actual,
            height=300,
            key="textarea_base_materia",
        )

        if st.button("💾 Guardar cambios en esta materia", key="btn_guardar_materia"):
            escribir_archivo_github(path, nuevo)
            st.success("Cambios guardados.")

# ============================================
# PANEL DEL ADMIN
# ============================================

if rol == "admin":
    st.header("⚙️ Panel de Administración")

    tab_usuarios, tab_cursos, tab_bases = st.tabs(
        ["Usuarios", "Cursos y materias", "Bases de conocimiento"]
    )

    # ----- USUARIOS -----
    with tab_usuarios:
        st.subheader("Usuarios existentes")
        for u in usuarios:
            st.markdown(
                f"- **{u['email']}** — rol: {u['rol']} — curso: {u['curso']}"
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
                if st.button("💾 Guardar cambios usuario", key="btn_admin_guardar_user"):
                    user_sel["nombre"] = nom_edit.strip()
                    user_sel["apellido"] = ape_edit.strip()
                    user_sel["rol"] = rol_edit.strip()
                    user_sel["curso"] = curso_edit.strip()
                    user_sel["password"] = pw_edit.strip()
                    guardar_usuarios(usuarios)
                    st.success("Usuario actualizado.")
                    st.rerun()
            with col_u2:
                if st.button("🗑 Eliminar usuario", key="btn_admin_borrar_user"):
                    usuarios = [u for u in usuarios if u["email"] != email_sel]
                    guardar_usuarios(usuarios)
                    st.success("Usuario eliminado.")
                    st.rerun()

    # ----- CURSOS Y MATERIAS -----
    with tab_cursos:
        st.subheader("Cursos existentes (courses.txt)")

        for c_obj in cursos:
            st.markdown(
                f"- **[{c_obj['id']}] {c_obj['curso']} — {c_obj['materia']}** "
                f"(prof: {c_obj['email']})"
            )

        st.markdown("---")
        st.subheader("Modificar / eliminar curso/materia existente")

        if cursos:
            curso_sel_admin = st.selectbox(
                "Elegí un curso/materia",
                [f"[{c['id']}] {c['curso']} — {c['materia']}" for c in cursos],
                key="admin_select_curso_edit",
            )
            id_sel = curso_sel_admin.split("]", 1)[0][1:]
            curso_obj = next(c for c in cursos if c["id"] == id_sel)

            curso_n = st.text_input(
                "Curso (ej: 1° B)",
                value=curso_obj["curso"],
                key="admin_curso_nombre_edit",
            )
            materia_n = st.text_input(
                "Materia (ej: Matemática)",
                value=curso_obj["materia"],
                key="admin_materia_nombre_edit",
            )
            prof_n = st.text_input(
                "Email del profesor",
                value=curso_obj["email"],
                key="admin_prof_email_edit",
            )

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("💾 Guardar cambios curso/materia", key="btn_admin_guardar_curso"):
                    curso_obj["curso"] = curso_n.strip()
                    curso_obj["materia"] = materia_n.strip()
                    curso_obj["email"] = prof_n.strip()
                    guardar_cursos(cursos)
                    st.success("Curso/materia actualizado.")
                    st.rerun()
            with col_c2:
                if st.button("🗑 Eliminar curso/materia", key="btn_admin_borrar_curso"):
                    cursos = [c for c in cursos if c["id"] != id_sel]
                    guardar_cursos(cursos)
                    st.success("Curso/materia eliminado.")
                    st.rerun()

        st.markdown("---")
        st.subheader("Agregar curso/materia nuevo")

        idc = st.text_input("ID del curso (número)", key="admin_id_curso_nuevo")
        curso_n2 = st.text_input("Curso (ej: 1° A)", key="admin_curso_nombre_nuevo")
        materia_n2 = st.text_input("Materia (ej: Matemática)", key="admin_materia_nombre_nuevo")
        prof_n2 = st.text_input("Email del profesor", key="admin_prof_email_nuevo")

        if st.button("Crear materia nueva", key="btn_admin_crear_materia"):
            cursos.append(
                {
                    "id": idc.strip(),
                    "curso": curso_n2.strip(),
                    "materia": materia_n2.strip(),
                    "email": prof_n2.strip(),
                }
            )
            guardar_cursos(cursos)
            st.success("Materia agregada.")
            st.rerun()

    # ----- BASES DE CONOCIMIENTO -----
    with tab_bases:
        st.subheader("Base general (pregunta;respuesta por línea)")

        texto_base_general = "\n".join(
            f"{p};{r}" for p, r in st.session_state.base_general
        )

        texto_base_general_edit = st.text_area(
            "Editar base general:",
            value=texto_base_general,
            height=250,
            key="admin_base_general",
        )

        if st.button("💾 Guardar base general", key="btn_admin_guardar_base_general"):
            nueva = []
            for linea in texto_base_general_edit.splitlines():
                if ";" not in linea:
                    continue
                p, r = linea.split(";", 1)
                nueva.append((p.strip(), r.strip()))
            if nueva:
                st.session_state.base_general = nueva
                st.success("Base general actualizada (se mantiene en esta sesión; podés luego volcarla a un archivo si querés).")
            else:
                st.error("No se detectaron líneas válidas (pregunta;respuesta).")

        st.markdown("---")
        st.subheader("Base específica por curso")

        cursos_base = sorted(st.session_state.bases_especificas.keys())
        if cursos_base:
            curso_base_sel = st.selectbox(
                "Curso a editar",
                cursos_base,
                key="admin_select_curso_base",
            )
            lista_faq = st.session_state.bases_especificas.get(curso_base_sel, [])
            texto_faq = "\n".join(f"{p};{r}" for p, r in lista_faq)

            texto_faq_edit = st.text_area(
                f"Editar base específica de {curso_base_sel}:",
                value=texto_faq,
                height=250,
                key="admin_texto_base_especifica",
            )

            if st.button(
                "💾 Guardar base específica del curso", key="btn_admin_guardar_base_curso"
            ):
                nueva_faq = []
                for linea in texto_faq_edit.splitlines():
                    if ";" not in linea:
                        continue
                    p, r = linea.split(";", 1)
                    nueva_faq.append((p.strip(), r.strip()))
                st.session_state.bases_especificas[curso_base_sel] = nueva_faq
                st.success("Base específica actualizada (solo en esta sesión).")
        else:
            st.info("No hay bases específicas cargadas.")
