import streamlit as st
import requests
import threading
import time
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # API KEY opcional
ADMIN_PASSWORD = "mercedaria2025"

API_USERS = "https://mi-insm.onrender.com/users"
API_TASKS = "https://mi-insm.onrender.com/tasks"
API_COURSES = "https://mi-insm.onrender.com/courses"
API_FILES = "https://mi-insm.onrender.com/files"
API_EGRESADOS = "https://mi-insm.onrender.com/egresados"

# -------------------------------
# FUNCIÓN PARA USAR DEEPSEEK
# (ahora usa usuarios + cursos como contexto)
# -------------------------------
def consultar_deepseek(pregunta, api_key, contexto=""):
    if not api_key or not str(api_key).strip():
        return "No tengo respuestas locales y no hay API externa configurada."

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

        if isinstance(data, dict):
            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                choice = data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
                if "text" in choice:
                    return choice["text"]
        return "La API respondió pero no pude interpretar el resultado."
    except Exception as e:
        return f"Error consultando DeepSeek: {str(e)}"

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

# =====================================
# FUNCIÓN PARA GENERAR CONTEXTO AUTOMÁTICO
# (usa datos reales de la API)
# =====================================
def generar_contexto_con_datos(usuarios, cursos):
    texto = "BASE DE PROFESORES Y CURSOS DEL INSM:\n\n"

    texto += "=== PROFESORES ===\n"
    for u in usuarios:
        rol = (u.get("rol") or "").lower()
        if rol == "profe":
            texto += f"- Profesor: {u.get('nombre','')} {u.get('apellido','')} — Email: {u.get('email','')}\n"

    texto += "\n=== ASIGNACIONES POR CURSO ===\n"
    for c in cursos:
        texto += f"- Curso {c.get('curso_id','')}: {c.get('materia','')} — Profesor: {c.get('profesor_email','')}\n"

    return texto


# ==============================
# UTILIDADES Y FUNCIONES AUXILIARES
# ==============================
def api_get(url):
    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
    except:
        return []

def normalizar_curso(curso_raw):
    try:
        s = str(curso_raw).strip().lower()
    except:
        return ""
    if len(s) < 2:
        return ""
    numero = s[0]
    division = s[-1].upper()
    return f"{numero}° {division}"

def limpiar_estado_antes_login():
    for clave in ["usuario", "tareas_curso", "tareas_personales", "lista_tareas", "lista_cursos_api", "usuarios_api", "historial"]:
        st.session_state.pop(clave, None)

def tarea_pertenece_al_usuario(tarea, email_usuario):
    if not tarea or not isinstance(tarea, dict):
        return False

    email_user = (email_usuario or "").strip().lower()
    if not email_user:
        return False

    creador = (tarea.get("creador") or tarea.get("creator") or "").strip().lower()
    if not creador:
        return False

    if "@" not in creador:
        creador += "@insm.edu"

    return creador == email_user


def formatear_detalle_tarea(t):
    titulo = t.get("titulo") or t.get("title") or "Sin título"
    descripcion = t.get("descripcion") or t.get("description") or ""
    fecha_limite = t.get("fecha_limite") or t.get("due_date") or ""

    partes = [f"• {titulo}"]
    if descripcion:
        partes.append(f"  Descripción: {descripcion}")
    if fecha_limite:
        partes.append(f"  Fecha límite: {fecha_limite}")
    return "\n".join(partes)


def obtener_texto_tareas():
    texto = "📚 Tareas del curso:\n\n"
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
# ==============================
# FUNCIÓN PARA GENERAR CONTEXTO DE USUARIOS
# ==============================
def generar_contexto_usuarios():
    try:
        resp = requests.get(API_BASE_URL + "/users")
        if resp.status_code != 200:
            return "No se pudo obtener la lista de usuarios."

        data = resp.json()
        usuarios = data.get("usuarios", [])

        contexto = "BASE DE USUARIOS DEL COLEGIO:\n"
        for u in usuarios:
            nombre = u.get("nombre", "Desconocido")
            rol = u.get("rol", "Sin rol")
            correo = u.get("correo", "Sin correo")
            curso = u.get("curso", "Sin curso")
            contexto += f"- {nombre} | {rol} | Curso: {curso} | Email: {correo}\n"

        return contexto

    except Exception as e:
        return f"Error al generar contexto de usuarios: {e}"


# ==============================
# FUNCIÓN IA (DEEPSEEK + FALLBACK)
# ==============================
def obtener_respuesta_ia(pregunta):
    contexto_usuarios = generar_contexto_usuarios()

    prompt = f"""
Eres un asistente del Colegio Mercedario.
Usa EXCLUSIVAMENTE la siguiente base de usuarios para responder preguntas sobre profesores, cursos o contactos:

{contexto_usuarios}

Pregunta del usuario:
{pregunta}
"""

    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }

        r = requests.post("https://api.deepseek.com/chat/completions", json=body, headers=headers)

        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]

    except:
        pass

    return "⚠️ Error con IA. Intenta nuevamente."


# ==============================
# FUNCIÓN PARA ENVIAR MENSAJE
# ==============================
def enviar_mensaje(usuario, texto):
    if not texto.strip():
        return

    respuesta = obtener_respuesta_ia(texto)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    messages_db["mensajes"].append({
        "usuario": usuario["mail"],
        "mensaje": texto,
        "respuesta": respuesta,
        "timestamp": ts
    })

    guardar_db()


# ==============================
# PANTALLAS DE STREAMLIT
# ==============================
def pantalla_login():
    st.title("🔐 Login Mercedaria")
    mail = st.text_input("Correo")
    clave = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        usuario = obtener_usuario(mail)

        if usuario and usuario["password"] == clave:
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.error("Correo o contraseña incorrectos")


def pantalla_chat(usuario):
    st.title("💬 Asistente IA — Colegio Mercedario")
    st.write(f"Bienvenido **{usuario['nombre']}** ({usuario['rol']})")

    mensaje = st.text_area("Escribe tu mensaje:")

    if st.button("Enviar"):
        enviar_mensaje(usuario, mensaje)
        st.rerun()

    st.subheader("📜 Conversación")
    for m in reversed(messages_db["mensajes"]):
        st.markdown(f"**Tú:** {m['mensaje']}")
        st.markdown(f"**IA:** {m['respuesta']}")
        st.markdown("---")


def pantalla_admin():
    st.title("🛠️ Panel Admin")
    st.write("Gestión de mensajes almacenados")

    if st.button("Eliminar todos los mensajes"):
        messages_db["mensajes"] = []
        guardar_db()
        st.success("Mensajes borrados")
        st.rerun()

    st.write(messages_db)


# ==============================
# MAIN APP
# ==============================
def main():
    st.set_page_config(page_title="IA Colegio", page_icon="🎓")

    if "usuario" not in st.session_state:
        pantalla_login()
        return

    usuario = st.session_state["usuario"]

    if usuario["rol"] == "admin":
        pantalla_admin()
    else:
        pantalla_chat(usuario)


if __name__ == "__main__":
    main()
