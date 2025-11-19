# app.py
import streamlit as st
import json
import os
import requests
from datetime import datetime

# ============================================================
# CONFIG - Cambiá la DEEPSEEK_API_KEY si querés usar DeepSeek
# ============================================================
DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # <-- pegá tu clave aquí si querés usar DeepSeek; si queda vacío, se usa solo la base local
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"  # endpoint estándar (según tu ejemplo)
# Archivos locales donde persistimos las bases
F_BASE_GENERAL = "base_general.json"
F_BASES_ESPECIFICAS = "bases_especificas.json"
# ============================================================

st.set_page_config(page_title="MercedarIA (local + DeepSeek)", layout="wide")
st.title("🎓 MercedarIA — Local + DeepSeek (persistente)")

# ============================
# Helpers para archivos JSON
# ============================
def cargar_json_si_existe(ruta, default):
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    else:
        return default

def guardar_json(ruta, data):
    # guardado atómico simple (escribir en temp y renombrar)
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, ruta)

# ============================================================
# Valores por defecto (los que pasaste)
# ============================================================
DEFAULT_BASE_GENERAL = [
    ["hola", "Hola, ¿cómo estás?"],
    ["quién eres", "Soy MercedarIA, tu asistente del Colegio Mercedaria."],
    ["cómo te llamas", "Me llamo MercedarIA, tu asistente virtual."],
    ["cómo estás", "Estoy funcionando perfectamente, gracias por preguntar."],
    ["adiós", "¡Hasta luego! Que tengas un buen día."],
    ["quién es la directora", "La directora es Marisa Brizzio."],
    ["cuándo son los recreos", "Turno mañana: 8:35, 10:00, 11:35. Turno tarde: 14:40, 16:05, 17:50."],
    ["dónde queda la escuela", "En Arroyito, Córdoba, calle 9 de Julio 456."],
    ["cuándo empieza el ciclo lectivo", "El ciclo lectivo comienza el primer día hábil de marzo."],
    ["cuándo terminan las clases", "Generalmente a mediados de diciembre."]
]

DEFAULT_BASES_ESPECIFICAS = {
    "1° A": [
        ["¿Qué materias tengo?", "Biología, Educación en Artes Visuales, Lengua y Literatura, Física, Geografía, Educación Tecnológica, Matemática, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés y Educación Física."],
        ["¿Cuáles son mis contraturnos?", "Educación Física y Educación Tecnológica."],
        ["¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."]
    ],
    "1° B": [
        ["¿Qué materias tengo?", "Física, Matemática, Educación en Artes Visuales, Inglés, Educación Religiosa Escolar, Lengua y Literatura, Geografía, Ciudadanía y Participación, Educación Tecnológica, Biología y Educación Física."],
        ["¿Cuáles son mis contraturnos?", "Educación Tecnológica y Educación Física."],
        ["¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."]
    ],
    "2° A": [
        ["¿Qué materias tengo?", "Matemática, Lengua y Literatura, Educación Religiosa Escolar, Música, Historia, Educación Tecnológica, Química, Computación, Ciudadanía y Participación, Biología, Inglés y Educación Física."],
        ["¿Cuáles son mis contraturnos?", "Educación Física."],
        ["¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."]
    ],
    "2° B": [
        ["¿Qué materias tengo?", "Música, Historia, Educación Religiosa Escolar, Ciudadanía y Participación, Inglés, Matemática, Lengua y Literatura, Educación Tecnológica, Química, Biología y Educación Física."],
        ["¿Cuáles son mis contraturnos?", "Educación Física."],
        ["¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."]
    ],
    "3° A": [
        ["¿Qué materias tengo?", "Lengua y Literatura, Inglés, Historia, Geografía, Química, Educación Tecnológica, Física, Educación Religiosa Escolar, Formación para la Vida y el Trabajo, Matemática, Educación Artística Visual, Música, Computación y Educación Física."],
        ["¿Cuáles son mis contraturnos?", "Educación Física y Formación para la Vida y el Trabajo."],
        ["¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."]
    ],
    "3° B": [
        ["¿Qué materias tengo?", "Lengua y Literatura, Formación para la Vida y el Trabajo, Física, Historia, Geografía, Educación Artística Visual, Música, Matemática, Educación Tecnológica, Química, Computación, Educación Religiosa Escolar, Educación Física e Inglés."],
        ["¿Cuáles son mis contraturnos?", "Educación Física e Inglés."],
        ["¿A qué hora son los recreos?", "14:40, 16:05, 17:40 hs."]
    ],
    "4° A": [
        ["¿Qué materias tengo?", "Historia, Lengua y Literatura, Biología, ERE, Matemática, Geografía, Educ. Artística, FVT, TIC, Sociedad y Comunicación, Antropología, Educación Física e Inglés."],
        ["¿Cuáles son mis contraturnos?", "Educación Física e Inglés."],
        ["¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."]
    ],
    "4° B": [
        ["¿Qué materias tengo?", "Lengua y Literatura, Biología, ERE, Historia, Programación, Geografía, Matemática, Sistemas Digitales, FVT, Educación Artística, Educación Física e Inglés."],
        ["¿Cuáles son mis contraturnos?", "Educación Física e Inglés."],
        ["¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."]
    ],
    "5° A": [
        ["¿Qué materias tengo?", "Metodología, Historia, Física, Geografía, Arte Cultural y Social, ERE, Lengua y Literatura, FVT, Matemática, EF, Psicología, Sociología e Inglés."],
        ["¿Cuáles son mis contraturnos?", "EF, Psicología, Sociología e Inglés."],
        ["¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."]
    ],
    "5° B": [
        ["¿Qué materias tengo?", "Robótica, Música, Física, Matemática, Historia, Lengua y Literatura, FVT, Sistemas Digitales, Geografía, Psicología, EF, Desarrollo Informático e Inglés."],
        ["¿Cuáles son mis contraturnos?", "EF, Sistemas Digitales, Desarrollo Informático e Inglés."],
        ["¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."]
    ],
    "6° A": [
        ["¿Qué materias tengo?", "Ciudadanía y Política, Economía Política, Matemática, Geografía, Filosofía, Química, Lengua y Literatura, Historia, ERE, Sociedad y Comunicación, Teatro, FVT, EF e Inglés."],
        ["¿Cuáles son mis contraturnos?", "EF, Sociedad y Comunicación e Inglés."],
        ["¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."]
    ],
    "6° B": [
        ["¿Qué materias tengo?", "Lengua y Literatura, Comunicación Audiovisual, Desarrollo de Soluciones Informáticas, Informática Aplicada, Filosofía, Formación para la Vida y el Trabajo, Química, Matemática, ERE, Ciudadanía y Política, Teatro, EF, Aplicaciones Informáticas e Inglés."],
        ["¿Cuáles son mis contraturnos?", "EF, Aplicaciones Informáticas e Inglés."],
        ["¿A qué hora son los recreos?", "8:35, 10:00, 11:35 hs."]
    ]
}

# ============================================================
# CARGAR O INICIALIZAR ARCHIVOS LOCALES
# ============================================================
# base_general.json --> lista de pares [pregunta, respuesta]
base_general = cargar_json_si_existe(F_BASE_GENERAL, DEFAULT_BASE_GENERAL)
# bases_especificas.json --> mapa curso -> lista de pares
bases_especificas = cargar_json_si_existe(F_BASES_ESPECIFICAS, DEFAULT_BASES_ESPECIFICAS)

# Guardar si no existían para crear los archivos con defaults
if not os.path.exists(F_BASE_GENERAL):
    guardar_json(F_BASE_GENERAL, base_general)
if not os.path.exists(F_BASES_ESPECIFICAS):
    guardar_json(F_BASES_ESPECIFICAS, bases_especificas)

# ============================================================
# UTILIDADES
# ============================================================
def obtener_contexto(lista_pares):
    """Convierte lista de pares a texto plano para enviar como contexto a DeepSeek"""
    contexto = "BASE DE CONOCIMIENTO DEL COLEGIO:\n\n"
    for i, (p, r) in enumerate(lista_pares, 1):
        contexto += f"Pregunta {i}: {p}\nRespuesta {i}: {r}\n\n"
    return contexto

def buscar_local(pregunta, curso_seleccionado=None):
    """Busca respuesta en base_general y en la base del curso seleccionado (coincidencia exacta o parcial)."""
    q = pregunta.strip().lower()
    # Buscar exacto en general
    for p, r in base_general:
        if p.strip().lower() == q:
            return r, "local"
    # Buscar parcial en general
    for p, r in base_general:
        if p.strip().lower() in q:
            return r, "local"
    # Buscar en curso específico (si está)
    if curso_seleccionado and curso_seleccionado in bases_especificas:
        for p, r in bases_especificas[curso_seleccionado]:
            if p.strip().lower() == q:
                return r, curso_seleccionado
        for p, r in bases_especificas[curso_seleccionado]:
            if p.strip().lower() in q:
                return r, curso_seleccionado
    return None, None

def consultar_deepseek(pregunta, api_key, contexto=""):
    """Consulta DeepSeek (si api_key provista). Manejo robusto de errores."""
    if not api_key:
        return "No tengo respuesta en la base local y DeepSeek no está configurado."
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
        r = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        # Estructuras comunes
        if isinstance(data, dict):
            # camino "choices" / "message" / "content"
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                choice = choices[0]
                msg = choice.get("message") or {}
                if isinstance(msg, dict) and "content" in msg:
                    return msg["content"]
                if "text" in choice:
                    return choice["text"]
            # fallback
            if "answer" in data:
                return data["answer"]
        return "La API DeepSeek respondió, pero no pude interpretar el resultado."
    except Exception as e:
        return f"Error consultando DeepSeek: {str(e)}"

# ============================================================
# UI: Panel lateral y menú principal
# ============================================================
st.sidebar.header("Configuración")
st.sidebar.write("DeepSeek: solo se usa si pegás la API key abajo.")
api_key_input = st.sidebar.text_input("DEEPSEEK API KEY (opcional)", value=DEEPSEEK_API_KEY, type="password")
if api_key_input != DEEPSEEK_API_KEY:
    # no sobrescribimos el archivo; solo usamos lo que el usuario ponga en la sesión actual
    DEEPSEEK_API_KEY = api_key_input

st.sidebar.markdown("---")
st.sidebar.write("Persistencia en archivos locales:")
st.sidebar.write(f"- {F_BASE_GENERAL}")
st.sidebar.write(f"- {F_BASES_ESPECIFICAS}")
st.sidebar.markdown("---")
st.sidebar.write("Sugerencia: agregá esos archivos a .gitignore si no querés subirlos a GitHub.")

menu = st.sidebar.radio("Menú", ["Chat", "Editar base general", "Editar bases específicas", "Exportar / Importar"])

st.info("Este modo guarda cambios en archivos locales. Solo se conecta a DeepSeek si pegás la API key.")

# ============================================================
# CHAT
# ============================================================
if menu == "Chat":
    st.header("💬 Chat con MercedarIA (local → DeepSeek fallback)")
    curso_sel = st.selectbox("Seleccioná curso (para buscar en su base):", ["(ninguno)"] + list(bases_especificas.keys()))
    pregunta = st.text_area("Escribí tu pregunta aquí:")
    col1, col2 = st.columns([1, 1])
    with col1:
        enviar = st.button("Enviar")
    with col2:
        agregar_a_general = st.button("Agregar pregunta/respuesta a Base General (sin enviar)")
    if enviar and pregunta.strip():
        # primero buscar local
        respuesta_local, fuente = buscar_local(pregunta, curso_sel if curso_sel != "(ninguno)" else None)
        if respuesta_local:
            st.success(f"Respuesta (desde {fuente}):")
            st.write(respuesta_local)
        else:
            # usar DeepSeek con contexto generado a partir de base general + base curso
            contexto = obtener_contexto(base_general.copy())
            if curso_sel != "(ninguno)":
                contexto += "\n\n" + obtener_contexto(bases_especificas.get(curso_sel, []).copy())
            respuesta_deep = consultar_deepseek(pregunta, DEEPSEEK_API_KEY, contexto)
            st.success("Respuesta (DeepSeek):")
            st.write(respuesta_deep)
    if agregar_a_general and pregunta.strip():
        with st.form("form_agregar_general", clear_on_submit=True):
            st.write("Agregar a Base General:")
            nueva_resp = st.text_area("Respuesta para la pregunta:", value="")
            guardar = st.form_submit_button("Guardar en base_general")
            if guardar:
                base_general.append([pregunta.strip(), nueva_resp])
                guardar_json(F_BASE_GENERAL, base_general)
                st.success("Guardado en base_general.json")

# ============================================================
# EDITAR BASE GENERAL
# ============================================================
elif menu == "Editar base general":
    st.header("📝 Editar Base General")
    st.write("Editá, agregá o eliminá entradas. Los cambios se guardan automáticamente en disco.")
    # Mostrar lista con índices para edición segura
    for i, (q, r) in enumerate(list(base_general)):
        st.subheader(f"{i+1}. {q}")
        col_q, col_r, col_btn = st.columns([4,6,1])
        with col_q:
            nuevo_q = st.text_input(f"Pregunta #{i}", value=q, key=f"g_q_{i}")
        with col_r:
            nueva_r = st.text_area(f"Respuesta #{i}", value=r, key=f"g_r_{i}")
        with col_btn:
            if st.button("Eliminar", key=f"g_del_{i}"):
                base_general.pop(i)
                guardar_json(F_BASE_GENERAL, base_general)
                st.experimental_rerun()
        # guardar cambios si el usuario edita y presiona el botón guardar de cada fila
        if st.button("Guardar cambios", key=f"g_save_{i}"):
            base_general[i] = [nuevo_q.strip(), nueva_r]
            guardar_json(F_BASE_GENERAL, base_general)
            st.success("Guardado")
    # Agregar nueva entrada
    st.markdown("---")
    st.write("➕ Agregar nueva entrada a Base General")
    nueva_p = st.text_input("Nueva pregunta (general):", key="g_new_q")
    nueva_r = st.text_area("Respuesta (general):", key="g_new_r")
    if st.button("Agregar a Base General"):
        if nueva_p.strip() and nueva_r.strip():
            base_general.append([nueva_p.strip(), nueva_r.strip()])
            guardar_json(F_BASE_GENERAL, base_general)
            st.success("Agregada a base_general.json")
        else:
            st.warning("Completá pregunta y respuesta.")

# ============================================================
# EDITAR BASES ESPECIFICAS
# ============================================================
elif menu == "Editar bases específicas":
    st.header("🗂 Editar Bases Específicas por Curso")
    curso = st.selectbox("Elegí un curso:", list(bases_especificas.keys()))
    lista = bases_especificas[curso]
    # Mostrar y editar entradas
    for i, (q, r) in enumerate(list(lista)):
        st.subheader(f"{curso} — {i+1}. {q}")
        col_q, col_r, col_btn = st.columns([4,6,1])
        with col_q:
            nuevo_q = st.text_input(f"{curso}_q_{i}", value=q, key=f"{curso}_q_{i}")
        with col_r:
            nueva_r = st.text_area(f"{curso}_r_{i}", value=r, key=f"{curso}_r_{i}")
        with col_btn:
            if st.button("Eliminar", key=f"{curso}_del_{i}"):
                lista.pop(i)
                bases_especificas[curso] = lista
                guardar_json(F_BASES_ESPECIFICAS, bases_especificas)
                st.experimental_rerun()
        if st.button("Guardar cambios", key=f"{curso}_save_{i}"):
            lista[i] = [nuevo_q.strip(), nueva_r]
            bases_especificas[curso] = lista
            guardar_json(F_BASES_ESPECIFICAS, bases_especificas)
            st.success("Guardado")
    # Agregar nueva entrada
    st.markdown("---")
    st.write(f"➕ Agregar entrada a {curso}")
    npreg = st.text_input("Nueva pregunta:", key=f"nq_{curso}")
    nres = st.text_area("Nueva respuesta:", key=f"nr_{curso}")
    if st.button("Agregar a la base específica"):
        if npreg.strip() and nres.strip():
            lista.append([npreg.strip(), nres.strip()])
            bases_especificas[curso] = lista
            guardar_json(F_BASES_ESPECIFICAS, bases_especificas)
            st.success("Agregado correctamente")
        else:
            st.warning("Completá ambos campos.")

# ============================================================
# EXPORTAR / IMPORTAR
# ============================================================
elif menu == "Exportar / Importar":
    st.header("📤 Exportar / Importar bases")
    st.write("Podés descargar las bases actuales o cargar un archivo JSON con el mismo formato.")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Descargar base_general.json", data=json.dumps(base_general, ensure_ascii=False, indent=2), file_name="base_general.json", mime="application/json")
        st.download_button("Descargar bases_especificas.json", data=json.dumps(bases_especificas, ensure_ascii=False, indent=2), file_name="bases_especificas.json", mime="application/json")
    with col2:
        uploaded = st.file_uploader("Subir bases_especificas.json (reemplaza)", type=["json"])
        if uploaded is not None:
            try:
                new = json.load(uploaded)
                if isinstance(new, dict):
                    bases_especificas = new
                    guardar_json(F_BASES_ESPECIFICAS, bases_especificas)
                    st.success("bases_especificas.json importado y guardado.")
                else:
                    st.error("Formato inválido: se esperaba un objeto/dict.")
            except Exception as e:
                st.error(f"Error importando: {e}")
        uploaded2 = st.file_uploader("Subir base_general.json (reemplaza)", type=["json"], key="u2")
        if uploaded2 is not None:
            try:
                new2 = json.load(uploaded2)
                if isinstance(new2, list):
                    base_general = new2
                    guardar_json(F_BASE_GENERAL, base_general)
                    st.success("base_general.json importado y guardado.")
                else:
                    st.error("Formato inválido: se esperaba una lista de pares.")
            except Exception as e:
                st.error(f"Error importando: {e}")

# ============================================================
# PIE: acciones útiles
# ============================================================
st.sidebar.markdown("---")
if st.sidebar.button("Restaurar valores por defecto (sobrescribe archivos)"):
    guardar_json(F_BASE_GENERAL, DEFAULT_BASE_GENERAL)
    guardar_json(F_BASES_ESPECIFICAS, DEFAULT_BASES_ESPECIFICAS)
    st.experimental_rerun()

st.sidebar.markdown(" ")
st.sidebar.write(f"Última carga: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
