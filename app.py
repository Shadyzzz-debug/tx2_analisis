import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator
from textblob import TextBlob # Nuevo Import

# Inicializar servicios globales
translator = Translator()

# Inicializar sesión de estado para almacenar el texto reconocido
if 'recognized_text' not in st.session_state:
    st.session_state.recognized_text = ""

# --- Funciones de Utilidad (TTS y Limpieza) ---

def text_to_speech(input_language, output_language, text, tld):
    """Traduce y convierte el texto a audio, guardando el archivo temporalmente.
       Utiliza el objeto 'translator' global."""
    if not text.strip():
        return None, "Error: Texto vacío para traducir."
        
    try:
        # Usa el traductor global
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        
        # gTTS utiliza el idioma de salida, pero el tld es para el acento
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        
        # Crear un nombre de archivo seguro
        safe_name = "".join(c for c in text[0:20] if c.isalnum() or c.isspace()).replace(" ", "_").lower()
        if not safe_name: safe_name = "audio_conjuro"
        file_path = f"temp/{safe_name}.mp3"
        
        # Asegurarse de que el directorio temp existe
        os.makedirs("temp", exist_ok=True)
        tts.save(file_path)
        
        return file_path, trans_text
    except Exception as e:
        # Aquí se muestra el error en la interfaz
        st.error(f"Fallo en la traducción o conversión: {e}")
        return None, f"Error en la operación: {e}"

def remove_files(n):
    """Elimina archivos MP3 antiguos para mantener limpio el sistema."""
    mp3_files = glob.glob("temp/*mp3")
    now = time.time()
    n_days = n * 86400
    for f in mp3_files:
        try:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
        except Exception:
            pass

# Limpieza inicial de archivos antiguos
remove_files(7)

# --- 1. Configuración de la Página y Estilo Gótico (CSS Injection) ---
st.set_page_config(
    page_title="El Códice de la Visión",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Paleta Gótica (Estilo Bloodborne):
# Fondo: #0A0A0A (Negro profundo)
# Texto Principal: #F5F5DC (Hueso/Papiro)
# Acento/Sangre: #8B0000 (Rojo intenso)
# Metal/Piedra: #6B5B3E (Bronce oscuro/Caoba)

gothic_css = """
<style>
/* Fondo general y fuente serif dramática */
body {
    background-color: #0A0A0A;
    color: #F5F5DC;
    font-family: 'Georgia', serif;
}
.stApp {
    background-color: #0A0A0A;
    color: #F5F5DC;
}

/* Título Principal (h1): Cincelado, Dramático y GRANDE */
h1 {
    color: #8B0000; /* Rojo sangre */
    text-shadow: 3px 3px 8px #000000;
    font-size: 3.5em; /* Aumentado */
    border-bottom: 7px double #6B5B3E; /* Borde más grueso */
    padding-bottom: 15px;
    margin-bottom: 40px;
    text-align: center;
    letter-spacing: 3px; /* Más espaciado */
}

/* Subtítulos (h2, h3): Menos prominentes, color de metal */
h2, h3 {
    color: #D4D4D4;
    font-family: 'Georgia', serif;
    letter-spacing: 1px;
}

/* Sidebar: Fondo de cámara oscura con bordes intrincados */
[data-testid="stSidebar"] {
    background-color: #1A1A1A;
    color: #F5F5DC;
    border-right: 3px solid #6B5B3E;
    box-shadow: 0 0 15px rgba(107, 91, 62, 0.5), inset 0 0 5px rgba(0, 0, 0, 0.8);
}

/* Etiquetas de radio y selectbox en sidebar */
.stRadio label, .stSelectbox label {
    font-size: 1.1em;
    font-weight: bold;
    color: #F5F5DC;
}

/* Botones (Sellar, Convertir): Botones tipo Relicario */
.stButton > button {
    background-color: #444444; /* Base metálica */
    color: #F5F5DC;
    border: 3px solid #8B0000; /* Borde rojo sangre */
    border-radius: 8px;
    padding: 12px 25px;
    font-weight: bold;
    box-shadow: 6px 6px 10px #000000, inset 0 0 10px rgba(255, 255, 255, 0.1);
    transition: background-color 0.3s, box-shadow 0.3s, transform 0.1s;
}

.stButton > button:hover {
    background-color: #8B0000; /* Hover a rojo intenso */
    color: white;
    box-shadow: 8px 8px 15px #000000;
    transform: translateY(-2px);
}

/* Estilo para las alertas de Streamlit (Output) - El Manuscrito Descifrado */
div[data-testid="stAlert"] {
    background-color: #1A1A1A !important;
    border: 2px solid #6B5B3E !important;
    color: #F5F5DC !important;
    font-family: 'Georgia', serif;
    box-shadow: 0 0 10px rgba(139, 0, 0, 0.5); /* Sombra roja sutil */
}
/* Texto dentro de la alerta (OCR Result) - Hueso y grande */
div[data-testid="stAlert"] .stMarkdown p {
    font-size: 1.5em !important; 
    font-weight: bold;
    color: #F5F5DC !important;
    white-space: pre-wrap; /* Mantiene el formato del OCR */
}

/* Estilo para el Expander - Cofres de conocimiento */
div[data-testid="stExpander"] {
    border: 1px solid #6B5B3E !important;
    border-radius: 6px;
    margin-top: 15px;
    background-color: #151515;
}
div[data-testid="stExpander"] > div:first-child > div:first-child {
    font-size: 1.3em;
    font-weight: bold;
    color: #8B0000;
    text-shadow: 1px 1px 3px #000000;
}
</style>
"""
st.markdown(gothic_css, unsafe_allow_html=True)

st.title("El Códice de la Visión")
st.subheader("I. Rastreo y Tradición de Runas Prohibidas")

# --- 2. Imagen Gótica (Placeholder de un Sello) ---
image_url = "https://placehold.co/650x250/1A1A1A/6B5B3E?text=El+Ojo+del+Cazador+Observa"
st.image(image_url, caption="Una visión que corta la oscuridad.", use_column_width=True)

# --- 3. Selección de Fuente de Imagen ---

st.markdown("---")
st.subheader("II. Elige la Fuente del Sello")

cam_ = st.checkbox("Usar el Ojo de la Cámara (Webcam)")

# Placeholder para la imagen
img_file_buffer = None
bg_image = None
uploaded_file = None

if cam_ :
    # Si se selecciona la cámara, usa el input de la cámara
    img_file_buffer = st.camera_input("📸 Captura la Runa al instante")
else :
    # Si no se selecciona la cámara, usa el cargador de archivos
    bg_image = st.file_uploader("📥 Cargar Relicario Visual (Imagen):", type=["png", "jpg", "jpeg"])

# --- 4. Sidebar: OCR Filtro y Traducción ---

with st.sidebar:
    st.subheader("Protocolo de la Visión Ocular")
    
    # OCR Filter
    filtro_ocr = st.radio(
        "Ritual de Inversión (OCR Filtro)",
        ('Con el Ritual (Invertir)', 'Sin el Ritual (Normal)'),
        key="ocr_filter"
    )
    st.markdown("---")
    
    # Traducción Setup
    st.subheader("Parámetros de Tradición (Traducción)")
    
    # Mapa de lenguajes consolidado y más limpio
    lang_map = {
        "Inglés": "en", 
        "Español": "es", 
        "Bengalí": "bn", 
        "Coreano": "ko", 
        "Mandarín": "zh-cn", 
        "Japonés": "ja"
    }

    in_lang_name = st.selectbox(
        "Lengua de la Fuente (Input)",
        list(lang_map.keys()),
        key="in_lang_select"
    )
    input_language = lang_map[in_lang_name]

    out_lang_name = st.selectbox(
        "Lengua del Destino (Output)",
        list(lang_map.keys()),
        index=1, # Default a Español
        key="out_lang_select"
    )
    output_language = lang_map[out_lang_name]
    
    # Selección del Acento (tld)
    english_accent = st.selectbox(
        "Acento del Eco (tld)",
        (
            "Default (com)",
            "España (es)",
            "México (com.mx)",
            "Reino Unido (co.uk)",
            "Estados Unidos (com)",
            "Australia (com.au)",
        ),
        key="accent_select"
    )
    
    tld_map = {
        "Default (com)": "com",
        "España (es)": "es",
        "México (com.mx)": "com.mx",
        "Reino Unido (co.uk)": "co.uk",
        "Estados Unidos (com)": "com",
        "Australia (com.au)": "com.au",
    }
    tld = tld_map[english_accent]

    display_output_text = st.checkbox("Revelar el texto traducido", value=True)

# --- 5. Procesamiento de Imagen y OCR ---

processed_image = False

# 5.1 Procesamiento de Imagen Cargada
if bg_image is not None:
    # Simular la carga del archivo para el OCR
    bytes_data = bg_image.read()
    np_arr = np.frombuffer(bytes_data, np.uint8)
    cv2_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    st.image(bg_image, caption='Relicario Visual Cargado.', use_column_width=True)
    processed_image = True

# 5.2 Procesamiento de Imagen de Cámara
elif img_file_buffer is not None:
    # Para leer el buffer de la imagen con OpenCV:
    bytes_data = img_file_buffer.getvalue()
    np_arr = np.frombuffer(bytes_data, np.uint8)
    cv2_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    processed_image = True
    
# 5.3 Ejecución del OCR
if processed_image and cv2_img is not None:
    try:
        # Aplicar filtro de inversión (bitwise_not)
        if filtro_ocr == 'Con el Ritual (Invertir)':
            cv2_img = cv2.bitwise_not(cv2_img)
        
        # Convertir a RGB para Tesseract
        img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        
        # Reconocimiento de texto
        with st.spinner('Descifrando las Runas en el éter...'):
            text = pytesseract.image_to_string(img_rgb)
        
        st.session_state.recognized_text = text
        
        st.markdown(f"## 📜 Manuscrito Descifrado:")
        
        if st.session_state.recognized_text.strip():
            st.info(st.session_state.recognized_text)
        else:
            st.warning("El Oráculo no pudo discernir Runas claras en el Relicario Visual. Intenta con el Ritual de Inversión.")
        
    except Exception as e:
        st.error(f"Un fallo ocurrió durante el ritual de la Visión: {e}")

# --- 6. Botón y Ejecución de Traducción ---

st.markdown("---")
st.subheader("III. El Sello de la Tradición")

if st.button("🔥 Sellar la Tradición (Convertir a Audio)"):
    text_to_translate = st.session_state.recognized_text
    
    if not text_to_translate.strip():
        st.error("❌ No hay Runas descifradas para sellar la traducción. Captura o carga una imagen primero.")
    else:
        with st.spinner('Grabando el eco de la traducción en el éter...'):
            file_path, output_text = text_to_speech(input_language, output_language, text_to_translate, tld)
        
        if file_path and os.path.exists(file_path):
            audio_file = open(file_path, "rb")
            audio_bytes = audio_file.read()
            
            st.success("✨ ¡El conjuro ha sido traducido y grabado!")
            
            st.markdown(f"## 🎧 Eco del Destino (Audio):")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
        
            if display_output_text:
                st.markdown(f"## 📜 El Eco en Letras:")
                st.info(output_text)
        
        else:
            st.error("No se pudo completar el ritual de traducción y audio.")
            
# --- 7. Nuevo: Análisis de Sentimiento (TextBlob) ---

st.markdown("---")
st.subheader("IV. El Oráculo del Sentimiento")
st.caption("Escribe un texto directamente para que el Oráculo analice su carga emocional (Polaridad) y su naturaleza (Subjetividad).")

# Se usa el contenido del Sidebar del código proporcionado aquí
with st.sidebar:
    st.markdown("---")
    st.subheader("Polaridad y Subjetividad")
    st.markdown(
        """
        Polaridad: Indica si el sentimiento expresado en el texto es positivo, negativo o neutral. 
        Su valor oscila entre -1 (muy negativo) y 1 (muy positivo), con 0 representando un sentimiento neutral.
        
        Subjetividad: Mide cuánto del contenido es subjetivo (opiniones, emociones, creencias) frente a objetivo
        (hechos). Va de 0 a 1, donde 0 es completamente objetivo y 1 es completamente subjetivo.
        """
    )

# 7.1 Análisis de Polaridad y Subjetividad
with st.expander('🔮 Analizar el Núcleo Emocional del Texto'):
    text_to_analyze = st.text_area('Escribe la Revelación por favor: ', key='sentiment_input')
    
    if text_to_analyze:
        try:
            # Traducir a inglés para TextBlob
            with st.spinner('Traduciendo al idioma ancestral para el Oráculo...'):
                translation = translator.translate(text_to_analyze, src="auto", dest="en")
                trans_text = translation.text
            
            blob = TextBlob(trans_text)
            
            polarity = round(blob.sentiment.polarity, 2)
            subjectivity = round(blob.sentiment.subjectivity, 2)
            
            st.markdown("### Resultados de la Revelación:")
            st.write(f'**Polaridad (Carga Emocional):** `{polarity}`')
            st.write(f'**Subjetividad (Naturaleza del Texto):** `{subjectivity}`')
            
            # Clasificación del sentimiento
            if polarity >= 0.5:
                st.success('Es un sentimiento **Positivo** (Euforia del Cazador) 😊')
            elif polarity <= -0.5:
                st.error('Es un sentimiento **Negativo** (Gritos de la Noche) 😔')
            else:
                st.warning('Es un sentimiento **Neutral** (Silencio Observante) 😐')
                
        except Exception as e:
             st.error(f"Fallo en el análisis del Oráculo: {e}")

# 7.2 Corrección en Inglés
with st.expander('🖋️ Corregir Sello Rúnico (Sólo Inglés)'):
    text_to_correct = st.text_area('Escribe el Sello Erróneo en Inglés: ', key='correction_input')
    if text_to_correct:
        try:
            blob2 = TextBlob(text_to_correct)
            corrected_text = str(blob2.correct())
            
            st.markdown("### Sello Rúnico Corregido:")
            st.info(corrected_text)
            
        except Exception as e:
            st.error(f"Fallo al corregir el sello: {e}")
