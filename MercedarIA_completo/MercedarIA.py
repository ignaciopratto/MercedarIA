import requests
from datetime import datetime
import streamlit as st
from typing import List, Tuple, Optional
import time

# ==============================
# CONFIGURACIÓN Y CONSTANTES
# ==============================

DEEPSEEK_API_KEY = "sk-f3e25c8aa4604877bc9238eca28e5e0e"  # Dejalo vacío o configurá tu API key aquí

# Configuración de colores (paleta educativa vibrante)
COLORES = {
    "primario": "#FF6B6B",      # Coral energético
    "secundario": "#4ECDC4",    # Turquesa motivador
    "acento": "#FFE66D",        # Amarillo brillante
    "exito": "#95E1D3",         # Verde menta
    "texto": "#2C3E50",         # Azul oscuro para texto
    "fondo": "#F8F9FA"          # Gris muy claro
}

# ==============================
# BASE DE CONOCIMIENTO INTEGRADA
# ==============================

# Base de datos inicial del colegio
BASE_CONOCIMIENTO_INICIAL = [
    ("¿Cuál es el horario de entrada?", "El horario de ingreso al colegio es a las 7:45 hs. Las clases comienzan puntualmente a las 8:00 hs. Se recomienda llegar con 10 minutos de anticipación."),
    ("¿Cuál es el horario de salida?", "El horario de salida varía según el nivel: Nivel Inicial sale a las 12:00 hs, Primaria a las 12:30 hs y Secundaria a las 13:00 hs. Los días de educación física pueden extenderse hasta las 14:00 hs."),
    ("¿Cómo me inscribo a las actividades extracurriculares?", "Las inscripciones a actividades extracurriculares se realizan durante las primeras dos semanas de marzo. Podés acercarte a la secretaría con la autorización de tus padres o completar el formulario online en nuestra página web."),
    ("¿Qué actividades extracurriculares hay disponibles?", "Ofrecemos diversas actividades: deportes (fútbol, hockey, básquet, vóley), artísticas (teatro, música, danza), tecnología (robótica, programación) y apoyo académico (talleres de matemática, lengua e idiomas). Todas se dictan en contraturno."),
    ("¿Cuándo son las reuniones de padres?", "Las reuniones generales de padres se realizan trimestralmente: en marzo (presentación del año), junio (primer balance), septiembre (avances) y noviembre (cierre del año). También hay entrevistas individuales con previa cita."),
    ("¿Cómo puedo justificar una inasistencia?", "Las inasistencias deben justificarse dentro de las 48 horas mediante: nota firmada por el padre/madre/tutor, certificado médico (para ausencias por enfermedad), o a través del sistema online en la plataforma del colegio con tu usuario y contraseña."),
    ("¿Qué documentación necesito para matricular?", "Para la matrícula necesitás: DNI del alumno y los padres/tutores, certificado de salud actualizado, constancia de vacunación al día, partida de nacimiento original, foto carnet, boletín del año anterior (si corresponde) y comprobante de domicilio."),
    ("¿Hay servicio de comedor?", "Sí, contamos con servicio de comedor con menús balanceados elaborados por nutricionistas. Hay opciones normales, vegetarianas y para celíacos. El servicio debe contratarse mensualmente en la secretaría administrativa."),
    ("¿Cómo accedo a la plataforma virtual?", "El usuario y contraseña se entregan en secretaría al momento de la matrícula. Ingresás a www.colegiomercedaria.edu.ar/campus con tus credenciales. Si olvidaste tu contraseña, podés recuperarla con tu email registrado o solicitando reset en secretaría."),
    ("¿Qué pasa si pierdo el cuaderno de comunicaciones?", "En caso de pérdida o extravío, debés solicitar un duplicado en la librería del colegio dentro de los 3 días hábiles. Tiene un costo de $2000 y es indispensable para la comunicación oficial entre el colegio y la familia."),
    ("¿Hay transporte escolar?", "El colegio no brinda transporte propio, pero tenemos convenios con 5 empresas de transporte escolar habilitadas. Los datos de contacto y recorridos están disponibles en secretaría y en nuestra página web en la sección 'Servicios'."),
    ("¿Cuándo son las vacaciones de invierno?", "Las vacaciones de invierno siguen el calendario escolar oficial de la provincia. Generalmente son dos semanas completas durante julio. El receso 2024 será del 15 al 26 de julio inclusive. La fecha exacta se confirma en febrero."),
    ("¿Dónde puedo consultar las calificaciones?", "Las calificaciones están disponibles en la plataforma virtual del colegio. Se actualizan semanalmente y podés ver notas, asistencias y observaciones. Los boletines oficiales se entregan trimestralmente en formato impreso y digital."),
    ("¿Qué hago si mi hijo/a se enferma en el colegio?", "Ante cualquier malestar, el alumno es atendido en enfermería. Si es necesario, se comunica inmediatamente a los padres/tutores al número registrado. Es fundamental mantener actualizado el contacto de emergencia y la ficha médica."),
    ("¿Hay gabinete psicopedagógico?", "Sí, contamos con un equipo psicopedagógico conformado por psicólogos, psicopedagogos y trabajadores sociales. Atienden de lunes a viernes de 8:00 a 16:00 hs. Para solicitar entrevista, comunicarse al interno 123 o por email a gabinete@colegiomercedaria.edu.ar"),
]

# ==============================
# ESTILOS CSS PERSONALIZADOS
# ==============================

def aplicar_estilos():
    """Aplica estilos CSS personalizados para una interfaz moderna y educativa."""
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        * {{
            font-family: 'Poppins', sans-serif;
        }}
        
        .stApp {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .main .block-container {{
            padding: 2rem 3rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            max-width: 1200px;
        }}
        
        h1 {{
            color: {COLORES['primario']};
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5rem;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        
        h2 {{
            color: {COLORES['secundario']};
            font-weight: 600;
            margin-top: 1.5rem;
        }}
        
        h3 {{
            color: {COLORES['texto']};
            font-weight: 500;
        }}
        
        .subtitle {{
            text-align: center;
            color: #7F8C8D;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            font-weight: 300;
        }}
        
        .chat-message {{
            padding: 1rem;
            border-radius: 15px;
            margin: 0.8rem 0;
            animation: fadeIn 0.3s ease-in;
        }}
        
        .user-message {{
            background: linear-gradient(135deg, {COLORES['secundario']} 0%, #3DBDAF 100%);
            color: white;
            margin-left: 20%;
            box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);
        }}
        
        .bot-message {{
            background: linear-gradient(135deg, {COLORES['primario']} 0%, #FF5252 100%);
            color: white;
            margin-right: 20%;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {COLORES['primario']} 0%, #FF5252 100%);
            color: white;
            border: none;
            padding: 0.6rem 2rem;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
        }}
        
        .stTextInput > div > div > input {{
            border-radius: 15px;
            border: 2px solid {COLORES['secundario']};
            padding: 0.8rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLORES['primario']};
            box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
        }}
        
        .info-card {{
            background: linear-gradient(135deg, {COLORES['exito']} 0%, #7FE4D8 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(149, 225, 211, 0.3);
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 0.2rem;
        }}
        
        .badge-local {{
            background: {COLORES['acento']};
            color: {COLORES['texto']};
        }}
        
        .badge-ia {{
            background: {COLORES['secundario']};
            color: white;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2rem;
            background-color: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent;
            border-radius: 10px 10px 0 0;
            padding: 1rem 2rem;
            font-weight: 600;
            font-size: 1.1rem;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {COLORES['primario']} 0%, #FF5252 100%);
            color: white;
        }}
        
        .streamlit-expanderHeader {{
            background: linear-gradient(135deg, {COLORES['acento']} 0%, #FFD93D 100%);
            border-radius: 10px;
            font-weight: 600;
            color: {COLORES['texto']};
        }}
        
        .datetime-display {{
            text-align: center;
            color: #95A5A6;
            font-size: 0.9rem;
            padding: 1rem;
            background: {COLORES['fondo']};
            border-radius: 10px;
            margin-top: 1rem;
        }}
        
        hr {{
            margin: 2rem 0;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, {COLORES['secundario']}, transparent);
        }}
        
        .stTextArea textarea {{
            border-radius: 15px;
            border: 2px solid {COLORES['secundario']};
            padding: 0.8rem;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==============================
# FUNCIONES DE GESTIÓN DE DATOS
# ==============================

def inicializar_base_datos():
    """Inicializa la base de datos en session_state si no existe."""
    if "base_conocimiento" not in st.session_state:
        st.session_state.base_conocimiento = list(BASE_CONOCIMIENTO_INICIAL)

def buscar_respuesta_local(consulta: str) -> Optional[str]:
    """
    Busca una respuesta en la base de conocimiento integrada.
    
    Args:
        consulta: Pregunta del usuario
        
    Returns:
        Respuesta encontrada o None
    """
    consulta_normalizada = consulta.lower().strip()
    
    for pregunta, respuesta in st.session_state.base_conocimiento:
        pregunta_normalizada = pregunta.lower().strip()
        
        # Búsqueda flexible: si la consulta contiene palabras clave de la pregunta
        palabras_consulta = set(consulta_normalizada.split())
        palabras_pregunta = set(pregunta_normalizada.split())
        
        if palabras_consulta & palabras_pregunta:  # Si hay intersección
            return respuesta
    
    return None

def generar_contexto() -> str:
    """
    Genera un contexto formateado con todas las preguntas y respuestas.
    
    Returns:
        String con el contexto formateado
    """
    contexto = "📚 BASE DE CONOCIMIENTO DEL COLEGIO MERCEDARIA:\n\n"
    
    for i, (pregunta, respuesta) in enumerate(st.session_state.base_conocimiento, 1):
        contexto += f"Q{i}: {pregunta}\n"
        contexto += f"A{i}: {respuesta}\n\n"
    
    return contexto

def consultar_ia(pregunta: str, api_key: str, contexto: str = "") -> str:
    """
    Consulta la API de DeepSeek para obtener una respuesta inteligente.
    
    Args:
        pregunta: Consulta del usuario
        api_key: Clave de API de DeepSeek
        contexto: Contexto adicional de la base de conocimiento
        
    Returns:
        Respuesta generada por la IA o mensaje de error
    """
    if not api_key or api_key.strip() == "":
        return "⚠️ Para usar la IA, configurá tu clave API en la variable DEEPSEEK_API_KEY del código."
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt_sistema = """Sos el asistente educativo oficial del Colegio Mercedaria. 
    
Tu misión es ayudar a estudiantes, docentes y familias con información clara, precisa y motivadora.

DIRECTRICES:
- Usá la base de conocimiento local como fuente principal
- Si la respuesta no está en la base, usá tu conocimiento general educativo
- Sé amable, empático y profesional
- Respuestas concisas pero completas (máximo 3-4 párrafos)
- Usá un lenguaje accesible pero formal
- Incluí emojis educativos ocasionalmente para hacer la comunicación más cálida
- Si no sabés algo, admitilo con honestidad y sugerí cómo pueden obtener la información"""

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"{contexto}\n\nConsulta del usuario: {pregunta}"}
        ],
        "max_tokens": 600,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        resultado = response.json()
        return resultado["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⏱️ La consulta tardó demasiado. Por favor, intentá nuevamente."
    except requests.exceptions.RequestException as e:
        return f"❌ Error de conexión con la IA: {str(e)}"
    except Exception as e:
        return f"❌ Error inesperado: {str(e)}"

def obtener_fecha_hora_formateada() -> str:
    """Retorna la fecha y hora actual en formato legible en español."""
    dias = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    meses = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril',
        'May': 'mayo', 'June': 'junio', 'July': 'julio', 'August': 'agosto',
        'September': 'septiembre', 'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    
    ahora = datetime.now()
    dia_semana = dias[ahora.strftime('%A')]
    mes = meses[ahora.strftime('%B')]
    
    return f"📅 {dia_semana} {ahora.day} de {mes} de {ahora.year} • 🕐 {ahora.strftime('%H:%M')}"

# ==============================
# INTERFAZ PRINCIPAL
# ==============================

def main():
    """Función principal que configura y ejecuta la aplicación."""
    
    # Configuración de página
    st.set_page_config(
        page_title="MercedarIA - Asistente Educativo",
        page_icon="🎓",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Inicializar base de datos
    inicializar_base_datos()
    
    # Aplicar estilos
    aplicar_estilos()
    
    # Cabecera principal
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1>🎓 MercedarIA</h1>
            <p class='subtitle'>Tu asistente educativo inteligente del Colegio Mercedaria</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs principales
    tab_chat, tab_editor, tab_info = st.tabs([
        "💬 Asistente Virtual",
        "📝 Gestión de Conocimiento",
        "ℹ️ Información"
    ])
    
    # =====================================
    # TAB 1: ASISTENTE VIRTUAL
    # =====================================
    with tab_chat:
        st.markdown("### 🤖 Conversá con el asistente")
        st.markdown("*Hacé tus preguntas sobre el colegio, actividades, horarios y más.*")
        
        # Estado del historial
        if "historial_chat" not in st.session_state:
            st.session_state.historial_chat = []
            mensaje_bienvenida = """¡Hola! 👋 Soy MercedarIA, tu asistente virtual del Colegio Mercedaria.

Estoy aquí para ayudarte con información sobre:
✅ Horarios y calendario escolar
✅ Actividades y eventos
✅ Procedimientos administrativos
✅ Información académica
✅ Y mucho más

¿En qué puedo ayudarte hoy?"""
            st.session_state.historial_chat.append(("bot", mensaje_bienvenida))
        
        # Input del usuario
        col1, col2 = st.columns([5, 1])
        with col1:
            consulta_usuario = st.text_input(
                "Escribí tu pregunta:",
                placeholder="Ejemplo: ¿Cuáles son los horarios de entrada?",
                label_visibility="collapsed",
                key="input_chat"
            )
        with col2:
            enviar = st.button("📤 Enviar", use_container_width=True)
        
        # Procesar consulta
        if enviar and consulta_usuario.strip():
            # Agregar mensaje del usuario
            st.session_state.historial_chat.append(("usuario", consulta_usuario))
            
            # Buscar respuesta local primero
            respuesta_local = buscar_respuesta_local(consulta_usuario)
            
            if respuesta_local:
                respuesta_final = f"{respuesta_local}\n\n<span class='badge badge-local'>📚 Respuesta de base local</span>"
                st.session_state.historial_chat.append(("bot", respuesta_final))
            else:
                # Consultar IA
                with st.spinner("🤔 Analizando tu consulta..."):
                    time.sleep(0.5)
                    contexto = generar_contexto()
                    respuesta_ia = consultar_ia(consulta_usuario, DEEPSEEK_API_KEY, contexto)
                    respuesta_final = f"{respuesta_ia}\n\n<span class='badge badge-ia'>🤖 Respuesta generada por IA</span>"
                    st.session_state.historial_chat.append(("bot", respuesta_final))
            
            st.rerun()
        
        # Mostrar historial
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        for rol, mensaje in st.session_state.historial_chat:
            if rol == "usuario":
                st.markdown(f"""
                    <div class='chat-message user-message'>
                        <strong>👤 Tú:</strong><br>{mensaje}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='chat-message bot-message'>
                        <strong>🎓 MercedarIA:</strong><br>{mensaje}
                    </div>
                """, unsafe_allow_html=True)
        
        # Botones de acción
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpiar conversación"):
                st.session_state.historial_chat = []
                st.rerun()
        with col2:
            if st.button("💡 Ver ejemplos"):
                st.info("""
**Ejemplos de preguntas que podés hacer:**
- ¿Cuál es el horario de entrada?
- ¿Cómo me inscribo a las actividades extracurriculares?
- ¿Cuándo son las próximas reuniones de padres?
- ¿Qué documentación necesito para matricular?
                """)
        
        # Fecha y hora
        st.markdown(f"""
            <div class='datetime-display'>
                {obtener_fecha_hora_formateada()}
            </div>
        """, unsafe_allow_html=True)
    
    # =====================================
    # TAB 2: GESTIÓN DE CONOCIMIENTO
    # =====================================
    with tab_editor:
        st.markdown("### 📝 Administrador de Base de Conocimiento")
        st.markdown("*Gestioná las preguntas y respuestas que el asistente puede responder automáticamente.*")
        
        # Estadísticas
        total_items = len(st.session_state.base_conocimiento)
        st.markdown(f"""
            <div class='info-card'>
                <h4 style='margin:0; color: #2C3E50;'>📊 Estadísticas de la Base</h4>
                <p style='font-size: 2rem; font-weight: 700; margin: 0.5rem 0; color: {COLORES['primario']};'>
                    {total_items}
                </p>
                <p style='margin:0; color: #7F8C8D;'>preguntas/respuestas almacenadas</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sección: Agregar nueva pregunta
        st.markdown("#### ➕ Agregar Nueva Entrada")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            nueva_pregunta = st.text_input("🔹 Pregunta:", placeholder="Ej: ¿Cuál es el horario?", key="nueva_preg")
        with col2:
            nueva_respuesta = st.text_area("🔹 Respuesta:", placeholder="Detallá la respuesta completa aquí...", height=100, key="nueva_resp")
        
        if st.button("💾 Guardar Nueva Entrada", use_container_width=True):
            if nueva_pregunta.strip() and nueva_respuesta.strip():
                st.session_state.base_conocimiento.append((nueva_pregunta.strip(), nueva_respuesta.strip()))
                st.success("✅ ¡Entrada agregada exitosamente!")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("⚠️ Por favor, completá ambos campos antes de guardar.")
        
        st.markdown("---")
        
        # Sección: Ver y editar entradas existentes
        st.markdown("#### 📋 Entradas Actuales")
        
        if not st.session_state.base_conocimiento:
            st.info("🔍 No hay entradas en la base de conocimiento todavía. ¡Agregá la primera!")
        else:
            for i, (preg, resp) in enumerate(st.session_state.base_conocimiento):
                with st.expander(f"**{i+1}.** {preg[:60]}{'...' if len(preg) > 60 else ''}"):
                    st.markdown(f"**📝 Pregunta completa:**")
                    st.info(preg)
                    st.markdown(f"**💬 Respuesta:**")
                    st.info(resp)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"✏️ Editar", key=f"edit_btn_{i}"):
                            st.session_state[f"editando_{i}"] = True
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🗑️ Eliminar", key=f"del_btn_{i}"):
                            st.session_state.base_conocimiento.pop(i)
                            st.success("✅ Entrada eliminada")
                            time.sleep(0.5)
                            st.rerun()
                    
                    with col3:
                        if st.button(f"⬆️ Subir", key=f"up_btn_{i}", disabled=(i==0)):
                            # Intercambiar con el elemento anterior
                            st.session_state.base_conocimiento[i], st.session_state.base_conocimiento[i-1] = \
                                st.session_state.base_conocimiento[i-1], st.session_state.base_conocimiento[i]
                            st.rerun()
                    
                    # Modo edición
                    if st.session_state.get(f"editando_{i}", False):
                        st.markdown("---")
                        st.markdown("**Editar esta entrada:**")
                        nueva_p = st.text_input("Modificar pregunta:", preg, key=f"edit_p_{i}")
                        nueva_r = st.text_area("Modificar respuesta:", resp, height=120, key=f"edit_r_{i}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Guardar cambios", key=f"save_{i}"):
                                st.session_state.base_conocimiento[i] = (nueva_p, nueva_r)
                                st.session_state[f"editando_{i}"] = False
                                st.success("✅ Cambios guardados")
                                time.sleep(0.5)
                                st.rerun()
                        with col2:
                            if st.button("❌ Cancelar", key=f"cancel_{i}"):
                                st.session_state[f"editando_{i}"] = False
                                st.rerun()
        
        st.markdown("---")
        
        # Botón de reseteo
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Restaurar Base Original", use_container_width=True):
                st.session_state.base_conocimiento = list(BASE_CONOCIMIENTO_INICIAL)
                st.success("✅ Base de conocimiento restaurada a valores iniciales")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("🗑️ Borrar Toda la Base", use_container_width=True):
                if st.session_state.get("confirmar_borrado", False):
                    st.session_state.base_conocimiento = []
                    st.session_state.confirmar_borrado = False
                    st.success("✅ Base de conocimiento vaciada")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.confirmar_borrado = True
                    st.warning("⚠️ Hacé clic nuevamente para confirmar")
    
    # =====================================
    # TAB 3: INFORMACIÓN
    # =====================================
    with tab_info:
        st.markdown("### ℹ️ Acerca de MercedarIA")
        
        st.markdown(f"""
            <div class='info-card'>
                <h4 style='color: {COLORES['texto']};'>🎯 Misión del Proyecto</h4>
                <p style='color: {COLORES['texto']};'>
                    MercedarIA es un asistente virtual educativo diseñado para facilitar 
                    el acceso a información del Colegio Mercedaria de manera rápida, 
                    intuitiva y amigable. Toda la información se gestiona directamente 
                    desde la aplicación, sin necesidad de archivos externos.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🛠️ Características Principales")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                **💡 Respuestas Inteligentes**
                - Base de conocimiento integrada
                - Integración con IA avanzada (opcional)
                - Respuestas contextualizadas
                - Búsqueda flexible por palabras clave
            """)
        with col2:
            st.markdown("""
                **⚙️ Gestión Flexible**
                - Editor visual incorporado
                - Agregar, editar y eliminar entradas
                - Reordenar preguntas
                - Restaurar base original
            """)
        
        st.markdown("---")
        
        st.markdown("#### 🔧 Configuración Técnica")
        
        st.code(f"""
# Base de datos almacenada en memoria (session_state)
Total de entradas actuales: {len(st.session_state.base_conocimiento)}

# API de IA configurada: {'✅ Sí' if DEEPSEEK_API_KEY else '❌ No'}

# Modo de almacenamiento: En memoria de la sesión
# Los cambios persisten mientras la aplicación esté abierta
        """, language="python")
        
        st.markdown("---")
        
        st.markdown("#### 📚 Guía Rápida de Uso")
        
        with st.expander("👤 Para Usuarios (Estudiantes/Familias)"):
            st.markdown("""
                1. Ingresá a la pestaña **"💬 Asistente Virtual"**
                2. Escribí tu pregunta en el campo de texto
                3. Hacé clic en **"📤 Enviar"** o presioná Enter
                4. Recibí tu respuesta instantánea (primero busca en la base local)
                5. Si no hay respuesta local, el sistema puede usar IA (si está configurada)
                6. Podés seguir preguntando o limpiar la conversación cuando quieras
            """)
        
        with st.expander("👨‍💼 Para Administradores (Docentes/Staff)"):
            st.markdown("""
                **Agregar nueva información:**
                1. Accedé a **"📝 Gestión de Conocimiento"**
                2. En la sección "➕ Agregar Nueva Entrada"
                3. Completá pregunta y respuesta
                4. Hacé clic en "💾 Guardar Nueva Entrada"
                
                **Editar información existente:**
                1. Expandí la entrada que querés modificar
                2. Hacé clic en "✏️ Editar"
                3. Modificá el contenido
                4. Guardá los cambios
                
                **Eliminar información:**
                1. Expandí la entrada
                2. Hacé clic en "🗑️ Eliminar"
                3. La entrada se elimina inmediatamente
                
                **Reordenar:**
                - Usá el botón "⬆️ Subir" para mover entradas hacia arriba
                
                **Restaurar:**
                - "🔄 Restaurar Base Original" recupera la base inicial
                - "🗑️ Borrar Toda la Base" vacía completamente la base (requiere confirmación)
            """)
        
        st.markdown("---")
        
        st.markdown("#### 🎨 Paleta de Colores del Proyecto")
        
        cols = st.columns(5)
        colores_info = [
            ("Primario", COLORES['primario'], "🔴"),
            ("Secundario", COLORES['secundario'], "🔵"),
            ("Acento", COLORES['acento'], "💛"),
            ("Éxito", COLORES['exito'], "💚"),
            ("Texto", COLORES['texto'], "⚫")
        ]
        
        for col, (nombre, color, emoji) in zip(cols, colores_info):
            with col:
                st.markdown(f"""
                    <div style='text-align: center; padding: 1rem;'>
                        <div style='background: {color}; height: 60px; border-radius: 10px; margin-bottom: 0.5rem; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'></div>
                        <p style='margin: 0; font-size: 0.85rem; font-weight: 600;'>{emoji} {nombre}</p>
                        <code style='font-size: 0.75rem;'>{color}</code>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("#### 💡 Consejos de Uso")
        
        st.markdown("""
            <div style='background: #E8F4F8; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #4ECDC4;'>
                <ul style='margin: 0;'>
                    <li><strong>Búsqueda inteligente:</strong> El sistema busca por palabras clave, no necesita coincidencia exacta</li>
                    <li><strong>Respuestas claras:</strong> Escribí respuestas completas y detalladas para mejor experiencia</li>
                    <li><strong>Organización:</strong> Reordená las preguntas más frecuentes al principio</li>
                    <li><strong>Actualización regular:</strong> Mantené la base actualizada con información reciente</li>
                    <li><strong>API opcional:</strong> La IA es complementaria, la base local es la fuente principal</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("#### 🚀 Próximas Mejoras Planificadas")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                **Funcionalidades:**
                - 📊 Estadísticas de consultas más frecuentes
                - 🔍 Búsqueda y filtrado avanzado
                - 📁 Exportar/Importar base de datos
                - 🏷️ Categorías y etiquetas para preguntas
            """)
        with col2:
            st.markdown("""
                **Mejoras técnicas:**
                - 💾 Persistencia en base de datos real
                - 👥 Sistema multiusuario con roles
                - 📱 Versión móvil optimizada
                - 🌐 API REST para integraciones
            """)
        
        st.markdown("---")
        
        st.markdown("#### ⚙️ Configuración de API (Opcional)")
        
        st.markdown("""
            Si querés habilitar las respuestas con IA, necesitás una clave API de DeepSeek:
            
            1. **Obtener API Key:**
               - Visitá: [https://platform.deepseek.com](https://platform.deepseek.com)
               - Creá una cuenta gratuita
               - Generá tu API Key en la sección de configuración
            
            2. **Configurar en el código:**
               - Abrí el archivo `MercedarIA.py`
               - Buscá la línea: `DEEPSEEK_API_KEY = ""`
               - Reemplazá con tu clave: `DEEPSEEK_API_KEY = "tu_clave_aqui"`
            
            3. **Funcionamiento:**
               - Primero busca en la base local
               - Si no encuentra respuesta, consulta a la IA
               - La IA usa el contexto de tu base para respuestas coherentes
        """)
        
        st.markdown("---")
        
        st.markdown("#### ❓ Preguntas Frecuentes")
        
        with st.expander("¿Los cambios se guardan permanentemente?"):
            st.markdown("""
                Los cambios se mantienen **mientras la aplicación esté abierta** en tu navegador.
                Si cerrás la pestaña o reiniciás la aplicación, la base vuelve a su estado inicial.
                
                Para persistencia permanente, podés usar el botón de exportar (próximamente) o 
                modificar directamente la variable `BASE_CONOCIMIENTO_INICIAL` en el código.
            """)
        
        with st.expander("¿Cómo funciona la búsqueda?"):
            st.markdown("""
                El sistema compara las palabras de tu consulta con las palabras de cada pregunta
                en la base. No necesita coincidencia exacta, busca palabras en común.
                
                **Ejemplo:**
                - Pregunta guardada: "¿Cuál es el horario de entrada?"
                - Tu consulta: "horario entrada" → ✅ Encuentra la respuesta
                - Tu consulta: "cuando empiezan las clases" → ❌ No encuentra (diferentes palabras)
            """)
        
        with st.expander("¿Puedo usar esto sin Internet?"):
            st.markdown("""
                **Sí**, la funcionalidad principal funciona sin Internet:
                - ✅ Chat con base local
                - ✅ Agregar, editar y eliminar preguntas
                - ✅ Toda la gestión de la base de datos
                
                **No** funcionará sin Internet:
                - ❌ Respuestas con IA (requiere conexión a DeepSeek API)
            """)
        
        st.markdown("---")
        
        # Footer con información del proyecto
        st.markdown(f"""
            <div style='text-align: center; padding: 2rem 0; color: #95A5A6;'>
                <p style='margin: 0.5rem 0;'>
                    <strong style='color: {COLORES['primario']};'>🎓 Colegio Mercedaria</strong>
                </p>
                <p style='margin: 0.5rem 0; font-size: 0.9rem;'>
                    Sistema de Asistencia Virtual Educativa
                </p>
                <p style='margin: 1rem 0; font-size: 0.85rem;'>
                    Desarrollado con ❤️ usando Streamlit + Python + IA
                </p>
                <p style='margin: 0.5rem 0; font-size: 0.85rem;'>
                    📊 Base de datos: <strong>{len(st.session_state.base_conocimiento)} entradas activas</strong>
                </p>
                <p style='margin: 0; font-size: 0.8rem;'>
                    © 2024 - Innovación Educativa
                </p>
            </div>
        """, unsafe_allow_html=True)


# ==============================
# PUNTO DE ENTRADA
# ==============================

if __name__ == "__main__":
    main()
