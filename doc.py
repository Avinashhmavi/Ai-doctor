import streamlit as st
import os
from dotenv import load_dotenv
import base64
from groq import Groq
from gtts import gTTS
import elevenlabs
import speech_recognition as sr

# Load environment variables
load_dotenv()
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]

# Initialize AI clients
groq_client = Groq(api_key=GROQ_API_KEY)
elevenlabs_client = elevenlabs.ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Function to encode image to base64
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Function to analyze image and voice input together
def analyze_image_and_voice(user_query, model, encoded_image):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_query},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                },
            ],
        }
    ]
    chat_completion = groq_client.chat.completions.create(
        messages=messages, model=model
    )
    return chat_completion.choices[0].message.content

# Function to generate AI response for text-only queries
def generate_ai_response(user_query):
    messages = [{"role": "user", "content": user_query}]
    chat_completion = groq_client.chat.completions.create(
        messages=messages, model="llama-3.2-90b-vision-preview"
    )
    return chat_completion.choices[0].message.content

# Function to convert AI response to speech using ElevenLabs
def text_to_speech(input_text, output_filepath):
    audio = elevenlabs_client.generate(
        text=input_text, voice="Aria", output_format="mp3_22050_32", model="eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)
    return output_filepath

# Function to transcribe uploaded audio file
def transcribe_uploaded_audio():
    st.info("Upload an audio file for transcription:")
    uploaded_audio = st.file_uploader("Choose an audio file", type=["wav", "mp3", "m4a"])
    
    if uploaded_audio is not None:
        recognizer = sr.Recognizer()
        with sr.AudioFile(uploaded_audio) as source:
            audio_data = recognizer.record(source)
            st.success("Audio uploaded successfully. Processing transcription...")
            try:
                return recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                st.error("Could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Speech Recognition service; {e}")
    else:
        return None

# Streamlit App
def main():
    st.title("🧑‍⚕️🩺AI Doctor 2.0: Voice and Vision")
    
    uploaded_image = st.file_uploader("Upload an image for analysis", type=["jpg", "jpeg", "png"])
    encoded_image = None
    
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        encoded_image = encode_image(uploaded_image)

        # Initial image analysis
        st.subheader("AI Image Analysis:")
        initial_query = "Describe the condition in this image."
        model = "llama-3.2-90b-vision-preview"
        analysis_result = analyze_image_and_voice(initial_query, model, encoded_image)
        st.write(analysis_result)

        # Convert analysis result to speech
        audio_path = text_to_speech(analysis_result, "ai_analysis.mp3")
        st.audio(audio_path)

    # Interaction Section
    st.subheader("Ask a question (Text or Voice)")

    # Text Input for Questions
    user_text_input = st.text_input("Type your question here:")
    if user_text_input and encoded_image:
        ai_response = analyze_image_and_voice(user_text_input, model, encoded_image)
    elif user_text_input:
        ai_response = generate_ai_response(user_text_input)
    else:
        ai_response = None

    if ai_response:
        st.subheader("AI Response:")
        st.write(ai_response)

        # Convert response to speech
        response_audio_path = text_to_speech(ai_response, "ai_response.mp3")
        st.audio(response_audio_path)

    # Voice Input for Questions (Using Uploaded Audio)
    st.subheader("Or upload an audio file to ask a question:")
    user_voice_input = transcribe_uploaded_audio()

    if user_voice_input:
        st.subheader("Transcription:")
        st.write(user_voice_input)

        if encoded_image:
            ai_voice_response = analyze_image_and_voice(user_voice_input, model, encoded_image)
        else:
            ai_voice_response = generate_ai_response(user_voice_input)

        st.subheader("AI Response:")
        st.write(ai_voice_response)

        # Convert response to speech
        voice_audio_path = text_to_speech(ai_voice_response, "ai_voice_response.mp3")
        st.audio(voice_audio_path)

if __name__ == "__main__":
    main()
