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

# Clave para crear cuentas de PROFESOR
ADMIN_MASTER_KEY = st.secrets.get("ADMIN_MASTER_KEY", "claveadmin")

BASES_ROOT = f"{GITHUB_BASE_FOLDER}/bases"


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
        f"{t['id']};{t['curso']};{t['materia']};{t['titulo']};{t['descripcion']};{t['creador']};{t['fecha_limite']}"
        for t in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/tasks.txt", contenido)


# ============================================
# ARCHIVO FAQ (PROFESORES)
# ============================================

def archivo_base_curso_materia(curso, materia):
    cid = curso.replace("°", "").replace(" ", "")
    mid = re.sub(r"[^a-z0-9]", "", materia.lower())
    return f"{BASES_ROOT}/{cid}_{mid}.txt"

def guardar_faqs_en_archivo(path, faqs):
    contenido = "\n".join(f"{f['pregunta']};{f['respuesta']}" for f in faqs)
    escribir_archivo_github(path, contenido)


# ============================================
# CONFIG DE PÁGINA
# ============================================

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "modo_anonimo" not in st.session_state:
    st.session_state.modo_anonimo = False

st.title("🎓 MercedarIA — Asistente del Colegio")
# ============================================
# LOGIN / REGISTRO / MODO ANÓNIMO
# ============================================

if st.session_state.usuario is None and not st.session_state.modo_anonimo:
    st.subheader("🔐 Iniciar sesión")

    col_login, col_reg, col_anon = st.columns([2, 2, 1])

    # ---------------------------
    # LOGIN
    # ---------------------------
    with col_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_password")

        if st.button("Ingresar"):
            usuarios = cargar_usuarios()
            user = next(
                (u for u in usuarios if u["email"].lower() == email.lower() and u["password"] == password),
                None
            )

            if user:
                st.session_state.usuario = user
                st.success(f"Bienvenido/a {user['nombre']} {user['apellido']}.")
                st.rerun()
            else:
                st.error("Email o contraseña incorrectos.")
                st.stop()

    # ---------------------------
    # REGISTRO
    # ---------------------------
    with col_reg:
        st.markdown("### 🧾 Crear cuenta")

        new_email = st.text_input("Email nuevo", key="reg_email")
        new_nombre = st.text_input("Nombre", key="reg_nombre")
        new_apellido = st.text_input("Apellido", key="reg_apellido")

        tipo_cuenta = st.selectbox(
            "Tipo de cuenta",
            ["alumno", "profe"],
            key="reg_tipo_cuenta"
        )

        if tipo_cuenta == "alumno":
            new_curso = st.selectbox(
                "Curso (solo alumnos)",
                sorted({c["curso"] for c in cursos}),
                key="reg_curso"
            )
        else:
            new_curso = "-"

        new_pw = st.text_input("Contraseña nueva", type="password", key="reg_pw")

        # Si es profesor → pedir clave admin
        if tipo_cuenta == "profe":
            admin_pw = st.text_input(
                "Contraseña de administrador para crear profesor",
                type="password",
                key="reg_admin_pw"
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

    # ---------------------------
    # MODO ANÓNIMO
    # ---------------------------
    with col_anon:
        if st.button("Entrar como invitado"):
            st.session_state.modo_anonimo = True
            st.session_state.usuario = None
            st.rerun()


# ============================================
# CREAR USUARIO ANÓNIMO si corresponde
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
curso_usuario = usuario["curso"]

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

# ============================================
# INFO DE USUARIO + CERRAR SESIÓN
# ============================================

col_info, col_logout = st.columns([4, 1])

with col_info:
    st.info(f"Conectado como **{usuario['nombre']} {usuario['apellido']}** — Rol: **{rol}** — Curso: **{curso_usuario}**")

with col_logout:
    if st.button("Cerrar sesión"):
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
        "max_tokens": 500,
    }

    try:
        r = requests.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error consultando DeepSeek: {e}"


# ============================================
# CONSTRUIR CONTEXTO DEL CHATBOT
# ============================================

def construir_contexto(usuario_actual):
    contexto = ""

    if usuario_actual["rol"] == "anonimo":
        contexto += "Modo anónimo: solo usar base general.\n"
        return contexto

    # Base general
    contexto += "BASE GENERAL DEL COLEGIO:\n"
    # (se puede agregar una base_general_default si querés)

    # Datos del curso
    contexto += f"\nCURSO DEL USUARIO: {usuario_actual['curso']}\n"

    # Cursos y profes
    contexto += "\nMATERIAS Y PROFESORADO DEL CURSO:\n"
    for c in cursos:
        if c["curso"] == usuario_actual["curso"]:
            contexto += f"{c['materia']} dictada por {c['email']}\n"

    # Tareas del curso
    contexto += "\nTAREAS DEL CURSO:\n"
    for t in tareas:
        if t["curso"] == usuario_actual["curso"]:
            contexto += f"- {t['materia']}: {t['titulo']} (vence {t['fecha_limite']})\n"

    # FAQ del curso/materia del usuario
    for c in cursos:
        if c["curso"] == usuario_actual["curso"]:
            path = archivo_base_curso_materia(c["curso"], c["materia"])
            contenido = leer_archivo_github(path)
            if contenido.strip():
                contexto += f"\nFAQ {c['materia']}:\n{contenido}\n"

    return contexto


# ============================================
# CHATBOX
# ============================================

st.subheader("💬 Chat con MercedarIA")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

col_input, col_send = st.columns([4, 1])

with col_input:
    pregunta = st.text_input("Escribí tu pregunta:")

with col_send:
    if st.button("Enviar"):
        if pregunta.strip():
            contexto = construir_contexto(usuario)
            respuesta = consultar_deepseek(pregunta, contexto)

            st.session_state.chat_history.append({"role": "user", "content": pregunta})
            st.session_state.chat_history.append({"role": "assistant", "content": respuesta})

for m in st.session_state.chat_history:
    if m["role"] == "user":
        st.markdown(f"<p style='text-align:right;'><b>Vos:</b> {m['content']}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align:left;'><b>MercedarIA:</b> {m['content']}</p>", unsafe_allow_html=True)

st.markdown("---")


# ============================================
# TAREAS — VISTAS PARA ALUMNO Y PROFESOR
# ============================================

st.header("📝 Tareas")

if rol == "alumno":
    st.subheader("Tareas de tu curso")
    tareas_curso = [t for t in tareas if t["curso"] == curso_usuario]

    if not tareas_curso:
        st.write("No hay tareas.")
    else:
        for t in tareas_curso:
            st.markdown(f"""
**{t['titulo']}**  
📚 {t['materia']}  
📌 {t['descripcion']}  
⏳ {t['fecha_limite']}  
👨‍🏫 {t['creador']}  
---""")

elif rol == "profe":

    st.subheader("Tus materias")
    materias_mias = [c for c in cursos if c["email"] == email_usuario]

    if not materias_mias:
        st.info("No tenés materias asignadas.")
    else:
        # CREAR TAREA
        st.markdown("### ➕ Crear nueva tarea")

        opcion = st.selectbox(
            "Elegí curso y materia",
            [f"{c['curso']} — {c['materia']}" for c in materias_mias]
        )

        curso_sel, mat_sel = opcion.split(" — ", 1)

        titulo = st.text_input("Título")
        descr = st.text_area("Descripción")
        fecha = st.date_input("Fecha límite")

        if st.button("Agregar tarea"):
            nuevo_id = str(max([int(t["id"]) for t in tareas] + [0]) + 1)
            nueva = {
                "id": nuevo_id,
                "curso": curso_sel,
                "materia": mat_sel,
                "titulo": titulo.strip(),
                "descripcion": descr.strip(),
                "creador": email_usuario,
                "fecha_limite": str(fecha),
            }
            tareas.append(nueva)
            guardar_tareas(tareas)
            st.success("Tarea agregada.")
            st.rerun()

        st.markdown("---")

        # EDITAR / BORRAR TAREA PROPIA
        st.markdown("### ✏️ Editar / borrar tareas")

        mis_tareas = [t for t in tareas if t["creador"] == email_usuario]

        for t in mis_tareas:
            with st.expander(f"{t['curso']} — {t['materia']} — {t['titulo']}"):
                new_title = st.text_input("Título", value=t["titulo"])
                new_desc = st.text_area("Descripción", value=t["descripcion"])
                new_date = st.text_input("Fecha (YYYY-MM-DD)", value=t["fecha_limite"])

                col_a, col_b = st.columns(2)

                with col_a:
                    if st.button(f"Guardar {t['id']}"):
                        t["titulo"] = new_title
                        t["descripcion"] = new_desc
                        t["fecha_limite"] = new_date
                        guardar_tareas(tareas)
                        st.rerun()

                with col_b:
                    if st.button(f"Borrar {t['id']}"):
                        tareas = [x for x in tareas if x["id"] != t["id"]]
                        guardar_tareas(tareas)
                        st.rerun()


# ============================================
# PANEL DEL PROFESOR — FAQ POR MATERIA
# ============================================

if rol == "profe":
    st.header("📚 Panel del Profesor — Preguntas y Respuestas por materia")

    materias_mias = [c for c in cursos if c["email"] == email_usuario]

    if materias_mias:
        seleccionado = st.selectbox(
            "Elegí materia",
            [f"{c['curso']} — {c['materia']}" for c in materias_mias]
        )

        curso_edit, materia_edit = seleccionado.split(" — ", 1)
        path = archivo_base_curso_materia(curso_edit, materia_edit)
        contenido = leer_archivo_github(path)

        faqs = []
        for linea in contenido.splitlines():
            if ";" in linea:
                p, r = linea.split(";", 1)
                faqs.append({"pregunta": p.strip(), "respuesta": r.strip()})

        st.markdown("### ➕ Agregar nueva pregunta/respuesta")
        with st.form("add_faq_form"):
            preg = st.text_input("Pregunta")
            resp = st.text_area("Respuesta")
            send = st.form_submit_button("Agregar")
            if send:
                if preg.strip() and resp.strip():
                    faqs.append({"pregunta": preg.strip(), "respuesta": resp.strip()})
                    guardar_faqs_en_archivo(path, faqs)
                    st.success("Agregado.")
                    st.rerun()

        st.markdown("---")
        st.markdown("### ❗ Editar o borrar preguntas existentes")

        for i, f in enumerate(faqs):
            with st.expander(f"{i+1}. {f['pregunta']}"):
                np = st.text_input("Pregunta", value=f["pregunta"], key=f"preg{i}")
                nr = st.text_area("Respuesta", value=f["respuesta"], key=f"resp{i}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Guardar {i}"):
                        faqs[i]["pregunta"] = np
                        faqs[i]["respuesta"] = nr
                        guardar_faqs_en_archivo(path, faqs)
                        st.rerun()
                with col2:
                    if st.button(f"Borrar {i}"):
                        faqs = [x for j, x in enumerate(faqs) if j != i]
                        guardar_faqs_en_archivo(path, faqs)
                        st.rerun()
# ============================================
# PANEL DEL ADMINISTRADOR
# ============================================

if rol == "admin":

    st.header("⚙️ Panel de Administración")

    tab_users, tab_courses, tab_bases = st.tabs(
        ["👥 Usuarios", "📘 Cursos y materias", "📚 Bases de conocimiento"]
    )

    # ============================================
    # TAB 1 — USUARIOS
    # ============================================

    with tab_users:

        st.subheader("Usuarios registrados:")
        for u in usuarios:
            st.markdown(f"- **{u['email']}** — Rol: {u['rol']} — Curso: {u['curso']}")

        st.markdown("---")
        st.subheader("Modificar / eliminar usuario")

        if usuarios:
            email_sel = st.selectbox(
                "Seleccionar usuario",
                [u["email"] for u in usuarios],
                key="admin_user_select"
            )

            user_sel = next(u for u in usuarios if u["email"] == email_sel)

            new_nom = st.text_input("Nombre", user_sel["nombre"])
            new_ape = st.text_input("Apellido", user_sel["apellido"])
            new_rol = st.selectbox("Rol", ["alumno", "profe", "admin"], 
                                   ["alumno", "profe", "admin"].index(user_sel["rol"]))
            new_curso = st.text_input("Curso", user_sel["curso"])
            new_pw = st.text_input("Contraseña", user_sel["password"])

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Guardar cambios"):
                    user_sel["nombre"] = new_nom.strip()
                    user_sel["apellido"] = new_ape.strip()
                    user_sel["rol"] = new_rol.strip()
                    user_sel["curso"] = new_curso.strip()
                    user_sel["password"] = new_pw.strip()
                    guardar_usuarios(usuarios)
                    st.success("Usuario actualizado.")
                    st.rerun()

            with col2:
                if st.button("Eliminar usuario"):
                    usuarios = [u for u in usuarios if u["email"] != email_sel]
                    guardar_usuarios(usuarios)
                    st.success("Usuario eliminado.")
                    st.rerun()


    # ============================================
    # TAB 2 — CURSOS Y MATERIAS
    # ============================================

    with tab_courses:

        st.subheader("Materias existentes")

        for c in cursos:
            st.markdown(
                f"- **{c['curso']} — {c['materia']}** (prof: {c['email']})"
            )

        st.markdown("---")
        st.subheader("Agregar nueva materia")

        new_id = st.text_input("ID")
        new_curso = st.text_input("Curso (Ej: 1° B)")
        new_materia = st.text_input("Materia")
        new_prof = st.text_input("Email del profesor asignado")

        if st.button("Crear materia"):
            cursos.append({
                "id": new_id.strip(),
                "curso": new_curso.strip(),
                "materia": new_materia.strip(),
                "email": new_prof.strip()
            })
            guardar_cursos(cursos)
            st.success("Materia agregada.")
            st.rerun()

        st.markdown("---")
        st.subheader("Editar materia existente")

        if cursos:
            mat_sel = st.selectbox(
                "Elegí materia",
                [f"{c['id']} — {c['curso']} — {c['materia']}" for c in cursos],
                key="admin_course_sel"
            )

            idsel = mat_sel.split(" — ")[0]
            course_obj = next(c for c in cursos if c["id"] == idsel)

            ec_id = st.text_input("ID:", course_obj["id"])
            ec_curso = st.text_input("Curso:", course_obj["curso"])
            ec_mat = st.text_input("Materia:", course_obj["materia"])
            ec_prof = st.text_input("Profesor:", course_obj["email"])

            colc1, colc2 = st.columns(2)

            with colc1:
                if st.button("Guardar materia"):
                    course_obj["id"] = ec_id
                    course_obj["curso"] = ec_curso
                    course_obj["materia"] = ec_mat
                    course_obj["email"] = ec_prof
                    guardar_cursos(cursos)
                    st.success("Materia actualizada.")
                    st.rerun()

            with colc2:
                if st.button("Eliminar materia"):
                    cursos = [c for c in cursos if c["id"] != idsel]
                    guardar_cursos(cursos)
                    st.success("Materia eliminada.")
                    st.rerun()


    # ============================================
    # TAB 3 — BASES DE CONOCIMIENTO
    # ============================================

    with tab_bases:

        st.subheader("📖 Base general")

        # Esta base es local en memoria
        if "base_general" not in st.session_state:
            st.session_state.base_general = [
                ("hola", "Hola, ¿cómo estás?"),
                ("directora", "La directora es Marisa Brizzio.")
            ]

        texto_bg = "\n".join(f"{p};{r}" for p, r in st.session_state.base_general)

        new_bg = st.text_area("Editar base general", texto_bg, height=200)

        if st.button("Guardar base general"):
            nueva = []
            for linea in new_bg.splitlines():
                if ";" in linea:
                    p, r = linea.split(";", 1)
                    nueva.append((p.strip(), r.strip()))

            st.session_state.base_general = nueva
            st.success("Base general actualizada (se guarda solo en esta sesión).")


        st.markdown("---")
        st.subheader("📘 Base específica por curso")

        cursos_existentes = sorted({c["curso"] for c in cursos})

        curso_sel = st.selectbox("Elegir curso", cursos_existentes)

        # Buscar materias del curso
        materias_sel = [c for c in cursos if c["curso"] == curso_sel]

        st.info(f"{curso_sel} tiene {len(materias_sel)} materias.")

        for c in materias_sel:
            cname = f"{c['curso']} — {c['materia']}"
            st.markdown(f"### {cname}")

            path = archivo_base_curso_materia(c["curso"], c["materia"])
            contenido_m = leer_archivo_github(path)

            edit = st.text_area(
                f"Editar archivo de {c['materia']}",
                contenido_m,
                key=f"base_edit_{c['id']}"
            )

            if st.button(f"Guardar {cname}"):
                escribir_archivo_github(path, edit)
                st.success(f"Actualizado {cname}.")
                st.rerun()
