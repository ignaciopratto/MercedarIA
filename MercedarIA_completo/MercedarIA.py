API_USERS = "https://mi-insm.onrender.com/users"
API_TASKS = "https://mi-insm.onrender.com/tasks"
API_COURSES = "https://mi-insm.onrender.com/courses"

def api_get(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return []
# ============================================
# LOGIN POR DNI
# ============================================

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("🔐 Ingreso al sistema")
    dni_ingresado = st.text_input("Ingresá tu DNI")

    if st.button("Ingresar"):
        usuarios = api_get(API_USERS)
        encontrado = None

        for u in usuarios:
            if str(u.get("dni")).strip() == dni_ingresado.strip():
                encontrado = u
                break

        if encontrado:
            st.session_state.usuario = encontrado
            st.success(f"Bienvenido/a {encontrado['nombre']} {encontrado['apellido']} - {encontrado['curso'].upper()}")
            st.experimental_rerun()
        else:
            st.error("❌ DNI no encontrado en el sistema.")

    st.stop()  # Evita que cargue el chatbot sin login
# Datos del usuario
usuario = st.session_state.usuario
curso_usuario = usuario["curso"].lower()
dni_usuario = usuario["dni"]

# Cargar tareas
todas_las_tareas = api_get(API_TASKS)
tareas_del_curso = [t for t in todas_las_tareas if t.get("curso", "").lower() == curso_usuario]
tareas_personales = [t for t in todas_las_tareas if str(t.get("dni")) == str(dni_usuario)]

# Cargar profesores
cursos_profes = api_get(API_COURSES)
profes_del_curso = [p for p in cursos_profes if p.get("curso", "").lower() == curso_usuario]
preg = pregunta_normalizada

# ===========================
# RESPUESTAS SOBRE TAREAS
# ===========================
if "tarea" in preg or "tareas" in preg:
    respuesta = "📚 **Tareas de tu curso:**\n\n"
    
    if tareas_del_curso:
        for t in tareas_del_curso:
            respuesta += f"• **{t['titulo']}** – {t['descripcion']}\n"
    else:
        respuesta += "No hay tareas cargadas para tu curso.\n"

    respuesta += "\n🧍‍♂️ **Tus tareas personales:**\n"
    if tareas_personales:
        for t in tareas_personales:
            respuesta += f"• **{t['titulo']}** – {t['descripcion']}\n"
    else:
        respuesta += "No tenés tareas personales.\n"

    st.session_state.historial.append(("🤖 MercedarIA", respuesta))
continue

# ===========================
# RESPUESTAS SOBRE PROFESORES
# ===========================
if "profe" in preg or "profesor" in preg or "profesora" in preg or "mail" in preg:
    respuesta = "👩‍🏫 **Profesores de tu curso:**\n\n"
    if profes_del_curso:
        for p in profes_del_curso:
            respuesta += f"• **{p['materia']}**: {p['profesor_mail']}\n"
    else:
        respuesta += "No encontré profesores para tu curso."

    st.session_state.historial.append(("🤖 MercedarIA", respuesta))
    continue

