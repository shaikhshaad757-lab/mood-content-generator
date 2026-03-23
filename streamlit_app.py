import streamlit as st
import base64
import tempfile
import os
from dotenv import load_dotenv
from gapi import generate_content, get_video_link, get_image_link

from speech_to_text import transcribe_wav_path
from st_audiorec import st_audiorec

import cv2
import numpy as np
from fer import FER

# --- Page Config ---
st.set_page_config(page_title="Mood-Based Content Generator", page_icon="🎭", layout="wide")

# --- Load env ---
load_dotenv()

# 🔥 Emotion detection from IMAGE (not webcam)
def detect_emotion_from_image(image):
    detector = FER()
    result = detector.detect_emotions(image)

    if result:
        emotions = result[0]["emotions"]
        dominant = max(emotions, key=emotions.get)
        return dominant
    else:
        return "No face detected"


# --- Theme toggle ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode


# --- Sidebar ---
with st.sidebar:
    st.title("🎭 Mood History")
    if "history" not in st.session_state:
        st.session_state["history"] = []
    for i, h in enumerate(st.session_state["history"]):
        st.markdown(f"**{i+1}.** {h}")
    st.button("🌗 Toggle Theme", on_click=toggle_theme)


# --- Styling ---
bg_color = "#1a1a2e" if st.session_state.dark_mode else "#f5f5f5"
text_color = "#ffffff" if st.session_state.dark_mode else "#000000"

st.markdown(f"""
<style>
.stApp {{
    background-color: {bg_color};
    color: {text_color};
}}
</style>
""", unsafe_allow_html=True)


# --- Title ---
st.title("✨ Mood-Based Content Generator")

# --- Input ---
st.subheader("How are you feeling today?")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    mood = st.radio("Select mood", ["😊 Happy", "😢 Sad", "😡 Angry", "😌 Calm"], label_visibility="collapsed")

with col2:
    user_text = st.text_input("Type your mood or idea here...")

with col3:
    st.markdown("🎤 Voice Input")
    wav_audio_data = st_audiorec()
    if wav_audio_data is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(wav_audio_data)
            tmp_path = tmp.name
        user_text = transcribe_wav_path(tmp_path)


# 🔥 CAMERA INPUT (FIXED)
st.subheader("📸 Capture your face")

img_file = st.camera_input("Take a photo")

if img_file is not None:
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)

    st.image(frame, channels="BGR")

    if st.button("🎭 Detect Emotion"):
        emotion = detect_emotion_from_image(frame)
        st.session_state.detected_emotion = emotion

        if "no face" not in emotion.lower():
            st.success(f"Detected Emotion: {emotion}")
            user_text = emotion
        else:
            st.error(emotion)


# --- Output Options ---
st.subheader("Choose what you want:")
colA, colB, colC = st.columns(3)

want_text = colA.checkbox("📝 Text", True)
want_video = colB.checkbox("🎬 Video", True)
want_image = colC.checkbox("🖼️ Image", True)


# --- Chat history ---
if "chat" not in st.session_state:
    st.session_state.chat = []


# --- Generate ---
if st.button("✨ Generate Content"):
    prompt_text = ""

    if "detected_emotion" in st.session_state:
        prompt_text = st.session_state.detected_emotion
    elif user_text:
        prompt_text = user_text

    if not prompt_text:
        st.error("Please provide input!")
    else:
        st.session_state["history"].append(prompt_text)

        output = {}

        if want_text:
            output["text"] = generate_content(prompt_text)

        if want_image:
            output["image"] = get_image_link(prompt_text)

        if want_video:
            output["video"] = get_video_link(prompt_text)

        st.session_state.chat.append({"user": prompt_text, "ai": output})


# --- Chat Display ---
st.subheader("💬 Conversation")

for msg in st.session_state.chat:
    st.markdown(f"**You:** {msg['user']}")
    ai = msg["ai"]

    if ai.get("text"):
        st.write(ai["text"])

    if ai.get("video"):
        st.markdown(f"[Watch Video]({ai['video']})")

    if ai.get("image"):
        st.image(ai["image"])