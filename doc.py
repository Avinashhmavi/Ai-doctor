import streamlit as st
import os
from dotenv import load_dotenv
import base64
from groq import Groq
from gtts import gTTS
import speech_recognition as sr
from tempfile import NamedTemporaryFile
import re
from pydub import AudioSegment

# Load environment variables
load_dotenv()
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Initialize AI client
groq_client = Groq(api_key=GROQ_API_KEY)

# Custom CSS for vibrant styling and centering AI response
st.markdown("""
    <style>
    .main {
        background-color: #f0f4f8;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #ff6f61;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff4f41;
    }
    .stTextInput>div>input {
        border: 2px solid #4a90e2;
        border-radius: 5px;
        padding: 8px;
    }
    .stFileUploader>div {
        border: 2px dashed #f4a261;
        border-radius: 5px;
        padding: 10px;
        background-color: #fffcf2;
    }
    h1, h2, h3 {
        color: #2a9d8f;
        font-family: 'Arial', sans-serif;
    }
    .stSuccess {
        background-color: #e9f7ef;
        color: #27ae60;
    }
    .stError {
        background-color: #ffe6e6;
        color: #c0392b;
    }
    .ai-response {
        text-align: center;
        margin: 20px 0;
    }
    .ai-response audio {
        display: block;
        margin: 10px auto;
    }
    </style>
""", unsafe_allow_html=True)

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
    cleaned_text = re.sub(r'[,\;\*\(\)\[\]\{\}!?@#$%^&+=_"\'`~|]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

# Function to convert AI response to speech using gTTS and return base64 audio
def text_to_speech(input_text):
    if not input_text or not isinstance(input_text, str):
        st.error("Invalid input text for speech conversion. 🚫")
        return None
    
    cleaned_text = clean_text_for_speech(input_text)
    
    try:
        tts = gTTS(text=cleaned_text, lang='en')
        with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts.save(temp_file.name)
            with open(temp_file.name, "rb") as audio_file:
                audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            os.unlink(temp_file.name)
            return audio_base64
    except Exception as e:
        st.error(f"Error during text-to-speech conversion: {e} 🚨")
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
    st.info("Upload an audio file (MP3 or WAV) for transcription: 🎤")
    uploaded_audio = st.file_uploader("Choose an audio file", type=["wav", "mp3"], key="audio_uploader")
    
    if uploaded_audio is not None:
        temp_wav_path = None
        try:
            with st.spinner("Processing audio... ⏳"):
                audio_segment = AudioSegment.from_file(uploaded_audio)
                with NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                    temp_wav_path = temp_wav.name
                    audio_segment.export(temp_wav_path, format="wav")
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(temp_wav_path) as source:
                        audio_data = recognizer.record(source)
                        st.success("Audio uploaded successfully. Processing transcription... ✅")
                        transcribed_text = recognizer.recognize_google(audio_data)
                        os.unlink(temp_wav_path)
                        return transcribed_text
        except sr.UnknownValueError:
            st.error("Could not understand the audio. 😕")
            return None
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service: {e} 🚨")
            return None
        except Exception as e:
            st.error(f"Error processing uploaded audio file: {e} 🚫")
            return None
        finally:
            if temp_wav_path and os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)
    return None

# Streamlit App
def main():
    st.title("🧑‍⚕️🩺 AI Doctor 2.0: Voice and Vision")
    st.markdown("Welcome to your vibrant AI health assistant! 🌟", unsafe_allow_html=True)

    # Image Upload Section
    with st.expander("📸 Upload an Image for Analysis", expanded=True):
        uploaded_image = st.file_uploader("Drop your image here", type=["jpg", "jpeg", "png"], key="image_uploader")
        if uploaded_image is not None:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
            encoded_image = encode_image(uploaded_image)

            with st.spinner("Analyzing image... 🔍"):
                st.subheader("AI Image Analysis:")
                initial_query = "Describe the condition in this image."
                model = "llama-3.2-90b-vision-preview"
                analysis_result = analyze_image_and_voice(initial_query, model, encoded_image)
                st.markdown(f'<div class="ai-response">{analysis_result}</div>', unsafe_allow_html=True)
                audio_base64 = text_to_speech(analysis_result)
                play_audio(audio_base64)

    # Interaction Section
    st.markdown("---")
    st.subheader("💬 Ask a Question (Text or Upload Audio)")

    # Use session state to store responses and manage input
    if 'responses' not in st.session_state:
        st.session_state.responses = []

    col1, col2 = st.columns([2, 1])
    with col1:
        user_text_input = st.text_input("Type your question here:", placeholder="e.g., What’s my diagnosis?", key="text_input")
    with col2:
        if st.button("Submit", key="text_submit"):
            if user_text_input:
                with st.spinner("Generating response... ⚙️"):
                    if 'encoded_image' in locals():
                        ai_response = analyze_image_and_voice(user_text_input, model, encoded_image)
                    else:
                        ai_response = generate_ai_response(user_text_input)
                    st.session_state.responses.append((user_text_input, ai_response))
                    # Clear the input by resetting the key (Streamlit will generate a new widget)
                    st.session_state.text_input = ""

    # Display previous responses
    for i, (question, response) in enumerate(st.session_state.responses):
        st.markdown(f"**Q{i+1}:** {question}")
        st.markdown(f'<div class="ai-response">{response}</div>', unsafe_allow_html=True)
        audio_base64 = text_to_speech(response)
        play_audio(audio_base64)
        st.markdown("---")

    # Audio Upload Section
    with st.expander("🎙️ Upload an Audio Question"):
        user_uploaded_voice_input = transcribe_uploaded_audio()
        if user_uploaded_voice_input:
            with st.spinner("Generating response... ⚙️"):
                if 'encoded_image' in locals():
                    ai_uploaded_voice_response = analyze_image_and_voice(user_uploaded_voice_input, model, encoded_image)
                else:
                    ai_uploaded_voice_response = generate_ai_response(user_uploaded_voice_input)
                st.session_state.responses.append((user_uploaded_voice_input, ai_uploaded_voice_response))

if __name__ == "__main__":
    main()
