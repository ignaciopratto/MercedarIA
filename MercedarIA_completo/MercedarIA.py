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
# BASES EN CÓDIGO
# ============================================

BASE_GENERAL = [
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

BASES_ESPECIFICAS = {
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
        r_get = requests.get(url, headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        })
        sha = r_get.json().get("sha") if r_get.status_code == 200 else None
    except:
        sha = None

    data = {
        "message": f"Actualizando {path_relativo} desde MercedarIA",
        "content": base64.b64encode(contenido.encode("utf-8")).decode("utf-8")
    }
    if sha:
        data["sha"] = sha

    try:
        r_put = requests.put(url, json=data, headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        })
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
# USERS / COURSES / TASKS
# ============================================

def cargar_usuarios():
    texto = leer_archivo_github(f"{BASES_ROOT}/users.txt")
    usuarios = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        email, nombre, apellido, rol, curso, password = linea.split(";", 5)
        usuarios.append({
            "email": email.strip(),
            "nombre": nombre.strip(),
            "apellido": apellido.strip(),
            "rol": rol.strip(),
            "curso": curso.strip(),
            "password": password.strip()
        })
    return usuarios

def guardar_usuarios(lista):
    contenido = "\n".join(
        f"{u['email']};{u['nombre']};{u['apellido']};{u['rol']};{u['curso']};{u['password']}"
        for u in lista
    )
    return escribir_archivo_github(f"{BASES_ROOT}/users.txt", contenido)

def cargar_cursos():
    texto = leer_archivo_github(f"{BASES_ROOT}/courses.txt")
    cursos = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        id_, curso, materia, email = linea.split(";", 3)
        cursos.append({
            "id": id_.strip(),
            "curso": curso.strip(),
            "materia": materia.strip(),
            "email": email.strip()
        })
    return cursos

def guardar_cursos(lista):
    contenido = "\n".join(
        f"{c['id']};{c['curso']};{c['materia']};{c['email']}"
        for c in lista
    )
    return escribir_archivo_github(f"{BASES_ROOT}/courses.txt", contenido)

def cargar_tareas():
    texto = leer_archivo_github(f"{BASES_ROOT}/tasks.txt")
    tareas = []
    for linea in texto.splitlines():
        if ";" not in linea:
            continue
        id_, titulo, descr, curso, creador, fecha = linea.split(";", 5)
        tareas.append({
            "id": id_.strip(),
            "titulo": titulo.strip(),
            "descripcion": descr.strip(),
            "curso": curso.strip(),
            "creador": creador.strip(),
            "fecha_limite": fecha.strip()
        })
    return tareas

def guardar_tareas(lista):
    contenido = "\n".join(
        f"{t['id']};{t['titulo']};{t['descripcion']};{t['curso']};{t['creador']};{t['fecha_limite']}"
        for t in lista
    )
    return escribir_archivo_github(f"{BASES_ROOT}/tasks.txt", contenido)

def agregar_tarea_a_bases_de_curso(curso, tarea, cursos):
    """
    Agrega la tarea como línea en cada base de materia del curso.
    """
    for c in cursos:
        if c["curso"].strip() == curso.strip():
            path = archivo_base_curso_materia(c["curso"], c["materia"])
            texto = leer_archivo_github(path)

            lineas = [l for l in texto.splitlines() if l.strip() != ""]
            linea_tarea = f"TAREA: {tarea['titulo']};{tarea['descripcion']};{tarea['fecha_limite']}"
            lineas.append(linea_tarea)

            nuevo = "\n".join(lineas)
            escribir_archivo_github(path, nuevo)

# ============================================
# CARGA INICIAL (ANTES DEL LOGIN)
# ============================================

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

# ============================================
# CONFIG STREAMLIT Y LOGIN
# ============================================

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")
st.title("🎓 MercedarIA - Asistente del Colegio INSM")

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.session_state.usuario is None:
    st.subheader("🔐 Iniciar sesión")

    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        usuarios = cargar_usuarios()
        user = next(
            (u for u in usuarios
             if u["email"].lower() == email.lower() and u["password"] == password),
            None
        )
        if user:
            st.session_state.usuario = user
            st.success(f"Bienvenido/a {user['nombre']} {user['apellido']}.")
            st.rerun()
        else:
            st.error("Email o contraseña incorrectos.")
            st.stop()

# ============================================
# USUARIO LOGUEADO
# ============================================

usuario = st.session_state.get("usuario", None)
if usuario is None:
    st.warning("Por favor, iniciá sesión para continuar.")
    st.stop()

rol = usuario["rol"]
email_usuario = usuario["email"]
curso_usuario = usuario["curso"]

# recargar por si hubo cambios
usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

st.info(
    f"Conectado como **{usuario['nombre']} {usuario['apellido']}** — "
    f"Rol: **{rol}** — Curso: **{curso_usuario}**"
)

# ============================================
# FUNCIÓN DE DEEPSEEK
# ============================================

def consultar_deepseek(pregunta, contexto_txt):
    """
    Envía la pregunta + contexto a la API de DeepSeek.
    """
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY"}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": contexto_txt},
            {"role": "user", "content": pregunta}
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

def construir_contexto_completo(curso_usuario):
    contexto = "INFORMACIÓN DEL USUARIO LOGUEADO:\n"
    contexto += f"El usuario actual pertenece al curso {curso_usuario}.\n"
    contexto += f"Nombre: {usuario['nombre']} {usuario['apellido']}.\n"
    contexto += f"Rol: {usuario['rol']}.\n"
    contexto += f"Email: {usuario['email']}.\n\n"

    contexto += "BASE DEL COLEGIO:\n\n"

    # General
    for p, r in BASE_GENERAL:
        contexto += f"{p} -> {r}\n"

    # Info específica del curso (preguntas fijas)
    contexto += "\nBASE DEL CURSO:\n"
    faqs = BASES_ESPECIFICAS.get(curso_usuario, [])
    for p, r in faqs:
        contexto += f"{p} -> {r}\n"

    # Usuarios (sobre todo profes y cursos)
    contexto += "\nBASE DE USUARIOS (roles, cursos, mails):\n"
    for u in usuarios:
        contexto += (
            f"Usuario: {u['nombre']} {u['apellido']} "
            f"({u['email']}), rol: {u['rol']}, curso: {u['curso']}.\n"
        )

    # Cursos y materias con profesor asignado
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

    # Bases por materia según TXT
    contexto += "\nBASE DE MATERIAS (faq + tareas guardadas en txt):\n"
    for c in cursos:
        if c["curso"] == curso_usuario:
            path = archivo_base_curso_materia(c["curso"], c["materia"])
            texto = leer_archivo_github(path)
            if texto.strip():
                contexto += f"\n[{c['materia']}]\n{texto}\n"

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
    contexto = construir_contexto_completo(curso_usuario)
    respuesta = consultar_deepseek(pregunta, contexto)

    # Guardar en historial
    st.session_state.chat_history.append({"role": "user", "content": pregunta.strip()})
    st.session_state.chat_history.append({"role": "assistant", "content": respuesta})

st.markdown("### 🗨️ Historial de conversación")

for mensaje in st.session_state.chat_history:
    if mensaje["role"] == "user":
        # Burbuja del usuario (verde suave)
        st.markdown(
            f"""
<div style="text-align: right; margin: 4px 0;">
  <div style="
      display: inline-block;
      background-color: #CFE8C0;
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
        # Burbuja de MercedarIA (gris suave)
        st.markdown(
            f"""
<div style="text-align: left; margin: 4px 0;">
  <div style="
      display: inline-block;
      background-color: #E0E0E0;
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
# PANEL DE TAREAS (CON EXPANDER)
# ============================================

st.header("📝 Tareas")

with st.expander("Ver tareas del curso", expanded=False):
    st.subheader("Tareas del curso")

    tareas_del_curso = [t for t in tareas if t["curso"] == curso_usuario]

    if not tareas_del_curso:
        st.write("No hay tareas cargadas para tu curso.")
    else:
        for t in tareas_del_curso:
            st.markdown(
                f"""
**{t['titulo']}**  
📌 *{t['descripcion']}*  
⏳ **Vence:** {t['fecha_limite']}  
👨‍🏫 **Profesor:** {t['creador']}  
---
"""
            )

    # Profes pueden crear tareas
    if rol == "profe":
        st.subheader("➕ Crear nueva tarea")

        titulo = st.text_input("Título de la tarea", key="nuevo_titulo")
        descr = st.text_area("Descripción", key="nuevo_descr")
        fecha = st.date_input("Fecha límite", key="nuevo_fecha")

        if st.button("Agregar tarea", key="btn_agregar_tarea"):
            if titulo.strip() == "":
                st.warning("Tenés que poner un título.")
            else:
                nuevo_id = str(len(tareas) + 1)
                nueva = {
                    "id": nuevo_id,
                    "titulo": titulo,
                    "descripcion": descr,
                    "curso": curso_usuario,
                    "creador": email_usuario,
                    "fecha_limite": str(fecha)
                }

                tareas.append(nueva)
                # Guarda TODAS las tareas en tasks.txt del repo
                guardar_tareas(tareas)
                # Y también la mete en los txt por materia del curso
                agregar_tarea_a_bases_de_curso(curso_usuario, nueva, cursos)

                st.success("Tarea agregada correctamente.")
                st.rerun()

# ============================================
# PANEL DEL PROFESOR (EDITAR BASES)
# ============================================

if rol == "profe":
    st.header("🧑‍🏫 Panel del Profesor")

    materias_mias = [c for c in cursos if c["email"] == email_usuario]

    if not materias_mias:
        st.info("No tenés materias asignadas.")
    else:
        materia_sel = st.selectbox(
            "Materia a editar:",
            [f"{c['curso']} — {c['materia']}" for c in materias_mias],
            key="select_materia_prof"
        )

        curso_edit = materia_sel.split(" — ")[0]
        materia_edit = materia_sel.split(" — ")[1]

        path = archivo_base_curso_materia(curso_edit, materia_edit)
        contenido_actual = leer_archivo_github(path)

        nuevo = st.text_area(
            "Contenido editable del archivo:",
            value=contenido_actual,
            height=400,
            key="textarea_base_materia"
        )

        if st.button("💾 Guardar cambios en esta materia", key="btn_guardar_materia"):
            escribir_archivo_github(path, nuevo)
            st.success("Cambios guardados.")

# ============================================
# PANEL DEL ADMIN
# ============================================

if rol == "admin":
    st.header("⚙️ Panel de Administración")

    st.subheader("Usuarios existentes")
    for u in usuarios:
        st.markdown(f"- **{u['email']}** — {u['rol']} — {u['curso']}")

    st.subheader("Crear nuevo usuario")

    em = st.text_input("Email nuevo", key="admin_email_nuevo")
    nom = st.text_input("Nombre", key="admin_nombre_nuevo")
    ape = st.text_input("Apellido", key="admin_apellido_nuevo")
    r = st.selectbox("Rol", ["alumno", "profe", "admin"], key="admin_rol_nuevo")
    c = st.text_input("Curso (solo alumnos)", key="admin_curso_nuevo")
    pw = st.text_input("Contraseña", key="admin_pw_nuevo")

    if st.button("Crear usuario", key="btn_admin_crear_usuario"):
        usuarios.append({
            "email": em,
            "nombre": nom,
            "apellido": ape,
            "rol": r,
            "curso": c,
            "password": pw
        })
        guardar_usuarios(usuarios)
        st.success("Usuario creado.")
        st.rerun()

    st.subheader("Cursos existentes")
    for c_obj in cursos:
        st.markdown(f"- **{c_obj['curso']} — {c_obj['materia']}** (prof: {c_obj['email']})")

    st.subheader("Agregar curso/materia")

    idc = st.text_input("ID del curso", key="admin_id_curso")
    curso_n = st.text_input("Curso (ej: 1° A)", key="admin_curso_nombre")
    materia_n = st.text_input("Materia (ej: Matemática)", key="admin_materia_nombre")
    prof_n = st.text_input("Email del profesor", key="admin_prof_email")

    if st.button("Crear materia nueva", key="btn_admin_crear_materia"):
        cursos.append({
            "id": idc,
            "curso": curso_n,
            "materia": materia_n,
            "email": prof_n
        })
        guardar_cursos(cursos)
        st.success("Materia agregada.")
        st.rerun()

