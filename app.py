import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

def on_publish(client, userdata, result):
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
topic = "voice_ctrl666"

client1 = paho.Client("sofibeta_streamlit")
client1.on_message = on_message

st.title("🐾 PETBUDDY")
st.subheader("CONTROL DE ALIMENTACIÓN POR VOZ")

try:
    image = Image.open("voice_ctrl.jpg")
    st.image(image, width=200)
except:
    st.info("Imagen no encontrada: voice_ctrl.jpg")

st.write("Toca el botón y di: alimentar, comida, dar comida o servir comida")

stt_button = Button(label="🎙️ Inicio", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "es-ES";
 
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
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT").strip().lower()
        st.write("Comando escuchado:", texto)

        client1.on_publish = on_publish
        client1.connect(broker, port)

        message = json.dumps({"Act1": texto})
        ret = client1.publish(topic, message)

        st.success("Comando enviado a Wokwi")

    try:
        os.mkdir("temp")
    except:
        pass
