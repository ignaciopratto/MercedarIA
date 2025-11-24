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
# NORMALIZAR TEXTO (CURSOS/MATERIAS)
# ============================================

def normalizar(texto: str) -> str:
    if not texto:
        return ""
    return texto.replace("\u00a0", " ").strip()


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
            "curso": normalizar(curso.strip()),
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
            "curso": normalizar(curso.strip()),
            "materia": normalizar(materia.strip()),
            "email": email_prof.strip()
        })
    return cursos

def guardar_cursos(lista):
    contenido = "\n".join(
        f"{c['id']};{c['curso']};{c['materia']};{c['email']}" for c in lista
    )
    escribir_archivo_github(f"{BASES_ROOT}/courses.txt", contenido)


# ============================================
# TASKS — ID ÚNICO
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
        tareas.append({
            "id": id_.strip(),
            "curso": normalizar(curso.strip()),
            "materia": normalizar(materia.strip()),
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
# ARCHIVO POR MATERIA (FAQ / BASE ESPECÍFICA)
# ============================================

def archivo_base_curso_materia(curso, materia):
    cid = normalizar(curso).replace("°", "").replace(" ", "")
    mid = re.sub(r"[^a-z0-9]", "", normalizar(materia).lower())
    return f"{BASES_ROOT}/{cid}_{mid}.txt"


# ============================================
# BASE GENERAL + BASES POR CURSO
# (USADAS SOLO POR ADMIN)
# ============================================

BASE_GENERAL_DEFAULT = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quién eres", "Soy MercedarIA, tu asistente del Colegio Mercedaria."),
    ("cómo te llamas", "Me llamo MercedarIA, tu asistente virtual."),
    ("cómo estás", "Estoy funcionando correctamente."),
    ("adiós", "¡Hasta luego!"),
    ("directora", "La directora es Marisa Brizzio."),
    ("recreos", "Turno mañana: 8:35, 10:00, 11:35. Turno tarde: 14:40, 16:05, 17:50."),
    ("ubicación", "Arroyito, Córdoba, calle 9 de Julio 456.")
]

BASES_ESPECIFICAS_DEFAULT = {
    "1° A": [("¿Qué materias tengo?", "Biología, Lengua...")],
    "1° B": [("¿Qué materias tengo?", "Física, Matemática...")],
    # (Puedes pegar tus bases completas aquí)
}

if "base_general" not in st.session_state:
    st.session_state.base_general = BASE_GENERAL_DEFAULT.copy()

if "bases_por_curso" not in st.session_state:
    st.session_state.bases_por_curso = {
        c: v.copy() for c, v in BASES_ESPECIFICAS_DEFAULT.items()
    }


# ============================================
# CARGA INICIAL
# ============================================

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()


# ============================================
# CONFIG DE PÁGINA
# ============================================

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "modo_anonimo" not in st.session_state:
    st.session_state.modo_anonimo = False

st.title("🎓 MercedarIA — Asistente del Colegio")


# ============================================
# LOGIN / REGISTRO / INVITADO
# ============================================

if st.session_state.usuario is None and not st.session_state.modo_anonimo:

    col_login, col_reg, col_anon = st.columns([2, 2, 1])

    # ---------- LOGIN ----------
    with col_login:
        st.subheader("🔐 Iniciar sesión")

        email = st.text_input("Email")
        pw = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):
            usuarios = cargar_usuarios()
            user = next(
                (u for u in usuarios if u["email"].lower() == email.lower() and u["password"] == pw),
                None
            )
            if user:
                st.session_state.usuario = user
                st.success(f"Bienvenido/a {user['nombre']} {user['apellido']}")
                st.rerun()
            else:
                st.error("Datos incorrectos")
                st.stop()

    # ---------- REGISTRO ----------
    with col_reg:
        st.subheader("🧾 Crear cuenta")

        new_email = st.text_input("Nuevo email")
        new_nombre = st.text_input("Nombre")
        new_apellido = st.text_input("Apellido")

        tipo = st.selectbox("Tipo de cuenta", ["alumno", "profe"])

        if tipo == "alumno":
            new_curso = st.selectbox("Curso", sorted({c["curso"] for c in cursos}))
        else:
            new_curso = "-"

        new_pw = st.text_input("Contraseña", type="password")

        admin_key = ""
        if tipo == "profe":
            admin_key = st.text_input("Contraseña de administrador", type="password")

        if st.button("Crear cuenta"):
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
                st.success("Cuenta creada")
                st.rerun()

    # ---------- INVITADO ----------
    with col_anon:
        st.subheader("Invitado")
        if st.button("Entrar como invitado"):
            st.session_state.modo_anonimo = True
            st.rerun()


# ============================================
# CONTINUAR SOLO SI SESIÓN ACTIVA
# ============================================

if st.session_state.modo_anonimo:
    usuario = {
        "email": "anonimo",
        "nombre": "Invitado",
        "apellido": "",
        "rol": "anonimo",
        "curso": "General"
    }
else:
    usuario = st.session_state.usuario
# ============================================
# DATOS DEL USUARIO ACTUAL + RECARGA DE BASES
# ============================================

# Si por alguna razón no hay usuario, cortamos
if usuario is None:
    st.warning("Iniciá sesión o entrá como invitado para continuar.")
    st.stop()

rol = usuario["rol"]
email_usuario = usuario["email"]
curso_usuario = normalizar(usuario.get("curso", ""))

# Recargamos siempre por si hubo cambios en GitHub
usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

# ============================================
# BARRA SUPERIOR: INFO + CERRAR SESIÓN
# ============================================

col_info, col_logout = st.columns([4, 1])

with col_info:
    if rol == "anonimo":
        st.info("Conectado en **modo invitado** — solo podés usar la base general.")
    else:
        st.info(
            f"Conectado como **{usuario['nombre']} {usuario['apellido']}** — "
            f"Rol: **{rol}** — Curso: **{curso_usuario}**"
        )

with col_logout:
    if st.button("Cerrar sesión"):
        # Limpio todo lo relacionado al usuario
        st.session_state.usuario = None
        st.session_state.modo_anonimo = False
        st.session_state.chat_history = []
        st.rerun()

# ============================================
# PREPARAR HISTORIAL DE CHAT
# ============================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


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

def construir_contexto(usuario_actual, usuarios, cursos, tareas):
    """
    Arma el contexto que se le pasa a DeepSeek.
    - Invitado: solo base general
    - Alumno (y resto de roles no anónimos): base general + base por curso + users + courses + tasks
    """

    rol_u = usuario_actual["rol"]
    curso_u = normalizar(usuario_actual.get("curso", ""))

    # ---------- MODO INVITADO ----------
    if rol_u == "anonimo":
        contexto = (
            "Estás respondiendo a un usuario INVITADO.\n"
            "Solo podés usar la BASE GENERAL del colegio.\n"
            "No inventes datos personales, ni de cursos específicos.\n\n"
        )
        contexto += "BASE GENERAL DEL COLEGIO:\n"
        for p, r in st.session_state.base_general:
            contexto += f"{p} -> {r}\n"
        return contexto

    # ---------- USUARIO LOGUEADO ----------
    contexto = "INFORMACIÓN DEL USUARIO LOGUEADO:\n"
    contexto += f"- Nombre: {usuario_actual['nombre']} {usuario_actual['apellido']}\n"
    contexto += f"- Rol: {rol_u}\n"
    contexto += f"- Email: {usuario_actual['email']}\n"
    contexto += f"- Curso: {curso_u}\n\n"

    # ---------- BASE GENERAL ----------
    contexto += "BASE GENERAL DEL COLEGIO:\n"
    for p, r in st.session_state.base_general:
        contexto += f"{p} -> {r}\n"

    # ---------- BASE ESPECÍFICA DEL CURSO ----------
    base_curso = st.session_state.bases_por_curso.get(curso_u, [])
    if base_curso:
        contexto += f"\nBASE ESPECÍFICA DEL CURSO {curso_u}:\n"
        for p, r in base_curso:
            contexto += f"{p} -> {r}\n"

    # ---------- USERS (solo para conocer roles y cursos) ----------
    contexto += "\nUSUARIOS REGISTRADOS (para referencia de roles y cursos):\n"
    for u in usuarios:
        contexto += (
            f"- {u['nombre']} {u['apellido']} ({u['email']}), "
            f"rol: {u['rol']}, curso: {u['curso']}.\n"
        )

    # ---------- COURSES (solo del curso del usuario) ----------
    contexto += f"\nMATERIAS DEL CURSO {curso_u}:\n"
    materias_curso = [c for c in cursos if c["curso"] == curso_u]
    for c in materias_curso:
        contexto += f"- {c['materia']} dictada por {c['email']}.\n"

    # ---------- TASKS (solo del curso del usuario) ----------
    contexto += f"\nTAREAS DEL CURSO {curso_u}:\n"
    tareas_curso = [t for t in tareas if t["curso"] == curso_u]
    for t in tareas_curso:
        contexto += (
            f"- [{t['materia']}] {t['titulo']} — vence {t['fecha_limite']} — "
            f"creada por {t['creador']}.\n"
        )

    # ---------- BASES TXT POR MATERIA (solo curso del usuario) ----------
    contexto += (
        f"\nBASES POR MATERIA (archivos TXT en GitHub) del curso {curso_u}.\n"
        "El formato suele ser: pregunta;respuesta, una por línea.\n"
    )
    for c in materias_curso:
        path = archivo_base_curso_materia(c["curso"], c["materia"])
        contenido = leer_archivo_github(path)
        if contenido.strip():
            contexto += f"\n[MATERIA: {c['materia']}]\n{contenido}\n"

    contexto += (
        "\nINSTRUCCIÓN IMPORTANTE:\n"
        "- Respondé siempre pensando en el CURSO del usuario.\n"
        "- Si pregunta por cosas de otros cursos, aclarar que solo tenés información "
        "del curso actual.\n"
        "- No inventes datos si no están en las bases o en el contexto.\n"
    )

    return contexto


# ============================================
# CHAT CON BURBUJAS (COLORES PERSONALIZADOS)
# ============================================

st.subheader("💬 Chat con MercedarIA")

col_inp, col_btn = st.columns([4, 1])

with col_inp:
    pregunta = st.text_input("Escribí tu pregunta:", key="input_pregunta")

with col_btn:
    if st.button("Enviar", key="btn_enviar_pregunta"):
        if pregunta.strip():
            contexto = construir_contexto(usuario, usuarios, cursos, tareas)
            respuesta = consultar_deepseek(pregunta, contexto)

            # Guardar en historial
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
        # BURBUJA USUARIO → derecha, verde #71b548
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
        # BURBUJA IA → izquierda, azul oscuro #23263d
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
# SECCIÓN TAREAS / PANEL DE ROLES
# ============================================

st.header("📝 Tareas")

# ---------- INVITADO ----------
if rol == "anonimo":
    st.info("🔒 Iniciá sesión para ver tus tareas.")
    st.stop()

# ==========================================================
# =====================  ALUMNO  ===========================
# ==========================================================

if rol == "alumno":

    st.subheader("📘 Tareas de tu curso")

    tareas_curso = [t for t in tareas if t["curso"] == curso_usuario]

    if not tareas_curso:
        st.info("No hay tareas asignadas a tu curso.")
    else:
        for t in tareas_curso:
            st.markdown(f"""
### 📚 {t['titulo']}
**Materia:** {t['materia']}  
**Descripción:** {t['descripcion']}  
**Fecha límite:** {t['fecha_limite']}  
**Profesor:** {t['creador']}  
---
""")


# ==========================================================
# =====================  PROFESOR  =========================
# ==========================================================

elif rol == "profe":

    st.subheader("📘 Mis materias asignadas")

    materias_mias = [c for c in cursos if c["email"] == email_usuario]

    if not materias_mias:
        st.info("No tenés materias asignadas.")
    else:

        # -----------------------
        # CREAR NUEVA TAREA
        # -----------------------
        st.markdown("## ➕ Crear nueva tarea")

        opcion = st.selectbox(
            "Elegí curso — materia",
            [f"{c['curso']} — {c['materia']}" for c in materias_mias],
            key="select_crear_tarea"
        )

        curso_sel, materia_sel = opcion.split(" — ", 1)

        titulo = st.text_input("Título de la tarea")
        descripcion = st.text_area("Descripción")
        fecha = st.date_input("Fecha límite")

        if st.button("Agregar tarea", key="btn_agregar_tarea"):
            tareas = cargar_tareas()  # recarga para evitar desync
            nuevo_id = generar_id_unico(tareas)

            nueva = {
                "id": nuevo_id,
                "curso": curso_sel,
                "materia": materia_sel,
                "titulo": titulo.strip(),
                "descripcion": descripcion.strip(),
                "creador": email_usuario,
                "fecha_limite": str(fecha)
            }

            tareas.append(nueva)
            guardar_tareas(tareas)

            st.success("📌 Tarea agregada correctamente.")
            st.rerun()

        st.divider()


        # -----------------------
        # EDITAR / BORRAR TAREAS
        # -----------------------
        st.markdown("## ✏️ Editar o borrar mis tareas")

        tareas_mias = [t for t in tareas if t["creador"] == email_usuario]

        if not tareas_mias:
            st.info("Todavía no creaste tareas.")
        else:
            for t in tareas_mias:
                with st.expander(f"{t['curso']} — {t['materia']} — {t['titulo']}"):

                    ntitulo = st.text_input("Título", t["titulo"], key=f"ti_{t['id']}")
                    ndesc = st.text_area("Descripción", t["descripcion"], key=f"de_{t['id']}")
                    nfecha = st.text_input("Fecha límite", t["fecha_limite"], key=f"fe_{t['id']}")

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(f"Guardar cambios {t['id']}", key=f"save_{t['id']}"):
                            tareas = cargar_tareas()

                            for x in tareas:
                                if x["id"] == t["id"]:
                                    x["titulo"] = ntitulo
                                    x["descripcion"] = ndesc
                                    x["fecha_limite"] = nfecha

                            guardar_tareas(tareas)
                            st.success("Cambios guardados.")
                            st.rerun()

                    with col2:
                        if st.button(f"Eliminar tarea {t['id']}", key=f"del_{t['id']}"):
                            tareas = cargar_tareas()
                            tareas = [x for x in tareas if x["id"] != t["id"]]
                            guardar_tareas(tareas)
                            st.success("Tarea eliminada.")
                            st.rerun()


# ==========================================================
# =====================  ADMIN  ============================
# ==========================================================

elif rol == "admin":

    st.header("⚙️ Panel de Administración")

    tab_users, tab_courses, tab_bases = st.tabs(
        ["👥 Usuarios", "📘 Cursos y materias", "📚 Bases de conocimiento"]
    )

    # ============================================
    # ============  TAB 1 — USUARIOS  ============
    # ============================================

    with tab_users:

        st.subheader("Usuarios registrados")

        for u in usuarios:
            st.markdown(f"- **{u['email']}** — {u['rol']} — Curso: {u['curso']}")

        st.divider()

        st.subheader("Modificar / Eliminar usuario")

        email_sel = st.selectbox(
            "Seleccioná usuario",
            [u["email"] for u in usuarios],
            key="seleccion_usuario_admin"
        )

        u = next(u for u in usuarios if u["email"] == email_sel)

        nn = st.text_input("Nombre", u["nombre"])
        na = st.text_input("Apellido", u["apellido"])
        nr = st.selectbox("Rol", ["alumno", "profe", "admin"],
                          index=["alumno", "profe", "admin"].index(u["rol"]))
        nc = st.text_input("Curso", u["curso"])
        npw = st.text_input("Contraseña", u["password"])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Guardar cambios usuario", key="admin_guardar_usuario"):
                usuarios = cargar_usuarios()
                for x in usuarios:
                    if x["email"] == email_sel:
                        x["nombre"] = nn
                        x["apellido"] = na
                        x["rol"] = nr
                        x["curso"] = nc
                        x["password"] = npw

                guardar_usuarios(usuarios)
                st.success("Usuario actualizado.")
                st.rerun()

        with col2:
            if st.button("Eliminar usuario", key="admin_borrar_usuario"):
                usuarios = cargar_usuarios()
                usuarios = [x for x in usuarios if x["email"] != email_sel]
                guardar_usuarios(usuarios)
                st.success("Usuario eliminado.")
                st.rerun()


    # ============================================
    # =======  TAB 2 — CURSOS Y MATERIAS  ========
    # ============================================

    with tab_courses:

        st.subheader("Materias registradas")

        for c in cursos:
            st.markdown(f"- **{c['curso']} — {c['materia']}** (prof: {c['email']})")

        st.divider()

        st.subheader("➕ Agregar nueva materia")

        nid = st.text_input("ID")
        ncurso = st.text_input("Curso (Ej: 6° B)")
        nmat = st.text_input("Materia")
        nprof = st.text_input("Email del profesor")

        if st.button("Crear materia", key="admin_crear_materia"):
            cursos = cargar_cursos()
            cursos.append({
                "id": nid,
                "curso": normalizar(ncurso),
                "materia": normalizar(nmat),
                "email": nprof
            })
            guardar_cursos(cursos)
            st.success("Materia creada.")
            st.rerun()

        st.divider()

        st.subheader("✏️ Editar/Eliminar materia")

        mat_sel = st.selectbox(
            "Seleccionar materia",
            [f"{c['id']} — {c['curso']} — {c['materia']}" for c in cursos],
            key="admin_edit_materia"
        )

        idsel = mat_sel.split(" — ")[0]
        cobj = next(c for c in cursos if c["id"] == idsel)

        eid = st.text_input("ID", cobj["id"])
        ecurso = st.text_input("Curso", cobj["curso"])
        emat = st.text_input("Materia", cobj["materia"])
        eprof = st.text_input("Profesor", cobj["email"])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Guardar cambios materia", key="save_materia"):
                cursos = cargar_cursos()
                for x in cursos:
                    if x["id"] == idsel:
                        x["id"] = eid
                        x["curso"] = normalizar(ecurso)
                        x["materia"] = normalizar(emat)
                        x["email"] = eprof

                guardar_cursos(cursos)
                st.success("Materia actualizada.")
                st.rerun()

        with col2:
            if st.button("Eliminar materia", key="del_materia"):
                cursos = cargar_cursos()
                cursos = [x for x in cursos if x["id"] != idsel]
                guardar_cursos(cursos)
                st.success("Materia eliminada.")
                st.rerun()


    # ============================================
    # =======  TAB 3 — BASES DE CONOCIMIENTO =====
    # ============================================

    with tab_bases:

        st.subheader("📖 Base general")

        bg_text = "\n".join(f"{p};{r}" for p, r in st.session_state.base_general)

        edit_bg = st.text_area("Editar base general", bg_text, height=200)

        if st.button("Guardar base general", key="save_base_general"):
            nueva = []
            for linea in edit_bg.splitlines():
                if ";" in linea:
                    p, r = linea.split(";", 1)
                    nueva.append((p.strip(), r.strip()))
            st.session_state.base_general = nueva
            st.success("Base general actualizada.")
            st.rerun()

        st.divider()

        st.subheader("📘 Base específica por curso")

        cursos_existentes = sorted({c["curso"] for c in cursos})

        curso_sel = st.selectbox("Seleccionar curso", cursos_existentes)

        base_curso = st.session_state.bases_por_curso.get(curso_sel, [])
        base_text = "\n".join(f"{p};{r}" for p, r in base_curso)

        edit_bc = st.text_area(f"Editar base de {curso_sel}", base_text, height=200)

        if st.button(f"Guardar base {curso_sel}", key="save_base_curso"):
            nueva = []
            for linea in edit_bc.splitlines():
                if ";" in linea:
                    p, r = linea.split(";", 1)
                    nueva.append((p.strip(), r.strip()))

            st.session_state.bases_por_curso[curso_sel] = nueva
            st.success(f"Base de {curso_sel} actualizada.")
            st.rerun()
