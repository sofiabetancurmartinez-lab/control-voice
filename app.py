import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# ---------------- CONFIG VISUAL ----------------
st.set_page_config(
    page_title="Alimentador de Mascotas",
    page_icon="🐾",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff7ed 0%, #fef3c7 45%, #fde68a 100%);
}

.main-card {
    background: rgba(255, 255, 255, 0.88);
    padding: 2rem;
    border-radius: 28px;
    box-shadow: 0 12px 35px rgba(120, 72, 24, 0.18);
    text-align: center;
    margin-top: 1rem;
}

.title {
    font-size: 3rem;
    font-weight: 800;
    color: #7c3f00;
    margin-bottom: 0;
}

.subtitle {
    font-size: 1.3rem;
    color: #9a5a13;
    margin-top: 0.2rem;
    margin-bottom: 1.5rem;
}

.instruction {
    background: #fff3cd;
    color: #7c3f00;
    padding: 1rem;
    border-radius: 18px;
    font-size: 1.05rem;
    margin: 1rem 0;
    border: 1px solid #facc15;
}

.command-box {
    background: #ffffff;
    border: 2px dashed #d97706;
    color: #7c2d12;
    padding: 1rem;
    border-radius: 18px;
    margin-top: 1rem;
    font-weight: 600;
}

.footer-note {
    font-size: 0.9rem;
    color: #92400e;
    margin-top: 1.5rem;
}

div.stButton > button {
    background-color: #f59e0b;
    color: white;
    border-radius: 18px;
    border: none;
    padding: 0.8rem 1.2rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

def on_publish(client,userdata,result):             #create function for callback
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("sofibeta")
client1.on_message = on_message

st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.markdown('<h1 class="title">🐾 ALIMENTADOR DE MASCOTAS</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Control por voz para servir comida automáticamente</p>', unsafe_allow_html=True)

try:
    image = Image.open('voice_ctrl.jpg')
    st.image(image, width=190)
except:
    st.markdown("### 🎙️🐶")

st.markdown(
    '<div class="instruction">Toca el botón y di una frase como:<br><b>feed</b>, o <b>food</b></div>',
    unsafe_allow_html=True
)

stt_button = Button(label="🎙️ Inicio", width=220)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.markdown(
            f'<div class="command-box">Comando escuchado: {result.get("GET_TEXT")}</div>',
            unsafe_allow_html=True
        )

        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":result.get("GET_TEXT").strip()})
        ret= client1.publish("voice_ctrl666", message)

        st.success("Comando enviado al alimentador 🐶🍖")

    
    try:
        os.mkdir("temp")
    except:
        pass

st.markdown('<p class="footer-note">Sistema multimodal conectado con Wokwi mediante MQTT.</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
