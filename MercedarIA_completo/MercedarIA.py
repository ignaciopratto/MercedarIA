import streamlit as st
import requests
import threading
import time
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # API KEY opcional (si no la tenés, queda solo el fallback)
ADMIN_PASSWORD = "mercedaria2025"

API_USERS = "https://mi-insm.onrender.com/users"
API_TASKS = "https://mi-insm.onrender.com/tasks"
API_COURSES = "https://mi-insm.onrender.com/courses"
API_FILES = "https://mi-insm.onrender.com/files"
API_EGRESADOS = "https://mi-insm.onrender.com/egresados"

# -------------------------------
# FUNCIÓN PARA USAR DEEPSEEK
# -------------------------------
def consultar_deepseek(pregunta, api_key, contexto=""):
    """
    Envía la pregunta a la API de DeepSeek para obtener una respuesta generada.
    Requiere API key válida. Si hay error, devuelve mensaje de error legible.
    """
    if not api_key or not str(api_key).strip():
        return "No tengo una respuesta en la base local y no está configurada la API externa."

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
        # Manejar estructura robusta
        if isinstance(data, dict):
            # intentar caminos comunes
            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                choice = data["choices"][0]
                # algunos APIs devuelven texto directo en "text" o en "message"->"content"
                if isinstance(choice, dict):
                    if "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
                        return choice["message"]["content"]
                    if "text" in choice:
                        return choice["text"]
            # fallback si estructura distinta
            if "answer" in data:
                return data["answer"]
        return "La API externa respondió, pero no pude interpretar la respuesta."
    except Exception as e:
        return f"Hubo un error consultando DeepSeek: {str(e)}"

# ==============================
# BASE LOCAL GENERAL
# ==============================
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

# ==============================
# BASE POR CURSO
# (idéntica a la que venías usando)
# ==============================
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

# =====================================
# FUNCIÓN: CONVERTIR BASE A CONTEXTO
# =====================================
def obtener_contexto(lista):
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(lista, 1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto

# ==============================
# UTILIDADES Y FUNCIONES AUXILIARES
# ==============================
def api_get(url):
    """
    Obtiene datos de la API remota. Devuelve lista o [] si hay error.
    """
    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        data = r.json()
        # soportar estructuras tipo {"data": [...]}
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            return data["data"]
        return data
    except Exception:
        return []

def normalizar_curso(curso_raw):
    """
    Normaliza formatos como "1b", "1 b", "1°b", "1° B" -> "1° B"
    Si no se puede normalizar devuelve cadena vacía.
    """
    try:
        s = str(curso_raw).strip().lower()
    except Exception:
        return ""
    if len(s) < 2:
        return ""
    numero = s[0]
    division = s[-1].upper()
    return f"{numero}° {division}"

def limpiar_estado_antes_login():
    """
    Limpia del session_state los datos que dependen del usuario anterior.
    """
    for clave in ["usuario", "tareas_curso", "tareas_personales", "lista_tareas", "lista_cursos_api", "historial"]:
        if clave in st.session_state:
            st.session_state.pop(clave, None)

def tarea_pertenece_al_usuario(tarea, email_usuario):
    """
    Una tarea personal pertenece solo a su creador.
    personal=True NO implica que sea visible para todos.
    Lógica:
      - Obtener creador (campo 'creador' o 'creator')
      - Si no existe creador -> no asignar (evita mostrar tareas 'huérfanas' como personales)
      - Si creador no tiene @ completar con dominio institucional @insm.edu
      - Comparar case-insensitive con email_usuario
    """
    if not tarea or not isinstance(tarea, dict):
        return False

    email_user = (email_usuario or "").strip().lower()
    if not email_user:
        return False

    creador_raw = (tarea.get("creador") or tarea.get("creator") or "").strip().lower()
    if not creador_raw:
        # no hay creador definido: no tratamos la tarea como personal de nadie
        return False

    # Si el creador viene sin dominio, asumimos dominio institucional
    if "@" not in creador_raw:
        creador_raw = creador_raw + "@insm.edu"

    return creador_raw == email_user

def formatear_detalle_tarea(t):
    """
    Devuelve un bloque de texto con todos los datos relevantes de la tarea.
    """
    titulo = t.get("titulo") or t.get("title") or "Sin título"
    descripcion = t.get("descripcion") or t.get("description") or ""
    fecha_limite = t.get("fecha_limite") or t.get("due_date") or ""
    creador = t.get("creador") or t.get("creator") or ""
    archivo = t.get("archivo") or t.get("file") or ""

    partes = [f"• {titulo}"]
    if descripcion:
        partes.append(f"  Descripción: {descripcion}")
    if fecha_limite:
        partes.append(f"  Fecha límite: {fecha_limite}")
    return "\n".join(partes)

def obtener_texto_tareas():
    texto = ""
    texto += "📚 Tareas del curso:\n\n"
    if st.session_state.tareas_curso:
        for t in st.session_state.tareas_curso:
            texto += formatear_detalle_tarea(t) + "\n\n"
    else:
        texto += "(No hay tareas cargadas para tu curso)\n\n"

    texto += "🧍‍♂️ Tus tareas personales:\n\n"
    if st.session_state.tareas_personales:
        for t in st.session_state.tareas_personales:
            texto += formatear_detalle_tarea(t) + "\n\n"
    else:
        texto += "(No tenés tareas personales cargadas)\n\n"

    return texto

def obtener_profesores_por_curso():
    """
    Usa la lista de cursos de la API (st.session_state.lista_cursos_api)
    y busca entradas cuya clave 'curso_id' coincida con el curso del usuario.
    Cada registro esperado tiene: curso_id, materia, profesor_email
    """
    lista = st.session_state.lista_cursos_api or []
    curso_id_norm = (usuario.get("curso") or "").strip().lower()
    entradas = [c for c in lista if str(c.get("curso_id", "")).strip().lower() == curso_id_norm]
    if not entradas:
        return "No se encontró información de profesores para tu curso."
    texto = "📘 Profesores asignados a tu curso:\n\n"
    for e in entradas:
        materia = e.get("materia") or "Materia desconocida"
        prof_email = e.get("profesor_email") or e.get("profesor") or e.get("profesor_mail") or "Email no disponible"
        texto += f"• {materia} — {prof_email}\n"
    return texto

# ==============================
# INICIALIZACIÓN STREAMLIT
# ==============================
st.set_page_config(page_title="MercedarIA", page_icon="🤖", layout="wide")
st.title("🎓 MercedarIA - Asistente del Colegio INSM")

# ==============================
# PANTALLA DE LOGIN (LIMPIA ESTADO ANTERIOR)
# ==============================
if "usuario" not in st.session_state or st.session_state.get("usuario") is None:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.subheader("🔐 Ingresá para continuar")
    email_input = st.text_input("Correo electrónico (Gmail):", key="email_login")

    if st.button("Ingresar"):
        limpiar_estado_antes_login()
        usuarios = api_get(API_USERS)
        encontrado = None
        for u in usuarios or []:
            if (u.get("email", "").strip().lower() == (email_input or "").strip().lower()):
                encontrado = u
                break

        if encontrado:
            # Guardar solo campos relevantes (sin DNI como llave primaria para login)
            st.session_state.usuario = {
                "email": encontrado.get("email", ""),
                "nombre": encontrado.get("nombre", ""),
                "apellido": encontrado.get("apellido", ""),
                "rol": (encontrado.get("rol") or "").strip().lower(),
                "curso": encontrado.get("curso", "")
            }
            # inicializar estructuras vacías dependientes del usuario
            st.session_state.lista_tareas = []
            st.session_state.lista_cursos_api = []
            st.session_state.tareas_curso = []
            st.session_state.tareas_personales = []
            st.session_state.historial = []
            st.success(f"Bienvenido/a {st.session_state.usuario['nombre']} {st.session_state.usuario['apellido']}.")
            st.rerun()
        else:
            st.error("Correo no encontrado. Revisá y volvé a intentarlo.")
    st.stop()

# ==============================
# USUARIO LOGUEADO (YA INICIALIZADO)
# ==============================
usuario = st.session_state.usuario
email_usuario = usuario.get("email", "")
rol_usuario = (usuario.get("rol") or "").strip().lower()
curso_usuario = normalizar_curso(usuario.get("curso", ""))

# ==============================
# RECONSTRUIR BASES LOCALES SEGÚN EL CURSO DEL USUARIO
# ==============================

# Asegurar que exista st.session_state.bases
if "bases" not in st.session_state:
    st.session_state.bases = {
        "General": BASE_GENERAL.copy(),
        **{curso: BASES_ESPECIFICAS.get(curso, []).copy() for curso in BASES_ESPECIFICAS}
    }

# Asegurar que exista la clave del curso del usuario (si su curso no está, crear una vacía)
if curso_usuario not in st.session_state.bases:
    st.session_state.bases[curso_usuario] = []

# BASE COMPLETA = BASE GENERAL + BASE ESPECÍFICA DEL CURSO DEL USUARIO
base_completa = BASE_GENERAL + st.session_state.bases[curso_usuario]

if not curso_usuario:
    st.error("No se pudo interpretar el curso del usuario. Contactá al administrador.")
    st.stop()

st.info(f"Estás conectado como: {usuario.get('nombre','')} {usuario.get('apellido','')} — Curso: {curso_usuario} — Rol: {rol_usuario}")

# ==============================
# CARGAR DATOS REMOTOS (TAREAS Y CURSOS)
# ==============================
# Guardamos en session para evitar múltiples requests durante la sesión
if not st.session_state.get("lista_tareas"):
    st.session_state.lista_tareas = api_get(API_TASKS) or []

if not st.session_state.get("lista_cursos_api"):
    st.session_state.lista_cursos_api = api_get(API_COURSES) or []

# construimos listas específicas para el usuario actual
st.session_state.tareas_curso = []
st.session_state.tareas_personales = []

for t in st.session_state.lista_tareas or []:
    try:
        curso_t = (t.get("curso") or "").strip().lower()
    except Exception:
        curso_t = ""
    try:
        tarea_id = t.get("id")
    except Exception:
        tarea_id = None

    # Tareas del curso (comparación simple por cadena)
    try:
        if curso_t and curso_t == (usuario.get("curso") or "").strip().lower():
            st.session_state.tareas_curso.append(t)
    except Exception:
        pass

    # Tareas personales (solo si el creador coincide con el email del usuario)
    try:
        if tarea_pertenece_al_usuario(t, email_usuario):
            st.session_state.tareas_personales.append(t)
    except Exception:
        pass

# Evitar duplicados: si una tarea aparece en personales y en curso la dejamos sólo en personales
ids_personales = {t.get("id") for t in st.session_state.tareas_personales if t.get("id") is not None}
st.session_state.tareas_curso = [t for t in st.session_state.tareas_curso if t.get("id") not in ids_personales]

# ==============================
# INTERFAZ DE CHAT PRINCIPAL
# ==============================
st.subheader(f"💬 Chat con MercedarIA — Curso: {curso_usuario} (bloqueado)")

pregunta = st.text_input("Escribí tu pregunta:", key="pregunta_principal")
if st.button("Enviar"):
    if pregunta and pregunta.strip():
        st.session_state.historial.append(("👨‍🎓 Vos", pregunta.strip()))
        q = pregunta.strip().lower()
        respuesta = None

        # 1) Coincidencia en base local
        for p, r in base_completa:
            try:
                if p.lower() in q:
                    respuesta = r
                    break
            except Exception:
                continue

        # 2) Consultas de tareas
        if not respuesta and ("tarea" in q or "tareas" in q):
            respuesta = obtener_texto_tareas()

        # 3) Consultas de profesores / mails
        if not respuesta and ("profe" in q or "profesor" in q or "profesores" in q or "mail" in q or "correo" in q):
            respuesta = obtener_profesores_por_curso()

        # 4) Si sigue sin respuesta, usar DeepSeek (si existe API key)
        if not respuesta:
            respuesta = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, obtener_contexto(base_completa))

        st.session_state.historial.append(("🤖 MercedarIA", respuesta))

# Mostrar historial (últimas 50 entradas)
st.markdown("### Historial de conversación")
for rol, msg in st.session_state.historial[-50:]:
    if rol == "👨‍🎓 Vos":
        st.markdown(f"🧍 *{rol}:* {msg}")
    else:
        st.markdown(f"🧠 <span style='color:#00FFAA'><b>{rol}:</b></span> {msg}", unsafe_allow_html=True)

st.divider()

# ==============================
# PANEL DE EDICIÓN RESTRINGIDO (solo 'profe' y 'admin')
# ==============================
st.subheader("🧩 Panel de Edición (solo personal autorizado)")

if rol_usuario not in ("profe", "admin"):
    st.info("No tenés permisos para editar la base de conocimiento. Si sos docente o administrador, iniciá sesión con una cuenta con rol 'profe' o 'admin'.")
else:
    st.success(f"Usuario con permisos de edición: rol = {rol_usuario}")
    # Permitimos seleccionar qué curso editar (General + locales)
    opciones_edicion = ["General"] + list(BASES_ESPECIFICAS.keys())
    curso_a_editar = st.selectbox("Seleccioná el curso que querés modificar", opciones_edicion, index=0)

    base_editable = st.session_state.bases.get(curso_a_editar, [])

    # Mostrar y editar entradas
    for i, (p, r) in enumerate(base_editable.copy()):
        col1, col2, col3 = st.columns([4, 5, 1])
        with col1:
            nuevo_p = st.text_input(f"Pregunta {i+1}", p, key=f"p_edit_{curso_a_editar}_{i}")
        with col2:
            nuevo_r = st.text_area(f"Respuesta {i+1}", r, key=f"r_edit_{curso_a_editar}_{i}")
        with col3:
            if st.button("🗑", key=f"del_edit_{curso_a_editar}_{i}"):
                try:
                    base_editable.pop(i)
                except Exception:
                    pass
                st.rerun()
        base_editable[i] = (nuevo_p, nuevo_r)

    st.markdown("---")
    nueva_p = st.text_input("➕ Nueva pregunta", key="nueva_p_edit")
    nueva_r = st.text_area("Respuesta", key="nueva_r_edit")
    if st.button("Agregar a la base"):
        if nueva_p and nueva_r:
            base_editable.append((nueva_p.strip(), nueva_r.strip()))
            st.success("Pregunta agregada correctamente.")
        else:
            st.warning("Completá pregunta y respuesta antes de agregar.")

    if st.button("Salir del modo edición"):
        st.rerun()

st.divider()

# ==============================
# ACCIONES UTILES
# ==============================
if st.button("🧹 Limpiar chat"):
    st.session_state.historial = []
    st.info("Historial limpiado correctamente.")

# ==============================
# BOTÓN DE CERRAR SESIÓN
# ==============================
st.markdown("---")
if st.button("🚪 Cerrar sesión"):
    # Limpiar todo lo relacionado al usuario
    for clave in list(st.session_state.keys()):
        if clave not in ["keepalive_thread"]:  # mantenemos el hilo de keepalive
            st.session_state.pop(clave, None)

    # Reiniciar usuario
    st.session_state.usuario = None
    st.success("Cerraste sesión correctamente.")
    st.rerun()


# ==============================
# KEEP-ALIVE
# ==============================
def mantener_sesion_viva():
    while True:
        time.sleep(300)
        st.session_state["keepalive"] = time.time()

if "keepalive_thread" not in st.session_state:
    hilo = threading.Thread(target=mantener_sesion_viva, daemon=True)
    hilo.start()
    st.session_state.keepalive_thread = True



