import streamlit as st
import requests
import threading
import time
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # Colocá tu API key si querés usar DeepSeek
ADMIN_PASSWORD = "mercedaria2025"

# Endpoints remotos
API_USERS = "https://mi-insm.onrender.com/users"
API_TASKS = "https://mi-insm.onrender.com/tasks"
API_COURSES = "https://mi-insm.onrender.com/courses"
API_FILES = "https://mi-insm.onrender.com/files"
API_EGRESADOS = "https://mi-insm.onrender.com/egresados"

# ==============================
# BASE DE CONOCIMIENTO LOCAL (ORIGINAL)
# ==============================
BASE_GENERAL = [
    ("hola", "Hola, ¿cómo estás?"),
    ("quién eres", "Soy MercedarIA, tu asistente del colegio."),
    ("cómo te llamas", "Me llamo MercedarIA, tu asistente virtual."),
    ("cómo estás", "Estoy funcionando perfectamente, gracias por preguntar."),
    ("adiós", "¡Hasta luego! Que tengas un buen día."),
    ("quién es la directora", "La directora es Marisa Brizzio."),
    ("cuándo son los recreos", "Turno mañana: 8:35, 10:00, 11:35. Turno tarde: 14:40, 16:05, 17:50."),
    ("dónde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456."),
    ("cuándo empieza el ciclo lectivo", "El ciclo lectivo comienza el primer día hábil de marzo."),
    ("cuándo terminan las clases", "Generalmente a mediados de diciembre."),
]

BASES_ESPECIFICAS = {
    "1° A": [
        ("¿Qué materias tengo?", "Biología, Educación en Artes Visuales, Lengua y Literatura, Física, Geografía, Educación Tecnológica, Matemática, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física y Educación Tecnológica."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "1° B": [
        ("¿Qué materias tengo?", "Física, Matemática, Educación en Artes Visuales, Inglés, Educación Religiosa Escolar, Lengua y Literatura, Geografía, Ciudadanía y Participación, Educación Tecnológica, Biología y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Tecnológica y Educación Física."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "2° A": [
        ("¿Qué materias tengo?", "Matemática, Lengua y Literatura, Educación Religiosa Escolar, Música, Historia, Educación Tecnológica, Química, Computación, Ciudadanía y Participación, Biología, Inglés y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "2° B": [
        ("¿Qué materias tengo?", "Música, Historia, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés, Matemática, Lengua y Literatura, Educación Tecnológica, Química, Biología y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "3° A": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Inglés, Historia, Geografía, Química, Educación Tecnológica, Física, Educación Religiosa Escolar, Formación para la Vida y el Trabajo, Matemática, Educación Artística Visual, Música, Computación y Educación Física."),
        ("¿Cuáles son mis contraturnos?", "Educación Física y Formación para la Vida y el Trabajo."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "3° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Formación para la Vida y el Trabajo, Física, Historia, Geografía, Educación Artística Visual, Música, Matemática, Educación Tecnológica, Química, Computación, Educación Religiosa Escolar, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 14:40, 16:05 y 17:40 hs.")
    ],
    "4° A": [
        ("¿Qué materias tengo?", "Historia, Lengua y Literatura, Biología, Educación Religiosa Escolar, Matemática, Geografía, Educación Artística, Formación para la Vida y el Trabajo, Tecnologías de la Información y la Comunicación (TIC), Sociedad, Cultura y Comunicación, Antropología, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "4° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Biología, Educación Religiosa Escolar, Historia, Tecnología y Lenguajes de Programación, Geografía, Matemática, Sistemas Digitales de Información, Formación para la Vida y el Trabajo, Educación Artística, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "5° A": [
        ("¿Qué materias tengo?", "Metodología, Historia, Física, Geografía, Arte Cultural y Social, Educación Religiosa Escolar, Lengua y Literatura, Formación para la Vida y el Trabajo, Matemática, Educación Física, Psicología, Sociología e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Psicología, Sociología e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "5° B": [
        ("¿Qué materias tengo?", "Robótica, Música, Física, Matemática, Historia, Lengua y Literatura, Formación para la Vida y el Trabajo, Sistemas Digitales de Información, Geografía, Psicología, Educación Física, Desarrollo de Soluciones Informáticas e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Sistemas Digitales de Información, Desarrollo de Soluciones Informáticos e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "6° A": [
        ("¿Qué materias tengo?", "Ciudadanía y Política, Economía Política, Matemática, Geografía, Filosofía, Química, Lengua y Literatura, Historia, Educación Religiosa Escolar, Sociedad, Cultura y Comunicación, Teatro, Formación para la Vida y el Trabajo, Educación Física e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Sociedad, Cultura y Comunicación e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ],
    "6° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Comunicación Audiovisual, Desarrollo de Soluciones Informáticas, Informática Aplicada, Filosofía, Formación para la Vida y el Trabajo, Química, Matemática, Ciudadanía y Política, Educación Religiosa Escolar, Teatro, Educación Física, Aplicaciones Informáticas e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Aplicaciones Informáticas e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ]
}

# ==============================
# FUNCIONES AUXILIARES
# ==============================
def api_get(url):
    try:
        resp = requests.get(url, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            return data["data"]
        return data
    except Exception:
        return []

def normalizar_dni_para_comparacion(dni_raw):
    try:
        s = str(dni_raw)
    except Exception:
        s = ""
    return "".join(ch for ch in s if ch.isdigit())

def normalizar_curso(curso_raw):
    if not curso_raw:
        return None
    s = str(curso_raw).strip().lower()
    # ejemplo "1b", "1 b", "1°b"
    if len(s) >= 2:
        numero = s[0]
        division = s[-1].upper()
        return f"{numero}° {division}"
    return None

def tarea_pertenece_a_dni(tarea, dni_usuario, email_usuario):
    """
    Devuelve True si la tarea pertenece al usuario:
    - si la tarea está marcada como 'personal' == True
    - o si el campo 'creador' coincide con el email del usuario
    - o si el dni aparece en alguna clave del registro
    """
    if not tarea:
        return False

    # 1) Por campo 'personal'
    try:
        if tarea.get("personal") is True:
            return True
    except Exception:
        pass

    # 2) Por creador == email
    try:
        creador = tarea.get("creador") or tarea.get("creador_email") or tarea.get("creator") or ""
        if creador and isinstance(creador, str):
            if creador.strip().lower() == str(email_usuario).strip().lower():
                return True
    except Exception:
        pass

    # 3) Por dni dentro del registro (ej: assigned_to, dni, usuario_dni)
    dni_norm = normalizar_dni_para_comparacion(dni_usuario)
    if dni_norm:
        # claves comunes
        claves = ["dni", "assigned_to", "student_dni", "owner", "responsable", "usuario_dni", "user_dni"]
        try:
            for clave in claves:
                if clave in tarea:
                    if normalizar_dni_para_comparacion(tarea.get(clave)) == dni_norm:
                        return True
        except Exception:
            pass

    # 4) Buscar dni dentro de la representación completa
    try:
        if dni_norm and dni_norm in normalizar_dni_para_comparacion(str(tarea)):
            return True
    except Exception:
        pass

    return False
# ==============================
# CONSULTA A DEEPSEEK (OPCIONAL)
# ==============================
def consultar_deepseek(pregunta, api_key, contexto):
    if not api_key:
        return "No tengo configurada la clave de DeepSeek. Respondo con la base local y los datos del colegio."
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": ("Sos MercedarIA, el asistente educativo del Colegio Mercedaria. "
                                           "Usá la base local y la información de las APIs del colegio.")},
            {"role": "user", "content": f"{contexto}\n\nPregunta: {pregunta}"}
        ],
        "max_tokens": 500,
        "temperature": 0.6
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=60)
        r.raise_for_status()
        j = r.json()
        return j["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error al conectar con DeepSeek: {e}"

# ==============================
# INICIALIZACIÓN STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")
st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption("Responde con información local y con consultas a las APIs del colegio cuando corresponde.")

# ==============================
# LOGIN POR DNI
# ==============================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.subheader("🔐 Inicio de sesión")
    dni_ingresado = st.text_input("Ingresá tu Documento Nacional de Identidad (DNI):", key="dni_input")
    if st.button("Ingresar"):
        usuarios = api_get(API_USERS)
        encontrado = None
        for u in usuarios:
            if normalizar_dni_para_comparacion(u.get("dni", "")) == normalizar_dni_para_comparacion(dni_ingresado):
                encontrado = u
                break
        if encontrado:
            st.session_state.usuario = encontrado
            st.success(f"Bienvenido/a {encontrado.get('nombre','')} {encontrado.get('apellido','')}. Curso: {str(encontrado.get('curso','')).upper()}")
            st.rerun()
        else:
            st.error("DNI no encontrado. Verificá e intentá nuevamente.")
    st.stop()

# ==============================
# SESIÓN ACTIVA: DATOS DEL USUARIO
# ==============================
usuario = st.session_state.usuario
email_usuario = usuario.get("email", "")
dni_usuario = usuario.get("dni", "")
rol_usuario = (usuario.get("rol") or "").strip().lower()
curso_usuario_raw = usuario.get("curso", "")
curso_usuario = normalizar_curso(curso_usuario_raw)

if not curso_usuario:
    st.error("No se pudo interpretar el curso del usuario. Revisá los datos en la API de usuarios.")
    st.stop()

st.info(f"📘 Estás en el curso: {curso_usuario} (bloqueado)")

# ==============================
# INICIALIZACIÓN DE ESTADO
# ==============================
if "bases" not in st.session_state:
    st.session_state.bases = {
        "General": BASE_GENERAL.copy(),
        **{curso: BASES_ESPECIFICAS.get(curso, []).copy() for curso in BASES_ESPECIFICAS}
    }

if "historial" not in st.session_state:
    st.session_state.historial = []

if "edicion_activa" not in st.session_state:
    st.session_state.edicion_activa = False

# Construimos la base local que corresponde al curso del usuario (bloqueado)
curso_seleccionado = curso_usuario
base_completa = BASE_GENERAL + st.session_state.bases.get(curso_seleccionado, [])
contexto = obtener_contexto(base_completa)

# ==============================
# CARGAR DATOS REMOTOS: TASKS Y COURSES
# ==============================
lista_tareas = api_get(API_TASKS)
lista_cursos_api = api_get(API_COURSES)

# Normalizamos y filtramos tareas del curso del usuario
tareas_curso = []
tareas_personales = []
for t in lista_tareas or []:
    try:
        curso_t = str(t.get("curso", "")).strip().lower()
    except Exception:
        curso_t = ""
    # Si la tarea es del curso
    try:
        if curso_t and curso_t == (usuario.get("curso") or "").strip().lower():
            tareas_curso.append(t)
    except Exception:
        pass
    # Si la tarea es personal o creada por el usuario
    try:
        if tarea_pertenece_a_dni(t, dni_usuario, email_usuario):
            tareas_personales.append(t)
    except Exception:
        pass

# Eliminar duplicados (misma tarea en ambas listas)
ids_personales = {t.get("id") for t in tareas_personales if t.get("id") is not None}
tareas_curso = [t for t in tareas_curso if t.get("id") not in ids_personales]
# ==============================
# FUNCIONES PARA FORMATEAR SALIDAS
# ==============================
def formatear_detalle_tarea(t):
    titulo = t.get("titulo") or t.get("title") or "Sin título"
    descripcion = t.get("descripcion") or t.get("description") or ""
    fecha_limite = t.get("fecha_limite") or t.get("due_date") or ""
    creador = t.get("creador") or t.get("creator") or ""
    personal = t.get("personal") is True
    archivo = t.get("archivo") or t.get("file") or ""
    partes = [f"• {titulo}"]
    if descripcion:
        partes.append(f"  Descripción: {descripcion}")
    if fecha_limite:
        partes.append(f"  Fecha límite: {fecha_limite}")
    if creador:
        partes.append(f"  Creador: {creador}")
    if personal:
        partes.append("  (Tarea marcada como personal)")
    if archivo:
        partes.append(f"  Archivo: {archivo}")
    return "\n".join(partes)

def obtener_texto_tareas():
    texto = ""
    texto += "📚 Tareas del curso:\n\n"
    if tareas_curso:
        for t in tareas_curso:
            texto += formatear_detalle_tarea(t) + "\n\n"
    else:
        texto += "(No hay tareas cargadas para tu curso)\n\n"

    texto += "🧍‍♂️ Tus tareas personales:\n\n"
    if tareas_personales:
        for t in tareas_personales:
            texto += formatear_detalle_tarea(t) + "\n\n"
    else:
        texto += "(No tenés tareas personales cargadas)\n\n"

    return texto

# ==============================
# FUNCION PARA OBTENER PROFESORES POR CURSO
# ==============================
def obtener_profesores():
    """
    La API de cursos devuelve registros con:
    - curso_id (ej. "1a")
    - materia (ej. "Biología")
    - profesor_email (ej. "cecilia.viotti@institutolamerced.edu.ar")
    """
    if not lista_cursos_api:
        return "❌ No se pudo cargar la información de profesores desde la API."

    curso_id_normalizado = (usuario.get("curso") or "").strip().lower()

    materias = [c for c in lista_cursos_api if str(c.get("curso_id", "")).strip().lower() == curso_id_normalizado]

    if not materias:
        return "❌ No encontré asignaciones de profesores para tu curso."

    texto = "📘 Profesores asignados a tu curso:\n\n"
    for m in materias:
        materia = m.get("materia") or "Materia desconocida"
        profesor_email = m.get("profesor_email") or m.get("profesor") or m.get("profesor_mail") or "Email no disponible"
        texto += f"• {materia} — {profesor_email}\n"

    return texto

# ==============================
# INTERFAZ PRINCIPAL DEL CHAT
# ==============================
st.subheader(f"💬 Chat con MercedarIA — Curso: {curso_seleccionado}")

pregunta = st.text_input("Escribí tu pregunta:")
if st.button("Enviar"):
    if pregunta and pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        q = pregunta.strip().lower()
        respuesta = None

        # Respuesta por coincidencia en base local
        for p, r in base_completa:
            try:
                if p.lower() in q:
                    respuesta = r
                    break
            except Exception:
                continue

        # Consultas sobre tareas
        if not respuesta and ("tarea" in q or "tareas" in q):
            respuesta = obtener_texto_tareas()

        # Consultas sobre profesores
        if not respuesta and ("profe" in q or "profesor" in q or "profesores" in q or "mail" in q or "correo" in q):
            respuesta = obtener_profesores()

        # Si no hay respuesta local, consultar IA externa
        if not respuesta:
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)

        st.session_state.historial.append(("🤖 MercedarIA", respuesta))

# Mostrar historial
st.markdown("### Historial de conversación")
for rol, mensaje in st.session_state.historial[-40:]:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"🧍 *{rol}:* {mensaje}")
    else:
        st.markdown(f"🧠 <span style='color:#00FFAA'><b>{rol}:</b></span> {mensaje}", unsafe_allow_html=True)

st.divider()

# ==============================
# PANEL DE EDICIÓN RESTRINGIDO
# ==============================
st.subheader("🧩 Panel de Edición (solo personal autorizado)")

# Mostrar panel solo para roles 'profe' y 'admin'
if rol_usuario not in ("profe", "admin"):
    st.info("No tenés permisos para editar la base de conocimiento. Si sos docente o administrador, iniciá sesión con una cuenta con rol 'profe' o 'admin'.")
else:
    st.success(f"Usuario con permisos: rol = {rol_usuario}")

    # Selección del curso a editar (General + claves locales)
    opciones_cursos_para_editar = ["General"] + list(BASES_ESPECIFICAS.keys())
    curso_a_editar = st.selectbox("Seleccioná el curso que querés modificar", opciones_cursos_para_editar, index=0)

    base_editable = st.session_state.bases.get(curso_a_editar, [])

    for i, (p, r) in enumerate(base_editable.copy()):
        col1, col2, col3 = st.columns([4, 5, 1])
        with col1:
            nueva_p = st.text_input(f"Pregunta {i+1}", p, key=f"p_edit_{curso_a_editar}_{i}")
        with col2:
            nueva_r = st.text_area(f"Respuesta {i+1}", r, key=f"r_edit_{curso_a_editar}_{i}")
        with col3:
            if st.button("🗑", key=f"del_edit_{curso_a_editar}_{i}"):
                try:
                    base_editable.pop(i)
                except Exception:
                    pass
                st.rerun()
        base_editable[i] = (nueva_p, nueva_r)

    st.markdown("---")
    nueva_preg = st.text_input("➕ Nueva pregunta", key="nueva_p_edit")
    nueva_resp = st.text_area("Respuesta", key="nueva_r_edit")
    if st.button("Agregar a la base"):
        if nueva_preg and nueva_resp:
            base_editable.append((nueva_preg.strip(), nueva_resp.strip()))
            st.success("✅ Pregunta agregada correctamente.")
        else:
            st.warning("⚠ Completá pregunta y respuesta antes de agregar.")

    if st.button("Salir del modo edición"):
        st.rerun()

st.divider()

# ==============================
# LIMPIAR CHAT Y MISC
# ==============================
if st.button("🧹 Limpiar chat"):
    st.session_state.historial = []
    st.info("Historial limpiado correctamente.")

st.caption("Los cambios en la base local se mantienen mientras la aplicación esté activa. Al reiniciar la app, se volverá a la base original del código.")

# ==============================
# KEEP ALIVE THREAD
# ==============================
def mantener_sesion_viva():
    while True:
        time.sleep(300)
        st.session_state["keepalive"] = time.time()

if "keepalive_thread" not in st.session_state:
    hilo = threading.Thread(target=mantener_sesion_viva, daemon=True)
    hilo.start()
    st.session_state.keepalive_thread = True
