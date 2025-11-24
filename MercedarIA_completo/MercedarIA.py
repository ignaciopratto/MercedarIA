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

BASES_ROOT = f"{GITHUB_BASE_FOLDER}"

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

def escribir_archivo_github(path_relativo: str, contenido: str):
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
        "message": f"Actualizando {path_relativo}",
        "content": base64.b64encode(contenido.encode("utf-8")).decode("utf-8")
    }
    if sha:
        data["sha"] = sha

    r_put = requests.put(
        url,
        json=data,
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }
    )
    return r_put.status_code in (200, 201)

# ============================================
# USERS / COURSES / TASKS
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
        usuarios.append({
            "email": email.strip(),
            "nombre": nombre.strip(),
            "apellido": apellido.strip(),
            "rol": rol.strip(),
            "curso": curso.strip(),
            "password": password.strip(),
        })
    return usuarios

def guardar_usuarios(lista):
    contenido = "\n".join(
        f"{u['email']};{u['nombre']};{u['apellido']};{u['rol']};{u['curso']};{u['password']}"
        for u in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/users.txt", contenido)

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
        cursos.append({
            "id": id_.strip(),
            "curso": curso.strip(),
            "materia": materia.strip(),
            "email": email.strip(),
        })
    return cursos

def guardar_cursos(lista):
    contenido = "\n".join(
        f"{c['id']};{c['curso']};{c['materia']};{c['email']}"
        for c in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/courses.txt", contenido)

# tasks.txt (NUEVO FORMATO):
# id;curso;materia;titulo;descripcion;creador;fecha_limite
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
        tareas.append({
            "id": id_.strip(),
            "curso": curso.strip(),
            "materia": materia.strip(),
            "titulo": titulo.strip(),
            "descripcion": descr.strip(),
            "creador": creador.strip(),
            "fecha_limite": fecha.strip(),
        })
    return tareas

def guardar_tareas(lista):
    contenido = "\n".join(
        f"{t['id']};{t['curso']};{t['materia']};{t['titulo']};{t['descripcion']};{t['creador']};{t['fecha_limite']}"
        for t in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/tasks.txt", contenido)

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

if "base_general" not in st.session_state:
    st.session_state.base_general = BASE_GENERAL_DEFAULT.copy()

# ============================================
# LOGIN / REGISTRO / MODO ANÓNIMO
# ============================================

usuarios = cargar_usuarios()

# --- PANTALLA DE LOGIN ---
if st.session_state.usuario is None and not st.session_state.modo_anonimo:
    st.subheader("🔐 Iniciar sesión")

    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        user = next(
            (u for u in usuarios
             if u["email"].lower() == email.lower()
             and u["password"] == password),
            None
        )
        if user:
            st.session_state.usuario = user
            st.rerun()
        else:
            st.error("Email o contraseña incorrectos.")

    st.markdown("### 👤 Modo anónimo")
    if st.button("Entrar como invitado"):
        st.session_state.modo_anonimo = True
        st.rerun()

# --- DEFINIR USUARIO ---
if st.session_state.modo_anonimo:
    usuario = {
        "nombre": "Invitado",
        "apellido": "",
        "rol": "anonimo",
        "email": "anonimo@insm.edu",
        "curso": "General",
    }
else:
    usuario = st.session_state.usuario

# --- VALIDAR USUARIO ---
if usuario is None:
    st.warning("Por favor, iniciá sesión o entrá en modo anónimo para continuar.")
    st.stop()

# --- DATOS DEL USUARIO ---
rol = usuario["rol"]
email_usuario = usuario["email"]
curso_usuario = usuario["curso"]

# --- RECARGAR BASES ---
cursos = cargar_cursos()
tareas = cargar_tareas()


# ============================================
# CHAT IA
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

def construir_contexto_completo(usuario_actual, usuarios, cursos):
    contexto = "BASE GENERAL:\n"
    for p, r in st.session_state.base_general:
        contexto += f"{p} -> {r}\n"

    contexto += "\nCURSOS Y PROFESORES:\n"
    for c in cursos:
        contexto += f"{c['curso']} - {c['materia']} - {c['email']}\n"

    return contexto

st.subheader("💬 Chat con MercedarIA")

pregunta = st.text_input("Escribí tu pregunta:")
if st.button("Enviar"):
    contexto = construir_contexto_completo(usuario, usuarios, cursos)
    respuesta = consultar_deepseek(pregunta, contexto)

    st.session_state.chat_history.append({"role": "user", "content": pregunta})
    st.session_state.chat_history.append({"role": "assistant", "content": respuesta})

for m in st.session_state.chat_history:
    color = "#D8F5C8" if m["role"] == "user" else "#EEE"
    quien = "Vos" if m["role"] == "user" else "MercedarIA"
    st.markdown(f"""
<div style="background:{color};padding:8px;border-radius:8px;margin:4px 0;">
<b>{quien}:</b> {m['content']}
</div>
""", unsafe_allow_html=True)

# ============================================
# TAREAS (OPCIÓN A — SOLO tasks.txt)
# ============================================

if rol != "anonimo":
    st.header("📝 Tareas")

    with st.expander("Ver tareas"):
        if rol == "alumno":
            tareas_del_curso = [t for t in tareas if t["curso"] == curso_usuario]
            if not tareas_del_curso:
                st.write("No hay tareas cargadas para tu curso.")
            else:
                for t in tareas_del_curso:
                    st.markdown(f"""
### {t['titulo']}
📚 **Materia:** {t['materia']}
📌 {t['descripcion']}
⏳ **Fecha límite:** {t['fecha_limite']}
👨‍🏫 **Profesor:** {t['creador']}
---
""")

        if rol == "profe":
            st.subheader("Crear nueva tarea")
            opciones = [f"{c['curso']} — {c['materia']}" for c in cursos if c["email"] == email_usuario]

            if opciones:
                sel = st.selectbox("Curso y materia", opciones)
                curso_sel, materia_sel = sel.split(" — ", 1)
                titulo = st.text_input("Título")
                descr = st.text_area("Descripción")
                fecha = st.date_input("Fecha límite")

                if st.button("Agregar tarea"):
                    nuevo_id = str(max([int(t["id"]) for t in tareas] + [0]) + 1)
                    nueva = {
                        "id": nuevo_id,
                        "curso": curso_sel,
                        "materia": materia_sel,
                        "titulo": titulo,
                        "descripcion": descr,
                        "creador": email_usuario,
                        "fecha_limite": str(fecha),
                    }
                    tareas.append(nueva)
                    guardar_tareas(tareas)
                    st.success("Tarea agregada.")
                    st.rerun()

            st.subheader("Tus tareas creadas")
            mis_tareas = [t for t in tareas if t["creador"] == email_usuario]

            for t in mis_tareas:
                with st.expander(f"{t['curso']} — {t['materia']} — {t['titulo']}"):
                    nuevo_titulo = st.text_input("Título", t['titulo'], key=f"title_{t['id']}")
                    nuevo_descr = st.text_area("Descripción", t['descripcion'], key=f"desc_{t['id']}")
                    nuevo_fecha = st.text_input("Fecha límite", t['fecha_limite'], key=f"date_{t['id']}")

                    if st.button("Guardar", key=f"save_{t['id']}"):
                        t['titulo'] = nuevo_titulo
                        t['descripcion'] = nuevo_descr
                        t['fecha_limite'] = nuevo_fecha
                        guardar_tareas(tareas)
                        st.rerun()

                    if st.button("Borrar", key=f"delete_{t['id']}"):
                        tareas = [x for x in tareas if x["id"] != t["id"]]
                        guardar_tareas(tareas)
                        st.rerun()

        if rol == "admin":
            st.subheader("Todas las tareas")
            for t in tareas:
                st.markdown(f"""
### [{t['id']}] {t['titulo']}
🏫 **Curso:** {t['curso']}
📚 **Materia:** {t['materia']}
📌 {t['descripcion']}
⏳ {t['fecha_limite']}
👨‍🏫 {t['creador']}
---
""")

# ============================================
# PANEL ADMIN (SIN TXT POR MATERIA)
# ============================================

if rol == "admin":
    st.header("⚙️ Panel de Administración")

    tab_users, tab_courses = st.tabs(["Usuarios", "Cursos"])

    with tab_users:
        st.subheader("Usuarios")
        for u in usuarios:
            st.write(f"{u['email']} — {u['rol']} — {u['curso']}")

        email_sel = st.selectbox("Editar usuario", [u["email"] for u in usuarios])

        u_sel = next(u for u in usuarios if u['email'] == email_sel)

        nombre = st.text_input("Nombre", u_sel["nombre"])
        ape = st.text_input("Apellido", u_sel["apellido"])
        rol_edit = st.selectbox("Rol", ["alumno", "profe", "admin"], index=["alumno","profe","admin"].index(u_sel["rol"]))
        curso_edit = st.text_input("Curso", u_sel["curso"])
        pw = st.text_input("Contraseña", u_sel["password"])

        if st.button("Guardar usuario"):
            u_sel["nombre"] = nombre
            u_sel["apellido"] = ape
            u_sel["rol"] = rol_edit
            u_sel["curso"] = curso_edit
            u_sel["password"] = pw
            guardar_usuarios(usuarios)
            st.success("Usuario actualizado.")
            st.rerun()

        if st.button("Eliminar usuario"):
            usuarios = [u for u in usuarios if u["email"] != email_sel]
            guardar_usuarios(usuarios)
            st.success("Usuario eliminado.")
            st.rerun()

    with tab_courses:
        st.subheader("Cursos/Materias")
        for c in cursos:
            st.write(f"{c['curso']} — {c['materia']} (prof: {c['email']})")

        idc = st.text_input("ID")
        curso_n = st.text_input("Curso")
        materia_n = st.text_input("Materia")
        email_prof = st.text_input("Email profesor")

        if st.button("Agregar"):
            cursos.append({"id": idc, "curso": curso_n, "materia": materia_n, "email": email_prof})
            guardar_cursos(cursos)
            st.rerun()

