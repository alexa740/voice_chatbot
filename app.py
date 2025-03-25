import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import os

# Backend API URL
API_URL = "http://localhost:8000/ask"

# Recording settings
DURATION = 5  # Record for 5 seconds
SAMPLE_RATE = 44100  # Sample rate
FILENAME = "recorded_audio.wav"

def record_audio():
    """Records audio from the microphone and saves it to a file."""
    st.info("Recording... Speak now!")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.int16)
    sd.wait()  # Wait until recording is done
    wav.write(FILENAME, SAMPLE_RATE, audio_data)  # Save as WAV file
    st.success("Recording complete!")

def send_audio():
    """Sends the recorded audio file to FastAPI and gets the bot's response."""
    if not os.path.exists(FILENAME):
        st.error("No audio file found. Please record first.")
        return None

    files = {"audio": open(FILENAME, "rb")}
    st.info("Sending audio to server...")

    try:
        response = requests.post(API_URL, files=files)
    except requests.exceptions.ConnectionError:
        st.error("Backend is not running. Start FastAPI first.")
        return None

    if response.status_code == 200:
        reply = response.json().get("reply", "No response received.")
        st.success(f"Bot's Response: {reply}")
        return reply
    else:
        st.error(f"Failed to process the request. Error: {response.text}")
        return None

# Streamlit UI
st.title("🎙️ AI Voice Bot")
st.write("Ask questions using your voice, and get AI-generated responses!")

if st.button("🎤 Record Audio"):
    record_audio()

if st.button("🚀 Send to AI Bot"):
    bot_reply = send_audio()
