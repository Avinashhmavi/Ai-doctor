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

# Initialize session state for storing the diagnosis and response count
if "diagnosis" not in st.session_state:
    st.session_state.diagnosis = None
if "response_count" not in st.session_state:
    st.session_state.response_count = 0

# Function to encode image to base64
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Function to extract diagnosis from the analysis result
def extract_diagnosis(analysis_result):
    lines = analysis_result.split('\n')
    for line in lines:
        if "Primary Diagnosis" in line or "Diagnosis:" in line or "Diagnostic Assessment" in line:
            diagnosis = line.split(":", 1)[1].strip() if ":" in line else lines[lines.index(line) + 1].strip()
            diagnosis = re.sub(r'\(.*?confidence\)', '', diagnosis).strip()
            return diagnosis
    for i, line in enumerate(lines):
        if "Diagnostic" in line or "Key Findings" in line:
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith("- Alternative"):
                    return lines[j].strip()
    return "a medical condition based on the image analysis"

# Function to analyze image and voice input together
def analyze_image_and_voice(user_query, model, encoded_image, is_initial_analysis=True):
    if is_initial_analysis:
        medical_query = """
You are a highly skilled medical imaging expert. Analyze the uploaded medical image as follows:

###  Image Type & Region
- Specify the type of image (e.g., CT scan, X-ray, MRI)
- Identify the anatomical region (e.g., chest, brain) and view (e.g., axial)
- Comment on image quality

### Key Findings
- List primary observations (e.g., normal lungs, no masses)
- Note any abnormalities with details (e.g., size, location)
- Rate severity: Normal/Mild/Moderate/Severe

### Diagnostic Assessment
- Provide a primary diagnosis with confidence level (e.g., 95% confidence)
- List differential diagnoses if applicable
- Support with evidence from the image

### Patient-Friendly Explanation
- Explain findings in simple language
- Address common patient concerns (e.g., "What should I do next?")

Format your response with markdown headers and bullet points.
"""
        full_query = medical_query + f"\n\nUser's additional query: {user_query}" if user_query else medical_query
    else:
        diagnosis = st.session_state.diagnosis if st.session_state.diagnosis else "a medical condition based on the image analysis"
        full_query = f"""
You are an AI doctor. The patient has been diagnosed with {diagnosis}. The patient has asked: "{user_query}". Provide a concise, direct answer in simple language, referencing the image findings if relevant. Offer general treatment advice confidently as a doctor would.
"""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": full_query},
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
    response = chat_completion.choices[0].message.content
    if is_initial_analysis:
        st.session_state.diagnosis = extract_diagnosis(response)
    return response

# Function to generate AI response for text-only queries
def generate_ai_response(user_query):
    messages = [{"role": "user", "content": user_query}]
    chat_completion = groq_client.chat.completions.create(
        messages=messages, model="llama-3.2-90b-vision-preview"
    )
    return chat_completion.choices[0].message.content

# Function to clean text for speech
def clean_text_for_speech(text):
    cleaned_text = re.sub(r'[,\;\*\(\)\[\]\{\}!?@#$%^&+=_"\'`~|]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

# Function to convert text to speech
def text_to_speech(input_text, response_key):
    if not input_text or not isinstance(input_text, str):
        st.error(f"Invalid input text for speech conversion (Response {response_key}).")
        return None
    
    cleaned_text = clean_text_for_speech(input_text)
    if not cleaned_text:
        st.error(f"Text after cleaning is empty (Response {response_key}).")
        return None
    
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
        st.error(f"Error during text-to-speech conversion (Response {response_key}): {e}")
        return None

# Function to play audio
def play_audio(audio_base64, response_key):
    if audio_base64:
        audio_html = f"""
        <audio autoplay controls id="audio-{response_key}">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.warning(f"Audio could not be generated for response {response_key}.")

# Function to transcribe uploaded audio
def transcribe_uploaded_audio():
    uploaded_audio = st.file_uploader("Choose an audio file", type=["wav", "mp3"], key="audio_uploader")
    if uploaded_audio is not None:
        temp_wav_path = None
        try:
            audio_segment = AudioSegment.from_file(uploaded_audio)
            with NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                temp_wav_path = temp_wav.name
                audio_segment.export(temp_wav_path, format="wav")
                recognizer = sr.Recognizer()
                with sr.AudioFile(temp_wav_path) as source:
                    audio_data = recognizer.record(source)
                    transcribed_text = recognizer.recognize_google(audio_data)
                    os.unlink(temp_wav_path)
                    return transcribed_text
        except Exception as e:
            st.error(f"Error processing audio: {e}")
            return None
        finally:
            if temp_wav_path and os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)
    return None

# Streamlit App
def main():
    st.title("🧑‍⚕️🩺 AI Doctor 2.0: Voice and Vision")
    st.markdown("Welcome to your vibrant AI health assistant! 🌟", unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader("Upload an image for analysis", type=["jpg", "jpeg", "png"], key="image_uploader")
    encoded_image = None
    
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
        encoded_image = encode_image(uploaded_image)

        # Initial image analysis
        st.subheader("AI Image Analysis:")
        initial_query = "Describe the condition in this image."
        model = "llama-3.2-90b-vision-preview"
        analysis_result = analyze_image_and_voice(initial_query, model, encoded_image, is_initial_analysis=True)
        st.write(analysis_result)

        # Convert analysis result to speech
        st.session_state.response_count += 1
        audio_base64 = text_to_speech(analysis_result, st.session_state.response_count)
        play_audio(audio_base64, st.session_state.response_count)

    # Interaction Section
    st.subheader("Ask a question (Text or Upload Audio)")

    # Text Input for Questions
    user_text_input = st.text_input("Type your question here:", key="text_question")
    if user_text_input and encoded_image:
        ai_response = analyze_image_and_voice(user_text_input, model, encoded_image, is_initial_analysis=False)
        st.subheader("AI Response:")
        st.write(ai_response)
        st.session_state.response_count += 1
        response_audio_base64 = text_to_speech(ai_response, st.session_state.response_count)
        play_audio(response_audio_base64, st.session_state.response_count)
    elif user_text_input:
        ai_response = generate_ai_response(user_text_input)
        st.subheader("AI Response:")
        st.write(ai_response)
        st.session_state.response_count += 1
        response_audio_base64 = text_to_speech(ai_response, st.session_state.response_count)
        play_audio(response_audio_base64, st.session_state.response_count)

    # Voice Input for Questions (Uploaded Audio)
    st.subheader("Or upload an audio file to ask a question:")
    user_uploaded_voice_input = transcribe_uploaded_audio()
    if user_uploaded_voice_input:
        st.subheader("Transcription (Uploaded Audio):")
        st.write(user_uploaded_voice_input)
        if encoded_image:
            ai_uploaded_voice_response = analyze_image_and_voice(user_uploaded_voice_input, model, encoded_image, is_initial_analysis=False)
        else:
            ai_uploaded_voice_response = generate_ai_response(user_uploaded_voice_input)
        st.subheader("AI Response:")
        st.write(ai_uploaded_voice_response)
        st.session_state.response_count += 1
        uploaded_voice_audio_base64 = text_to_speech(ai_uploaded_voice_response, st.session_state.response_count)
        play_audio(uploaded_voice_audio_base64, st.session_state.response_count)

if __name__ == "__main__":
    main()
