import streamlit as st
import requests
import threading
import time
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"   # ⚠️ reemplazá con tu API key real si querés usar DeepSeek
ADMIN_PASSWORD = "mercedaria2025"      # 🔒 contraseña para editar la base

# Endpoints externos
API_USERS = "https://mi-insm.onrender.com/users"
API_TASKS = "https://mi-insm.onrender.com/tasks"
API_COURSES = "https://mi-insm.onrender.com/courses"
API_FILES = "https://mi-insm.onrender.com/files"
API_EGRESADOS = "https://mi-insm.onrender.com/egresados"

# ==============================
# BASE DE CONOCIMIENTO LOCAL (INICIAL)
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
    # ... mantiene el resto tal como lo tenías ...
    "6° B": [
        ("¿Qué materias tengo?", "Lengua y Literatura, Comunicación Audiovisual, Desarrollo de Soluciones Informáticas, Informática Aplicada, Filosofía, Formación para la Vida y el Trabajo, Química, Matemática, Ciudadanía y Política, Educación Religiosa Escolar, Teatro, Educación Física, Aplicaciones Informáticas e Inglés."),
        ("¿Cuáles son mis contraturnos?", "Educación Física, Aplicaciones Informáticas e Inglés."),
        ("¿A qué hora son los recreos?", "Los recreos son a las 8:35, 10:00 y 11:35 hs.")
    ]
}

# ==============================
# UTILIDADES / Ayudas
# ==============================
def obtener_contexto(lista):
    """Genera un texto con el contenido de la base para enviar a la IA si hace falta."""
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(lista, 1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto

def safe_get_json(url, timeout=10):
    """Llama al endpoint y devuelve JSON o lista vacía si falla."""
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.warning(f"No se pudo cargar {url}: {e}")
        return []

def normalizar_curso(texto):
    """Normaliza nombres de curso para comparaciones: e.g., '1 b', '1°B' -> '1° B'"""
    if not texto:
        return texto
    t = texto.strip().upper()
    # reemplazos usuales
    t = t.replace("º", "°")
    # juntar número + grado
    # buscamos un número inicial
    import re
    m = re.search(r"^(\d+)\s*[°º]?\s*([A-Z])?$", t)
    if m:
        num = m.group(1)
        letra = m.group(2) or ""
        letra = letra.strip()
        if letra:
            return f"{num}° {letra}"
        else:
            return f"{num}°"
    # tratar formatos como "1B" o "1°B"
    m2 = re.search(r"^(\d+)\s*°?\s*([A-Z])$", t)
    if m2:
        return f"{m2.group(1)}° {m2.group(2)}"
    # si ya tiene símbolo
    return t

def normalizar_materia(texto):
    """Normaliza string de materia para comparar de forma simple."""
    if not texto:
        return texto
    return ''.join(c for c in texto.lower() if c.isalnum() or c.isspace()).strip()

def encontrar_usuario_por_dni(users, dni):
    """Retorna el usuario cuya 'dni' coincide con la cadena dni (compara como string)."""
    try:
        dni_str = str(dni).strip()
        for u in users:
            if 'dni' in u and str(u['dni']).strip() == dni_str:
                return u
    except Exception:
        pass
    return None

# ==============================
# FUNCION PARA CONSULTAR DEEPSEEK (opcional)
# ==============================
def consultar_deepseek(pregunta, api_key, contexto):
    """Consulta a DeepSeek con la base de conocimiento como contexto, si está configurado."""
    if not api_key:
        return "No tengo configurada la API de DeepSeek. Activá DEEPSEEK_API_KEY para respuestas generativas."
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",
             "content": (
                 "Sos MercedarIA, el asistente educativo del Colegio Mercedaria. "
                 "Usá la base de conocimiento local para responder preguntas del colegio. "
                 "Si la información no está disponible, respondé de manera educativa y correcta."
             )},
            {"role": "user", "content": f"{contexto}\n\nPregunta: {pregunta}"}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error al conectar con DeepSeek: {e}"

# ==============================
# CONFIG STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")

# ==============================
# INICIO: PIDE DNI (LOGIN SIMPLE)
# ==============================
# Inicializar estado
if "user" not in st.session_state:
    st.session_state.user = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "courses" not in st.session_state:
    st.session_state.courses = []
if "users_cache" not in st.session_state:
    st.session_state.users_cache = []
if "bases" not in st.session_state:
    st.session_state.bases = {
        "General": BASE_GENERAL.copy(),
        **{curso: BASES_ESPECIFICAS.get(curso, []).copy() for curso in BASES_ESPECIFICAS}
    }
if "historial" not in st.session_state:
    st.session_state.historial = []
if "edicion_activa" not in st.session_state:
    st.session_state.edicion_activa = False

# Si no hay usuario logueado: pedir DNI y cargar datos desde API_USERS
if st.session_state.user is None:
    st.title("🔐 MercedarIA — Ingreso por DNI")
    dni_input = st.text_input("Ingresá tu DNI para continuar:", key="dni_input")
    if st.button("Ingresar"):
        if not dni_input or not dni_input.strip():
            st.error("Por favor ingresá un DNI válido.")
        else:
            with st.spinner("Buscando tu usuario en la base..."):
                users = safe_get_json(API_USERS)
                st.session_state.users_cache = users  # cache local
                usuario = encontrar_usuario_por_dni(users, dni_input)
                if usuario:
                    # normalizar curso si existe
                    curso_usuario_raw = usuario.get("course") or usuario.get("curso") or usuario.get("grade") or ""
                    curso_usuario = normalizar_curso(curso_usuario_raw)
                    usuario["course_normalized"] = curso_usuario
                    st.session_state.user = usuario

                    # Cargar tasks y courses
                    st.session_state.tasks = safe_get_json(API_TASKS)
                    # Normalizar campo course en tareas (por si están en formatos distintos)
                    for t in st.session_state.tasks:
                        if "course" in t and t["course"]:
                            t["course_normalized"] = normalizar_curso(str(t["course"]))
                        else:
                            t["course_normalized"] = ""
                    st.session_state.courses = safe_get_json(API_COURSES)
                    # Normalizar materias/curso en courses
                    for c in st.session_state.courses:
                        if "course" in c and c["course"]:
                            c["course_normalized"] = normalizar_curso(str(c["course"]))
                        else:
                            c["course_normalized"] = ""
                        if "subject" in c and c["subject"]:
                            c["subject_normalized"] = normalizar_materia(c["subject"])
                        else:
                            c["subject_normalized"] = ""

                    st.success(f"Bienvenido {usuario.get('name','Estudiante')} — Curso: {curso_usuario or 'No especificado'}")
                    st.experimental_rerun()
                else:
                    st.error("DNI no encontrado en la base de usuarios.")
    st.stop()  # detenemos la ejecución hasta que se loguee

# ==============================
# SI LLEGAMOS AQUI, USUARIO YA LOGUEADO
# ==============================
usuario = st.session_state.user
usuario_nombre = usuario.get("name") or usuario.get("full_name") or "Estudiante"
curso_usuario = usuario.get("course_normalized") or normalizar_curso(usuario.get("course") or "")
id_usuario = usuario.get("id") or usuario.get("user_id") or usuario.get("identifier")

st.title("🎓 MercedarIA - Asistente del Colegio Mercedaria")
st.caption(f"Conectado como: {usuario_nombre} — Curso: {curso_usuario}")

# ==============================
# INTEGRAR TASKS Y COURSES A LAS BASES LOCALES
# ==============================
# Queremos que la app "sepa" las tareas y cursos externos como parte de sus datos
# Convertimos tareas a pares pregunta/respuesta simples para poder buscarlas fácilmente
def tareas_a_base(tasks_list):
    """Convierte tareas a entries consumibles por la base local (consulta rápida)."""
    entradas = []
    for t in tasks_list:
        # Esperamos campos como 'title', 'description', 'course', 'user_id', 'due_date'
        title = t.get("title") or t.get("name") or "Tarea sin título"
        description = t.get("description") or t.get("desc") or ""
        course = t.get("course") or t.get("course_name") or ""
        course_norm = normalizar_curso(course)
        # Creamos una 'pregunta' tipo para buscar por curso: "tareas 1° B"
        pregunta = f"tareas {course_norm}".strip()
        respuesta = f"{title}"
        if description:
            respuesta += f" — {description}"
        # añadimos metadatos en la tupla si hace falta
        entradas.append((pregunta, respuesta, t))  # tercer elemento es el objeto original
    return entradas

# Generamos una lista auxiliar de tareas transformadas
_base_tasks_transformada = tareas_a_base(st.session_state.tasks)

# ==============================
# SELECCIÓN VISIBLE (opcional) y construcción de base_completa
# ==============================
CURSOS = ["General"] + sorted(list(BASES_ESPECIFICAS.keys()))
# Forzamos el curso seleccionado al curso del usuario para búsquedas por defecto,
# pero dejamos opción de cambiar en sidebar para simular que se pregunta sobre otro curso.
curso_seleccionado = st.sidebar.selectbox("📘 Seleccioná el curso para contexto (por defecto tu curso):",
                                           [curso_usuario] + [c for c in CURSOS if c != curso_usuario], index=0)

# Reconstruir la base completa tomando la base general + base del curso seleccionado
if curso_seleccionado not in st.session_state.bases:
    st.session_state.bases[curso_seleccionado] = []

base_completa = BASE_GENERAL.copy() + st.session_state.bases.get(curso_seleccionado, []).copy()

# Añadimos también las tareas relacionadas con ese curso a la "base_completa" para búsqueda textual simple
# (convertimos cada entrada (pregunta, respuesta, meta) a pregunta/resp)
for pregunta_t, respuesta_t, meta in _base_tasks_transformada:
    # sólo añadimos las tareas que pertenecen al curso seleccionado
    if meta.get("course_normalized") == normalizar_curso(curso_seleccionado):
        # añadimos con una pregunta clave tipo "tareas 1° B" y una respuesta descriptiva
        base_completa.append((pregunta_t.lower(), respuesta_t))

# ==============================
# CHAT
# ==============================
st.subheader(f"💬 Chat con MercedarIA ({curso_seleccionado})")
pregunta = st.text_input("Escribí tu pregunta:", key="chat_input")

enviar = st.button("Enviar", key=f"enviar_{curso_seleccionado}")
if enviar:
    if pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta))
        pregunta_normalizada = pregunta.lower().strip()
        respuesta = None

        # --- 1) Comandos especiales por prefijo (ej.: /tareas, /profesores) ---
        if pregunta_normalizada.startswith("/tareas") or pregunta_normalizada.startswith("tareas") or "tareas" in pregunta_normalizada:
            # Buscar tareas del curso y personales
            curso_u = curso_usuario or normalizar_curso(curso_seleccionado)
            id_u = id_usuario
            curso_u_norm = normalizar_curso(curso_u)

            tareas_curso = [t for t in st.session_state.tasks if t.get("course_normalized") == curso_u_norm]
            tareas_personales = []
            # Los endpoints pueden usar 'user_id' o 'assigned_to' u otro campo; chequeamos varios
            for t in st.session_state.tasks:
                if t.get("user_id") and str(t.get("user_id")) == str(id_u):
                    tareas_personales.append(t)
                elif t.get("assigned_to") and str(t.get("assigned_to")) == str(id_u):
                    tareas_personales.append(t)
                elif t.get("assignee") and str(t.get("assignee")) == str(id_u):
                    tareas_personales.append(t)

            texto = ""
            if tareas_curso:
                texto += "📘 **Tareas del curso:**\n"
                for t in tareas_curso:
                    titulo = t.get("title") or t.get("name") or "Tarea sin título"
                    desc = t.get("description") or t.get("desc") or ""
                    fecha = t.get("due_date") or t.get("due") or ""
                    linea = f"- {titulo}"
                    if desc:
                        linea += f" — {desc}"
                    if fecha:
                        linea += f" (Entrega: {fecha})"
                    texto += linea + "\n"
            else:
                texto += "📘 No hay tareas públicas para tu curso por ahora.\n"

            if tareas_personales:
                texto += "\n👤 **Tus tareas personales:**\n"
                for t in tareas_personales:
                    titulo = t.get("title") or t.get("name") or "Tarea sin título"
                    desc = t.get("description") or t.get("desc") or ""
                    fecha = t.get("due_date") or t.get("due") or ""
                    linea = f"- {titulo}"
                    if desc:
                        linea += f" — {desc}"
                    if fecha:
                        linea += f" (Entrega: {fecha})"
                    texto += linea + "\n"
            else:
                texto += "\n👤 No tienes tareas personales registradas.\n"

            respuesta = texto

        # --- 2) Consultas sobre profesores/docentes ---
        if not respuesta and ("profesor" in pregunta_normalizada or "profesora" in pregunta_normalizada or "docente" in pregunta_normalizada or "profesores" in pregunta_normalizada):
            # ejemplos: "quien es el profesor de matematica", "profesores", "que profesores tengo"
            curso_u_norm = normalizar_curso(curso_usuario)
            registros = [c for c in st.session_state.courses if c.get("course_normalized") == curso_u_norm]

            # Si hay 'de <materia>' intentamos extraer la materia
            if " de " in pregunta_normalizada:
                # Tomamos lo que sigue a 'de' (la primera ocurrencia)
                materia_consulta = pregunta_normalizada.split(" de ", 1)[1].strip()
                materia_consulta_norm = normalizar_materia(materia_consulta)

                encontrado = None
                # buscamos coincidencia por palabra en subject_normalized o subject
                for c in registros:
                    subj_norm = c.get("subject_normalized") or normalizar_materia(c.get("subject") or "")
                    if materia_consulta_norm in subj_norm or subj_norm in materia_consulta_norm:
                        encontrado = c
                        break
                if encontrado:
                    # intentar recuperar mail y nombre del docente
                    teacher_field = encontrado.get("teacher") or encontrado.get("teacher_email") or encontrado.get("email") or encontrado.get("profesor") or ""
                    subj = encontrado.get("subject") or encontrado.get("subject_normalized") or materia_consulta
                    respuesta = f"📘 El profesor/a de *{subj}* es:\n{teacher_field}"
                else:
                    # intentar buscar por coincidencias sueltas en todos los registros
                    posible = [c for c in st.session_state.courses if materia_consulta_norm in (c.get("subject_normalized") or "")]
                    if posible:
                        c = posible[0]
                        teacher_field = c.get("teacher") or c.get("teacher_email") or c.get("email") or ""
                        subj = c.get("subject") or ""
                        respuesta = f"📘 El profesor/a de *{subj}* es:\n{teacher_field}"
                    else:
                        respuesta = "No encontré el profesor para esa materia en tu curso. ¿Querés que busque en todas las materias disponibles?"
            else:
                # Listar todos los profesores del curso
                if registros:
                    texto = "👨‍🏫 **Profesores de tu curso:**\n"
                    for c in registros:
                        subj = c.get("subject") or "Materia sin nombre"
                        teacher = c.get("teacher") or c.get("teacher_email") or c.get("email") or "Email/Nombre no disponible"
                        texto += f"- **{subj}** → {teacher}\n"
                    respuesta = texto
                else:
                    respuesta = "No encontré registros de profesores para tu curso."

        # --- 3) Búsqueda directa en la base local (pregunta/keyword exacta o parcial) ---
        if not respuesta:
            # Buscamos coincidencia textual simple en base_completa
            pregunta_simple = pregunta_normalizada
            for p, r in base_completa:
                # usamos 'in' para coincidencias parciales
                try:
                    if p.lower() in pregunta_simple:
                        respuesta = r
                        break
                except Exception:
                    # en caso de entradas no-string
                    continue

        # --- 4) Si todavía no hay respuesta, intentamos usar la IA externa (DeepSeek) con contexto ---
        if not respuesta:
            contexto = obtener_contexto(base_completa)
            # Añadimos info del usuario/curso al contexto
            contexto += f"Usuario: {usuario_nombre}\nCurso: {curso_usuario}\nFecha: {datetime.utcnow().isoformat()}\n"
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)

        # Guardar respuesta en historial
        st.session_state.historial.append(("🤖 MercedarIA", respuesta))

# Mostrar historial (últimos 20 mensajes)
for rol, msg in st.session_state.historial[-40:]:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"🧍 *{rol}:* {msg}")
    else:
        # permitimos HTML sencillo para resaltar
        st.markdown(f"🧠 <span style='color:#00FFAA'><b>{rol}:</b></span> {msg}", unsafe_allow_html=True)

st.divider()

# ==============================
# PANEL DE EDICIÓN PROTEGIDO
# ==============================
st.subheader("🧩 Panel de Edición (solo personal autorizado)")

if not st.session_state.edicion_activa:
    password = st.text_input("🔒 Ingresá la contraseña para editar", type="password", key="pass")
    if st.button("Acceder", key="login"):
        if password == ADMIN_PASSWORD:
            st.session_state.edicion_activa = True
            st.success("✅ Acceso concedido.")
        else:
            st.error("❌ Contraseña incorrecta.")
else:
    st.success(f"Modo edición activado para: {curso_seleccionado}")

    base_editable = st.session_state.bases[curso_seleccionado]

    # Edición de preguntas/resp locales
    for i, (p, r) in enumerate(base_editable.copy()):
        col1, col2, col3 = st.columns([4, 5, 1])
        with col1:
            nueva_p = st.text_input(f"Pregunta {i+1}", p, key=f"p_{curso_seleccionado}_{i}")
        with col2:
            nueva_r = st.text_area(f"Respuesta {i+1}", r, key=f"r_{curso_seleccionado}_{i}")
        with col3:
            if st.button("🗑", key=f"del_{curso_seleccionado}_{i}"):
                base_editable.pop(i)
                st.experimental_rerun()
        base_editable[i] = (nueva_p, nueva_r)

    st.markdown("---")
    nueva_pregunta = st.text_input("➕ Nueva pregunta", key=f"nueva_p_{curso_seleccionado}")
    nueva_respuesta = st.text_area("Respuesta", key=f"nueva_r_{curso_seleccionado}")
    if st.button("Agregar a la base", key=f"add_{curso_seleccionado}"):
        if nueva_pregunta and nueva_respuesta:
            base_editable.append((nueva_pregunta.strip(), nueva_respuesta.strip()))
            st.success("✅ Pregunta agregada correctamente.")
        else:
            st.warning("⚠ Escribí una pregunta y su respuesta antes de agregar.")

    if st.button("🚪 Salir del modo edición", key=f"exit_{curso_seleccionado}"):
        st.session_state.edicion_activa = False
        st.info("🔒 Modo edición cerrado.")

st.divider()

# ==============================
# FUNCIONES EXTRA
# ==============================
if st.button("🧹 Limpiar chat", key="clear"):
    st.session_state.historial = []
    st.info("💬 Chat limpiado correctamente.")

st.caption("💡 Los cambios se mantienen mientras la app esté activa. Si se reinicia, se vuelve a la base original.")

# ==============================
# MANTENER SESIÓN VIVA (HILO)
# ==============================
def mantener_sesion_viva():
    """Evita que la sesión se cierre automáticamente (actualiza un timestamp)."""
    while True:
        time.sleep(300)
        st.session_state["keepalive"] = time.time()

if "keepalive_thread" not in st.session_state:
    hilo = threading.Thread(target=mantener_sesion_viva, daemon=True)
    hilo.start()
    st.session_state["keepalive_thread"] = True
