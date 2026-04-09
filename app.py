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

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Visión a Voz",
    page_icon="🧠",
    layout="wide"
)

# =========================
# ESTILOS PERSONALIZADOS
# =========================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .hero-box {
        background: white;
        padding: 1.4rem 1.6rem;
        border-radius: 22px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }

    .card-box {
        background: white;
        padding: 1.2rem 1.3rem;
        border-radius: 18px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }

    .title-main {
        font-size: 2.6rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.3rem;
    }

    .subtitle-main {
        font-size: 1.08rem;
        color: #475569;
        margin-bottom: 0.2rem;
    }

    .small-note {
        font-size: 0.95rem;
        color: #64748b;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.6rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 0.7rem 1rem;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #1d4ed8 0%, #4338ca 100%);
        color: white;
    }

    .stTextArea textarea {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# VARIABLES GLOBALES
# =========================
translator = Translator()

IDIOMAS = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Italiano": "it",
    "Portugués": "pt",
    "Alemán": "de"
}

ACENTOS = {
    "General": "com",
    "México": "com.mx",
    "Reino Unido": "co.uk",
    "Estados Unidos": "com",
    "Canadá": "ca",
    "Australia": "com.au",
    "Irlanda": "ie",
    "Sudáfrica": "co.za"
}

if "texto_ocr" not in st.session_state:
    st.session_state.texto_ocr = ""

if "texto_traducido" not in st.session_state:
    st.session_state.texto_traducido = ""

if "audio_path" not in st.session_state:
    st.session_state.audio_path = None

# =========================
# FUNCIONES
# =========================
def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    translated_text = translation.text
    tts = gTTS(translated_text, lang=output_language, tld=tld, slow=False)

    try:
        file_name = text[:20].replace(" ", "_")
        if not file_name.strip():
            file_name = "audio"
    except:
        file_name = "audio"

    os.makedirs("temp", exist_ok=True)
    file_path = f"temp/{file_name}.mp3"
    tts.save(file_path)
    return file_path, translated_text


def remove_files(days):
    os.makedirs("temp", exist_ok=True)
    mp3_files = glob.glob("temp/*.mp3")
    if mp3_files:
        now = time.time()
        max_age = days * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - max_age:
                os.remove(f)


def ocr_from_uploaded_file(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)
    texto = pytesseract.image_to_string(img_np)
    return image, texto


def ocr_from_camera(img_file_buffer, aplicar_filtro):
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if aplicar_filtro:
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    texto = pytesseract.image_to_string(img_rgb)
    return img_rgb, texto


# Limpieza de audios antiguos
remove_files(7)

# =========================
# ENCABEZADO
# =========================
st.markdown("""
<div class="hero-box">
    <div class="title-main">🧠 Visión a Voz</div>
    <div class="subtitle-main">
        Reconoce texto en imágenes, tradúcelo y conviértelo en audio desde una sola interfaz.
    </div>
    <div class="small-note">
        Puedes trabajar con una imagen de tu equipo o capturar una foto directamente desde la cámara.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Personalización")
    fuente = st.radio(
        "Fuente de imagen",
        ("Cargar archivo", "Usar cámara")
    )

    aplicar_filtro = st.checkbox("Aplicar filtro de inversión", value=False)

    st.markdown("---")
    st.markdown("### 🌍 Traducción")
    idioma_entrada_nombre = st.selectbox("Idioma de entrada", list(IDIOMAS.keys()), index=0)
    idioma_salida_nombre = st.selectbox("Idioma de salida", list(IDIOMAS.keys()), index=1)
    acento_nombre = st.selectbox("Acento del audio", list(ACENTOS.keys()), index=0)

    mostrar_texto_traducido = st.checkbox("Mostrar texto traducido", value=True)

input_language = IDIOMAS[idioma_entrada_nombre]
output_language = IDIOMAS[idioma_salida_nombre]
tld = ACENTOS[acento_nombre]

# =========================
# CUERPO PRINCIPAL
# =========================
col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📷 Imagen de entrada</div>', unsafe_allow_html=True)

    imagen_mostrada = None

    if fuente == "Cargar archivo":
        uploaded_image = st.file_uploader("Selecciona una imagen", type=["png", "jpg", "jpeg"])
        if uploaded_image is not None:
            imagen_mostrada, texto_detectado = ocr_from_uploaded_file(uploaded_image)
            st.image(imagen_mostrada, caption="Imagen cargada", use_container_width=True)
            st.session_state.texto_ocr = texto_detectado

    else:
        img_file_buffer = st.camera_input("Toma una foto")
        if img_file_buffer is not None:
            imagen_mostrada, texto_detectado = ocr_from_camera(img_file_buffer, aplicar_filtro)
            st.image(imagen_mostrada, caption="Foto procesada", use_container_width=True)
            st.session_state.texto_ocr = texto_detectado

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Texto reconocido</div>', unsafe_allow_html=True)

    texto_editable = st.text_area(
        "Resultado OCR",
        value=st.session_state.texto_ocr,
        height=250,
        placeholder="Aquí aparecerá el texto detectado en la imagen."
    )
    st.session_state.texto_ocr = texto_editable

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# TRADUCCIÓN Y AUDIO
# =========================
st.markdown('<div class="card-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔊 Traducción y audio</div>', unsafe_allow_html=True)

if st.button("Generar traducción y audio"):
    if st.session_state.texto_ocr.strip():
        audio_path, output_text = text_to_speech(
            input_language,
            output_language,
            st.session_state.texto_ocr.strip(),
            tld
        )
        st.session_state.audio_path = audio_path
        st.session_state.texto_traducido = output_text
        st.success("El audio fue generado correctamente.")
    else:
        st.warning("Primero debes cargar una imagen o tomar una foto con texto legible.")

if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
    with open(st.session_state.audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")

if mostrar_texto_traducido and st.session_state.texto_traducido:
    st.markdown("#### Texto traducido")
    st.write(st.session_state.texto_traducido)

st.markdown('</div>', unsafe_allow_html=True)
