import os
import requests
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
import speech_recognition as sr

app = FastAPI()


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("API Key is missing! Set GROQ_API_KEY in your environment.")

def transcribe_audio(file_path):
    """Convert audio to text using SpeechRecognition (or use Whisper API)."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Could not request results, check your network."

def chat_with_groq(user_input):
    """Sends text to Groq API and returns the response."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are Vaishnavi, responding to personal questions in a naturally."},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post(GROQ_API_URL, json=data, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        return f"API Request Failed: {str(e)}"


    print(f"API Status Code: {response.status_code}")
    print(f"Full API Response: {response.text}")

    if response.status_code != 200:
        return f"Error {response.status_code}: {response.text}"

    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        return "Error: API response is not JSON. Check API key and endpoint."

    if "choices" not in response_json:
        return f"Unexpected API response: {response_json}"

    return response_json["choices"][0]["message"]["content"]

@app.post("/ask")
async def ask_question(audio: UploadFile = File(...)):
    """Processes audio, converts to text, and queries Groq API."""
    file_path = f"temp_{audio.filename}"

    try:
        
        with open(file_path, "wb") as f:
            f.write(await audio.read())

        user_input = transcribe_audio(file_path)
        if not user_input:
            raise HTTPException(status_code=400, detail="Failed to transcribe audio.")

        bot_reply = chat_with_groq(user_input)

    finally:
        
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"reply": bot_reply}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
