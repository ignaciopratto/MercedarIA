import streamlit as st
import requests
import base64
import re
from datetime import datetime

# ============================================
# CONFIGURACIÓN DESDE SECRETS
# ============================================
DEEPSEEK_API_KEY = st.secrets["sk-f3e25c8aa4604877bc9238eca28e5e0e"]
GITHUB_TOKEN = st.secrets["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"]
GITHUB_USER = st.secrets["ignaciopratto"]
GITHUB_REPO = st.secrets["MercedarIA"]
GITHUB_BASE_FOLDER = st.secrets.get("GITHUB_BASE_FOLDER", "MercedarIA_completo")

BASES_ROOT = f"{GITHUB_BASE_FOLDER}/bases"


# ============================================
# FUNCIONES BASE PARA GITHUB
# ============================================

def github_raw_url(path_relativo: str) -> str:
    return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{path_relativo}"


def github_api_url(path_relativo: str) -> str:
    return f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{path_relativo}"


def leer_archivo_github(path_relativo: str) -> str:
    """Lee archivo de GitHub. Si no existe devuelve ''."""
    try:
        r = requests.get(github_raw_url(path_relativo), timeout=10)
        if r.status_code == 200:
            return r.text
        return ""
    except:
        return ""


def escribir_archivo_github(path_relativo: str, contenido: str) -> (bool, str):
    """Crea/actualiza archivo en GitHub."""
    url = github_api_url(path_relativo)

    # Obtener SHA si existe
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


def crear_archivo_si_falta(path_relativo: str, contenido_inicial: str):
    """Crea archivo si no existe."""
    existe = leer_archivo_github(path_relativo)
    if existe.strip() == "":
        escribir_archivo_github(path_relativo, contenido_inicial)


# ============================================
# AUTOCREACIÓN DE ARCHIVOS BASE
# ============================================

# USERS
crear_archivo_si_falta(
    f"{BASES_ROOT}/users.txt",
    "admin@insm.edu;Admin;Root;admin;General;admin123"
)

# COURSES
crear_archivo_si_falta(
    f"{BASES_ROOT}/courses.txt",
    "1;1° A;Matemática;profe.marta@insm.edu"
)

# TASKS
crear_archivo_si_falta(
    f"{BASES_ROOT}/tasks.txt",
    "1;Ejemplo de tarea;Esto es una tarea de ejemplo;1° A;profe.marta@insm.edu;2025-12-31"
)

# BASE GENERAL
crear_archivo_si_falta(
    f"{BASES_ROOT}/general.txt",
    "hola;Hola, ¿cómo estás?\nquién eres;Soy MercedarIA, tu asistente del Colegio Mercedaria."
)


# ============================================
# HELPERS PARA ARCHIVOS DE CURSO+MATERIA
# ============================================

def curso_to_id(curso: str) -> str:
    return curso.replace("°", "").replace(" ", "").strip() or "General"


def slugify_materia(materia: str) -> str:
    s = materia.lower().strip()
    reemplazar = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}
    for o, d in reemplazar.items():
        s = s.replace(o, d)
    return re.sub(r"[^a-z0-9]", "", s) or "general"


def archivo_base_curso_materia(curso: str, materia: str) -> str:
    cid = curso_to_id(curso)
    mid = slugify_materia(materia)
    return f"{BASES_ROOT}/{cid}_{mid}.txt"


def crear_base_curso_materia_si_falta(curso: str, materia: str):
    path = archivo_base_curso_materia(curso, materia)
    contenido_inicial = "¿qué es una ecuación?;Una ecuación es una igualdad matemática con incógnitas."
    if leer_archivo_github(path).strip() == "":
        escribir_archivo_github(path, contenido_inicial)


# ============================================
# PARSEAR Y GUARDAR USERS / TASKS / COURSES
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


# ============================================
# LOGIN (EMAIL + PASSWORD)
# ============================================

st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")
st.title("🎓 MercedarIA - Asistente del Colegio INSM")

if "usuario" not in st.session_state:
    st.session_state.usuario = None

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
            st.experimental_rerun()
        else:
            st.error("Email o contraseña incorrectos.")
            st.stop()

# ============================================
# USUARIO LOGUEADO
# ============================================

usuario = st.session_state.usuario
rol = usuario["rol"]
email_usuario = usuario["email"]
curso_usuario = usuario["curso"]

usuarios = cargar_usuarios()
cursos = cargar_cursos()
tareas = cargar_tareas()

st.info(
    f"Conectado como **{usuario['nombre']} {usuario['apellido']}** — "
    f"Rol: **{rol}** — Curso: **{curso_usuario}**"
)
# ============================================
# BASES DE CONOCIMIENTO (Q&A) Y DEEPSEEK
# ============================================

def cargar_base_qa(path_relativo: str):
    """Carga una base de preguntas/respuestas p;r por línea."""
    texto = leer_archivo_github(path_relativo)
    pares = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea or ";" not in linea:
            continue
        p, r = linea.split(";", 1)
        pares.append((p.strip(), r.strip()))
    return pares


def guardar_base_qa(path_relativo: str, pares):
    """Guarda lista de (pregunta, respuesta) en formato p;r."""
    lineas = []
    for p, r in pares:
        if p.strip() and r.strip():
            lineas.append(f"{p.strip()};{r.strip()}")
    contenido = "\n".join(lineas)
    return escribir_archivo_github(path_relativo, contenido)


def obtener_contexto_qa(lista_pares):
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(lista_pares, start=1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto


def consultar_deepseek(pregunta, api_key, contexto=""):
    if not api_key:
        return "No tengo una respuesta local y no hay API externa configurada."

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": contexto},
            {"role": "user", "content": pregunta}
        ],
        "max_tokens": 512,
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return "La API respondió, pero no pude interpretar la respuesta."
    except Exception as e:
        return f"Hubo un error consultando la API externa: {e}"


# ============================================
# HELPERS DE PERMISOS / TAREAS / PROFES
# ============================================

def cursos_de_profesor(email_prof: str, lista_cursos):
    """Devuelve lista de entradas de courses.txt donde está ese profesor."""
    return [
        c for c in lista_cursos
        if c["email"].strip().lower() == email_prof.strip().lower()
    ]


def cursos_unicos(lista_cursos):
    vistos = set()
    resultado = []
    for c in lista_cursos:
        nombre = c["curso"]
        if nombre not in vistos:
            vistos.add(nombre)
            resultado.append(nombre)
    return resultado


def obtener_texto_tareas_para_usuario(usuario, tareas):
    curso = usuario.get("curso", "").strip()
    if not curso:
        return "No tenés curso asignado, no puedo mostrar tareas."
    relevantes = [t for t in tareas if t["curso"].strip() == curso]
    if not relevantes:
        return f"No hay tareas cargadas para el curso {curso}."
    texto = f"📚 Tareas para tu curso {curso}:\n\n"
    for t in relevantes:
        texto += f"• {t['titulo']} — {t['descripcion']} (Límite: {t['fecha_limite']})\n"
    return texto


def obtener_profesores_para_curso(usuario, cursos):
    curso = usuario.get("curso", "").strip()
    if not curso:
        return "No tenés curso asignado."
    relev = [c for c in cursos if c["curso"].strip() == curso]
    if not relev:
        return f"No se encontraron profesores para el curso {curso}."
    texto = f"📘 Profesores de tu curso {curso}:\n\n"
    for c in relev:
        texto += f"• {c['materia']}: {c['email']}\n"
    return texto


# ============================================
# CARGAR BASES (GENERAL + ESPECÍFICAS SEGÚN ROL)
# ============================================

# Base general
base_general = cargar_base_qa(f"{BASES_ROOT}/general.txt")

# Base específica según rol
base_especifica = []

if rol == "alumno":
    # Alumno: todas las materias de su curso (según courses.txt)
    entradas = [c for c in cursos if c["curso"].strip() == curso_usuario.strip()]
    for cinfo in entradas:
        crear_base_curso_materia_si_falta(cinfo["curso"], cinfo["materia"])
        path = archivo_base_curso_materia(cinfo["curso"], cinfo["materia"])
        base_especifica.extend(cargar_base_qa(path))

elif rol == "profe":
    # Profe: solo cursos/materias donde aparece
    mis_cursos = cursos_de_profesor(email_usuario, cursos)
    for cinfo in mis_cursos:
        crear_base_curso_materia_si_falta(cinfo["curso"], cinfo["materia"])
        path = archivo_base_curso_materia(cinfo["curso"], cinfo["materia"])
        base_especifica.extend(cargar_base_qa(path))

elif rol == "admin":
    # Admin: todas las bases de cursos/materias listadas
    paths_vistos = set()
    for cinfo in cursos:
        crear_base_curso_materia_si_falta(cinfo["curso"], cinfo["materia"])
        path = archivo_base_curso_materia(cinfo["curso"], cinfo["materia"])
        if path not in paths_vistos:
            paths_vistos.add(path)
            base_especifica.extend(cargar_base_qa(path))

base_completa = base_general + base_especifica

if "historial" not in st.session_state:
    st.session_state.historial = []


# ============================================
# TABS PRINCIPALES
# ============================================

tabs = ["Chat", "Tareas"]
if rol in ("profe", "admin"):
    tabs.append("Bases de conocimiento")
if rol == "admin":
    tabs.append("Usuarios y cursos")

tab_objs = st.tabs(tabs)


# ============================================
# TAB 0: CHAT
# ============================================

with tab_objs[0]:
    st.subheader("💬 Chat con MercedarIA")

    pregunta = st.text_area("Escribí tu pregunta:", key="pregunta_chat")

    if st.button("Enviar pregunta"):
        q = (pregunta or "").strip()
        if q:
            st.session_state.historial.append(("👨‍🎓 Vos", q))
            q_lower = q.lower()
            respuesta = None

            # Buscar en base de conocimiento local
            for p, r in base_completa:
                try:
                    if p.lower() in q_lower:
                        respuesta = r
                        break
                except:
                    continue

            # Pregunta por tareas
            if not respuesta and ("tarea" in q_lower or "tareas" in q_lower):
                respuesta = obtener_texto_tareas_para_usuario(usuario, tareas)

            # Pregunta por profesores / mail
            if not respuesta and any(x in q_lower for x in ["profe", "profesor", "profesora", "profesores", "mail", "correo"]):
                respuesta = obtener_profesores_para_curso(usuario, cursos)

            # DeepSeek
            if not respuesta:
                contexto = obtener_contexto_qa(base_completa)
                respuesta = consultar_deepseek(q, DEEPSEEK_API_KEY, contexto)

            st.session_state.historial.append(("🤖 MercedarIA", respuesta))

    st.markdown("### Historial de conversación")
    for rol_h, msg in st.session_state.historial[-50:]:
        if rol_h == "👨‍🎓 Vos":
            st.markdown(f"🧍 *{rol_h}:* {msg}")
        else:
            st.markdown(f"🧠 **{rol_h}:** {msg}")

    if st.button("🧹 Limpiar historial"):
        st.session_state.historial = []
        st.info("Historial limpiado.")


# ============================================
# TAB 1: TAREAS
# ============================================

with tab_objs[1]:
    st.subheader("📚 Tareas")

    if rol == "alumno":
        st.markdown("### Tareas de tu curso")
        st.write(obtener_texto_tareas_para_usuario(usuario, tareas))

    elif rol == "profe":
        st.markdown("### Tareas de tus cursos")

        mis_cursos = cursos_de_profesor(email_usuario, cursos)
        cursos_prof = sorted({c["curso"] for c in mis_cursos})

        for curso in cursos_prof:
            st.markdown(f"#### Curso {curso}")
            t_curso = [t for t in tareas if t["curso"].strip() == curso.strip()]
            if not t_curso:
                st.write("No hay tareas cargadas.")
            else:
                for t in t_curso:
                    st.write(f"- **{t['titulo']}**: {t['descripcion']} (Límite: {t['fecha_limite']})")

        st.markdown("---")
        st.markdown("### ➕ Crear nueva tarea")

        if not mis_cursos:
            st.info("No estás asignado como profesor en ningún curso.")
        else:
            cursos_opciones = cursos_prof
            curso_sel = st.selectbox("Curso", cursos_opciones)
            titulo_n = st.text_input("Título de la tarea")
            descr_n = st.text_area("Descripción")
            fecha_n = st.date_input("Fecha límite", value=datetime.today())

            if st.button("Guardar tarea nueva"):
                lista_tareas = cargar_tareas()
                ids_exist = []
                for t in lista_tareas:
                    try:
                        ids_exist.append(int(t["id"]))
                    except:
                        pass
                nuevo_id = (max(ids_exist) + 1) if ids_exist else 1

                lista_tareas.append({
                    "id": str(nuevo_id),
                    "titulo": titulo_n.strip(),
                    "descripcion": descr_n.strip(),
                    "curso": curso_sel.strip(),
                    "creador": email_usuario,
                    "fecha_limite": fecha_n.strftime("%Y-%m-%d")
                })
                ok, msg = guardar_tareas(lista_tareas)
                if ok:
                    st.success("Tarea guardada correctamente.")
                else:
                    st.error(msg)

    elif rol == "admin":
        st.markdown("### Tareas de todos los cursos")

        cursos_uni = ["(Todos)"] + cursos_unicos(cursos)
        filtro = st.selectbox("Filtrar por curso", cursos_uni)

        if filtro == "(Todos)":
            tareas_mostrar = tareas
        else:
            tareas_mostrar = [t for t in tareas if t["curso"].strip() == filtro.strip()]

        if not tareas_mostrar:
            st.write("No hay tareas para mostrar.")
        else:
            for t in tareas_mostrar:
                st.write(
                    f"- **[{t['curso']}] {t['titulo']}**: {t['descripcion']} "
                    f"(Límite: {t['fecha_limite']} — Creador: {t['creador']})"
                )

        st.markdown("---")
        st.markdown("### ➕ Crear nueva tarea (admin)")

        cursos_disp = cursos_unicos(cursos)
        if cursos_disp:
            curso_sel = st.selectbox("Curso", cursos_disp)
            titulo_n = st.text_input("Título")
            descr_n = st.text_area("Descripción")
            fecha_n = st.date_input("Fecha límite", value=datetime.today())

            if st.button("Guardar tarea nueva (admin)"):
                lista_tareas = cargar_tareas()
                ids_exist = []
                for t in lista_tareas:
                    try:
                        ids_exist.append(int(t["id"]))
                    except:
                        pass
                nuevo_id = (max(ids_exist) + 1) if ids_exist else 1

                lista_tareas.append({
                    "id": str(nuevo_id),
                    "titulo": titulo_n.strip(),
                    "descripcion": descr_n.strip(),
                    "curso": curso_sel.strip(),
                    "creador": email_usuario,
                    "fecha_limite": fecha_n.strftime("%Y-%m-%d")
                })
                ok, msg = guardar_tareas(lista_tareas)
                if ok:
                    st.success("Tarea guardada correctamente.")
                else:
                    st.error(msg)
        else:
            st.info("No hay cursos definidos en courses.txt")


# ============================================
# TAB: BASES DE CONOCIMIENTO (PROFE/ADMIN)
# ============================================

if "Bases de conocimiento" in tabs:
    idx = tabs.index("Bases de conocimiento")
    with tab_objs[idx]:
        st.subheader("🧠 Edición de bases de conocimiento")

        # ----- PROFESOR -----
        if rol == "profe":
            mis_cursos = cursos_de_profesor(email_usuario, cursos)
            if not mis_cursos:
                st.info("No estás asignado como profesor en ningún curso.")
            else:
                opciones = [f"{c['curso']} — {c['materia']}" for c in mis_cursos]
                seleccion = st.selectbox("Seleccioná curso y materia", opciones)
                idx_sel = opciones.index(seleccion)
                c_sel = mis_cursos[idx_sel]

                curso_sel = c_sel["curso"]
                materia_sel = c_sel["materia"]
                path_sel = archivo_base_curso_materia(curso_sel, materia_sel)

                crear_base_curso_materia_si_falta(curso_sel, materia_sel)
                base_actual = cargar_base_qa(path_sel)

                st.caption(f"Archivo: {path_sel}")

                nuevos_pares = []
                for i, (p, r) in enumerate(base_actual):
                    p_edit = st.text_input(f"Pregunta {i+1}", p, key=f"p_{i}")
                    r_edit = st.text_area(f"Respuesta {i+1}", r, key=f"r_{i}")
                    nuevos_pares.append((p_edit, r_edit))

                st.markdown("---")
                nueva_p = st.text_input("➕ Nueva pregunta")
                nueva_r = st.text_area("Respuesta nueva")

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("Agregar pregunta"):
                        if nueva_p.strip() and nueva_r.strip():
                            nuevos_pares.append((nueva_p.strip(), nueva_r.strip()))
                            ok, msg = guardar_base_qa(path_sel, nuevos_pares)
                            if ok:
                                st.success("Pregunta agregada y base actualizada.")
                            else:
                                st.error(msg)
                        else:
                            st.warning("Completá pregunta y respuesta.")

                with col_b2:
                    if st.button("💾 Guardar cambios en base"):
                        ok, msg = guardar_base_qa(path_sel, nuevos_pares)
                        if ok:
                            st.success("Base actualizada correctamente.")
                        else:
                            st.error(msg)

        # ----- ADMIN -----
        elif rol == "admin":
            st.markdown("### Base general")

            base_gen = cargar_base_qa(f"{BASES_ROOT}/general.txt")
            nuevos_gen = []
            for i, (p, r) in enumerate(base_gen):
                p_edit = st.text_input(f"[General] Pregunta {i+1}", p, key=f"pg_{i}")
                r_edit = st.text_area(f"[General] Respuesta {i+1}", r, key=f"rg_{i}")
                nuevos_gen.append((p_edit, r_edit))

            nueva_pg = st.text_input("➕ Nueva pregunta (general)")
            nueva_rg = st.text_area("Respuesta (general)")

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                if st.button("Agregar a base general"):
                    if nueva_pg.strip() and nueva_rg.strip():
                        nuevos_gen.append((nueva_pg.strip(), nueva_rg.strip()))
                        ok, msg = guardar_base_qa(f"{BASES_ROOT}/general.txt", nuevos_gen)
                        if ok:
                            st.success("Base general actualizada.")
                        else:
                            st.error(msg)
                    else:
                        st.warning("Completá pregunta y respuesta.")

            with col_g2:
                if st.button("💾 Guardar cambios en base general"):
                    ok, msg = guardar_base_qa(f"{BASES_ROOT}/general.txt", nuevos_gen)
                    if ok:
                        st.success("Base general guardada.")
                    else:
                        st.error(msg)

            st.markdown("---")
            st.markdown("### Bases por curso y materia")

            if not cursos:
                st.info("No hay cursos cargados en courses.txt.")
            else:
                opciones_c = [f"{c['curso']} — {c['materia']}" for c in cursos]
                seleccion = st.selectbox("Seleccionar curso y materia", opciones_c)
                idx_sel = opciones_c.index(seleccion)
                c_sel = cursos[idx_sel]

                curso_sel = c_sel["curso"]
                materia_sel = c_sel["materia"]
                path_sel = archivo_base_curso_materia(curso_sel, materia_sel)

                crear_base_curso_materia_si_falta(curso_sel, materia_sel)
                base_act = cargar_base_qa(path_sel)

                st.caption(f"Archivo: {path_sel}")

                nuevos = []
                for i, (p, r) in enumerate(base_act):
                    p_edit = st.text_input(f"[{curso_sel} - {materia_sel}] Pregunta {i+1}", p, key=f"pc_{i}")
                    r_edit = st.text_area(f"[{curso_sel} - {materia_sel}] Respuesta {i+1}", r, key=f"rc_{i}")
                    nuevos.append((p_edit, r_edit))

                nueva_p = st.text_input("➕ Nueva pregunta (curso/materia)")
                nueva_r = st.text_area("Respuesta (curso/materia)")

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("Agregar pregunta (curso/materia)"):
                        if nueva_p.strip() and nueva_r.strip():
                            nuevos.append((nueva_p.strip(), nueva_r.strip()))
                            ok, msg = guardar_base_qa(path_sel, nuevos)
                            if ok:
                                st.success("Base curso/materia actualizada.")
                            else:
                                st.error(msg)
                        else:
                            st.warning("Completá pregunta y respuesta.")
                with col_c2:
                    if st.button("💾 Guardar cambios (curso/materia)"):
                        ok, msg = guardar_base_qa(path_sel, nuevos)
                        if ok:
                            st.success("Cambios guardados.")
                        else:
                            st.error(msg)


# ============================================
# TAB: USUARIOS Y CURSOS (SOLO ADMIN)
# ============================================

if "Usuarios y cursos" in tabs:
    idx = tabs.index("Usuarios y cursos")
    with tab_objs[idx]:
        st.subheader("🛠️ Administración de usuarios y cursos (solo admin)")

        if rol != "admin":
            st.error("No tenés permisos para ver esta sección.")
        else:
            sub_tabs = st.tabs(["Usuarios", "Cursos"])

            # ----- Usuarios -----
            with sub_tabs[0]:
                st.markdown("### Usuarios existentes")
                if not usuarios:
                    st.write("No hay usuarios cargados.")
                else:
                    for u in usuarios:
                        st.write(
                            f"- {u['email']} — {u['nombre']} {u['apellido']} "
                            f"(rol: {u['rol']}, curso: {u['curso']})"
                        )

                st.markdown("---")
                st.markdown("### ➕ Crear nuevo usuario")

                email_n = st.text_input("Email nuevo")
                nombre_n = st.text_input("Nombre")
                apellido_n = st.text_input("Apellido")
                rol_n = st.selectbox("Rol", ["alumno", "profe", "admin"])
                curso_n = st.text_input("Curso (para alumno ej: 1° A, para profe/admin podés usar General)", value="General")
                pass_n = st.text_input("Contraseña", type="password")

                if st.button("Crear usuario"):
                    if not email_n.strip() or not pass_n.strip():
                        st.warning("Email y contraseña son obligatorios.")
                    else:
                        if any(u["email"].lower() == email_n.lower() for u in usuarios):
                            st.error("Ya existe un usuario con ese email.")
                        else:
                            usuarios.append({
                                "email": email_n.strip(),
                                "nombre": nombre_n.strip(),
                                "apellido": apellido_n.strip(),
                                "rol": rol_n.strip(),
                                "curso": curso_n.strip(),
                                "password": pass_n.strip()
                            })
                            ok, msg = guardar_usuarios(usuarios)
                            if ok:
                                st.success("Usuario creado correctamente.")
                            else:
                                st.error(msg)

                st.markdown("---")
                st.markdown("### ✏️ Editar / eliminar usuario")

                if usuarios:
                    emails = [u["email"] for u in usuarios]
                    email_sel = st.selectbox("Seleccionar usuario", emails)
                    u_sel = next(u for u in usuarios if u["email"] == email_sel)

                    nombre_e = st.text_input("Nombre (editar)", value=u_sel["nombre"])
                    apellido_e = st.text_input("Apellido (editar)", value=u_sel["apellido"])
                    rol_e = st.selectbox("Rol (editar)", ["alumno", "profe", "admin"], index=["alumno", "profe", "admin"].index(u_sel["rol"]))
                    curso_e = st.text_input("Curso (editar)", value=u_sel["curso"])
                    pass_e = st.text_input("Contraseña (editar)", value=u_sel["password"])

                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        if st.button("Guardar cambios usuario"):
                            for u in usuarios:
                                if u["email"] == email_sel:
                                    u["nombre"] = nombre_e.strip()
                                    u["apellido"] = apellido_e.strip()
                                    u["rol"] = rol_e.strip()
                                    u["curso"] = curso_e.strip()
                                    u["password"] = pass_e.strip()
                                    break
                            ok, msg = guardar_usuarios(usuarios)
                            if ok:
                                st.success("Usuario actualizado.")
                            else:
                                st.error(msg)

                    with col_u2:
                        if st.button("Eliminar usuario"):
                            usuarios = [u for u in usuarios if u["email"] != email_sel]
                            ok, msg = guardar_usuarios(usuarios)
                            if ok:
                                st.success("Usuario eliminado.")
                            else:
                                st.error(msg)

            # ----- Cursos -----
            with sub_tabs[1]:
                st.markdown("### Cursos y materias existentes")

                if not cursos:
                    st.write("No hay cursos cargados.")
                else:
                    for c in cursos:
                        st.write(
                            f"- ID {c['id']}: {c['curso']} — {c['materia']} "
                            f"(Profe: {c['email']})"
                        )

                st.markdown("---")
                st.markdown("### ➕ Crear nuevo curso/materia")

                curso_n = st.text_input("Curso (ej: 1° A)")
                materia_n = st.text_input("Materia (ej: Matemática)")
                prof_n = st.text_input("Email del profesor")

                if st.button("Crear curso/materia"):
                    lista_cursos = cargar_cursos()
                    ids_exist = []
                    for c in lista_cursos:
                        try:
                            ids_exist.append(int(c["id"]))
                        except:
                            pass
                    nuevo_id = (max(ids_exist) + 1) if ids_exist else 1

                    lista_cursos.append({
                        "id": str(nuevo_id),
                        "curso": curso_n.strip(),
                        "materia": materia_n.strip(),
                        "email": prof_n.strip()
                    })
                    ok, msg = guardar_cursos(lista_cursos)
                    if ok:
                        st.success("Curso/materia creado.")
                    else:
                        st.error(msg)

                st.markdown("---")
                st.markdown("### ✏️ Editar / eliminar curso/materia")

                lista_cursos = cargar_cursos()
                if lista_cursos:
                    opciones_c = [f"ID {c['id']} — {c['curso']} — {c['materia']}" for c in lista_cursos]
                    sel_c = st.selectbox("Seleccionar curso/materia", opciones_c)
                    idx_sel = opciones_c.index(sel_c)
                    c_sel = lista_cursos[idx_sel]

                    curso_e = st.text_input("Curso (editar)", value=c_sel["curso"])
                    materia_e = st.text_input("Materia (editar)", value=c_sel["materia"])
                    prof_e = st.text_input("Profesor email (editar)", value=c_sel["email"])

                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if st.button("Guardar cambios curso/materia"):
                            lista_cursos[idx_sel]["curso"] = curso_e.strip()
                            lista_cursos[idx_sel]["materia"] = materia_e.strip()
                            lista_cursos[idx_sel]["email"] = prof_e.strip()
                            ok, msg = guardar_cursos(lista_cursos)
                            if ok:
                                st.success("Curso/materia actualizado.")
                            else:
                                st.error(msg)

                    with col_c2:
                        if st.button("Eliminar curso/materia"):
                            lista_cursos.pop(idx_sel)
                            ok, msg = guardar_cursos(lista_cursos)
                            if ok:
                                st.success("Curso/materia eliminado.")
                            else:
                                st.error(msg)


# ============================================
# CERRAR SESIÓN
# ============================================

st.markdown("---")
if st.button("🚪 Cerrar sesión"):
    st.session_state.clear()
    st.success("Sesión cerrada. Volvé a recargar la página para iniciar de nuevo.")
