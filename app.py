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

texto = ""

translator = Translator()


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
    tts.save(f"temp/{file_name}.mp3")
    return file_name, translated_text


def remove_files(days):
    mp3_files = glob.glob("temp/*.mp3")
    if mp3_files:
        now = time.time()
        max_age = days * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - max_age:
                os.remove(f)


remove_files(7)

st.set_page_config(page_title="Lectura Inteligente", page_icon="🖼️", layout="centered")

st.title("🖼️ Lectura Inteligente de Imágenes")
st.subheader("Extrae texto desde una imagen, tradúcelo y conviértelo en audio.")

usar_camara = st.checkbox("Usar cámara")

if usar_camara:
    img_file_buffer = st.camera_input("Toma una foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.header("Configuración")
    st.subheader("Procesamiento de imagen")
    filtro = st.radio("Aplicar filtro a la imagen capturada", ("Sí", "No"))

bg_image = st.file_uploader("Cargar imagen", type=["png", "jpg", "jpeg"])

if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption="Imagen cargada", use_container_width=True)

    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.read())

    st.success(f"Imagen guardada como {uploaded_file.name}")

    img_cv = cv2.imread(uploaded_file.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    texto = pytesseract.image_to_string(img_rgb)

if texto.strip():
    st.markdown("### Texto reconocido")
    st.write(texto)

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == "Sí":
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    texto = pytesseract.image_to_string(img_rgb)

    st.markdown("### Texto reconocido")
    st.write(texto)

with st.sidebar:
    st.subheader("Parámetros de traducción")

    os.makedirs("temp", exist_ok=True)

    idiomas = {
        "Inglés": "en",
        "Español": "es",
        "Francés": "fr",
        "Italiano": "it",
        "Portugués": "pt",
        "Alemán": "de"
    }

    idioma_entrada = st.selectbox("Seleccione el idioma de entrada", list(idiomas.keys()))
    input_language = idiomas[idioma_entrada]

    idioma_salida = st.selectbox("Seleccione el idioma de salida", list(idiomas.keys()))
    output_language = idiomas[idioma_salida]

    acentos = {
        "General": "com",
        "México": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }

    acento = st.selectbox("Seleccione el acento", list(acentos.keys()))
    tld = acentos[acento]

    mostrar_texto_salida = st.checkbox("Mostrar texto traducido")

    if st.button("Generar audio"):
        if texto.strip():
            result, output_text = text_to_speech(input_language, output_language, texto, tld)

            with open(f"temp/{result}.mp3", "rb") as audio_file:
                audio_bytes = audio_file.read()

            st.markdown("## Audio generado")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            if mostrar_texto_salida:
                st.markdown("## Texto traducido")
                st.write(output_text)
        else:
            st.warning("Primero debes cargar una imagen o tomar una foto con texto legible.")
