import streamlit as st
import os
from dotenv import load_dotenv
import base64
from groq import Groq
from gtts import gTTS
import speech_recognition as sr
from tempfile import NamedTemporaryFile
import re

# Load environment variables
load_dotenv()
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Initialize AI client
groq_client = Groq(api_key=GROQ_API_KEY)

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

# Function to clean text by removing special characters for speech
def clean_text_for_speech(text):
    # Remove special characters but keep spaces and basic punctuation for natural flow
    # This regex removes: , ; * ( ) [ ] { } ! ? @ # $ % ^ & + = _ - " ' ` ~ |
    cleaned_text = re.sub(r'[,\;\*\(\)\[\]\{\}!?@#$%^&+=_"\'`~|]', '', text)
    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

# Function to convert AI response to speech using gTTS and return base64 audio
def text_to_speech(input_text):
    if not input_text or not isinstance(input_text, str):
        st.error("Invalid input text for speech conversion.")
        return None
    
    # Clean the text before converting to speech
    cleaned_text = clean_text_for_speech(input_text)
    
    try:
        # Generate audio with gTTS using cleaned text
        tts = gTTS(text=cleaned_text, lang='en')
        # Save to a temporary file
        with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts.save(temp_file.name)
            # Read the audio file and encode it to base64
            with open(temp_file.name, "rb") as audio_file:
                audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            os.unlink(temp_file.name)  # Clean up temporary file
            return audio_base64
    except Exception as e:
        st.error(f"Error during text-to-speech conversion with gTTS: {e}")
        return None

# Function to play audio automatically with controls
def play_audio(audio_base64):
    if audio_base64:
        audio_html = f"""
        <audio autoplay controls>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# Function to transcribe uploaded audio file
def transcribe_uploaded_audio():
    st.info("Upload an audio file for transcription:")
    uploaded_audio = st.file_uploader("Choose an audio file", type=["wav", "mp3", "m4a"], key="audio_uploader")
    
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
    return None

# Streamlit App
def main():
    st.title("🧑‍⚕️🩺AI Doctor 2.0: Voice and Vision")
    
    uploaded_image = st.file_uploader("Upload an image for analysis", type=["jpg", "jpeg", "png"], key="image_uploader")
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

        # Convert analysis result to speech and play automatically with controls
        audio_base64 = text_to_speech(analysis_result)
        play_audio(audio_base64)

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

        # Convert response to speech and play automatically with controls
        response_audio_base64 = text_to_speech(ai_response)
        play_audio(response_audio_base64)

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

        # Convert response to speech and play automatically with controls
        voice_audio_base64 = text_to_speech(ai_voice_response)
        play_audio(voice_audio_base64)

if __name__ == "__main__":
    main()
