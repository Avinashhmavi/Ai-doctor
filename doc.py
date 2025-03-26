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

# Initialize session state for storing the diagnosis
if "diagnosis" not in st.session_state:
    st.session_state.diagnosis = None

# Function to encode image to base64
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Function to extract diagnosis from the analysis result
def extract_diagnosis(analysis_result):
    # Simple extraction: look for the "Primary Diagnosis" line
    lines = analysis_result.split('\n')
    for line in lines:
        if "Primary Diagnosis" in line:
            # Extract the diagnosis text (e.g., "Possible stroke or cerebral infarction (confidence level: 80%)")
            diagnosis = line.split(":", 1)[1].strip()
            return diagnosis
    return "unknown condition"

# Function to analyze image and voice input together
def analyze_image_and_voice(user_query, model, encoded_image, is_initial_analysis=True):
    if is_initial_analysis:
        # Define the medical imaging query for initial analysis
        medical_query = """
You are a highly skilled medical imaging expert. First, determine if the uploaded image is related to medical, hospital, or diagnostic purposes. This includes traditional medical imaging (e.g., X-ray, MRI, CT, ultrasound) as well as clinical photographs showing visible medical conditions, such as dermatological issues (e.g., acne, rashes, lesions, or other skin abnormalities), wounds, or other physical signs of illness that a doctor might review. If the image is not medical-related (e.g., a landscape or unrelated object), respond with: "Please insert only a medical image related to hospital or diagnostic purposes for a doctor to review." If it is medical-related, analyze the image as follows:

###  Key Findings
- List primary observations systematically (e.g., presence of lesions, redness, swelling)
- Note any abnormalities with precise descriptions (e.g., type, color, distribution, texture)
- Include measurements if applicable (e.g., size of lesions in mm)
- Describe location, size, shape, and characteristics of findings
- Rate severity: Normal/Mild/Moderate/Severe

### Diagnostic 
- Provide a primary diagnosis with confidence level (e.g., 90% confidence)
- List differential diagnoses in order of likelihood
- Support each diagnosis with observed evidence from the image
- Note any critical or urgent findings (e.g., signs of infection requiring immediate attention)

### Patient-Friendly Explanation
- Explain the findings in simple, clear language that a patient can understand
- Avoid medical jargon or provide clear definitions (e.g., "inflammation" means redness and swelling)
- Include visual analogies if helpful (e.g., "the spots look like small red dots, similar to freckles but raised")
- Address common patient concerns related to these findings (e.g., "Is this contagious?" or "Will it go away on its own?")

Format your response using clear markdown headers and bullet points. Be concise yet thorough.
"""
        full_query = medical_query + f"\n\nUser's additional query: {user_query}" if user_query else medical_query
    else:
        # For follow-up questions, use a prompt that references the stored diagnosis
        diagnosis = st.session_state.diagnosis if st.session_state.diagnosis else "unknown condition"
        full_query = f"""
You are an AI doctor. The patient has already been diagnosed with {diagnosis} based on a medical image analysis. The patient has asked: "{user_query}". Provide a concise, direct answer to their question in simple language, as an AI doctor would, without repeating the full image analysis. If the question requires referencing the image findings, do so briefly. Offer general treatment advice confidently, as a doctor would, and do not include disclaimers about not being able to give advice or prescriptions, since you are acting as an AI doctor in this context.
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
        # Store the diagnosis in session state
        st.session_state.diagnosis = extract_diagnosis(response)
    return response

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
        st.error("Invalid input text for speech conversion.")
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
    st.info("Upload an audio file (MP3 or WAV) for transcription:")
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
                    st.success("Audio uploaded successfully. Processing transcription...")
                    try:
                        transcribed_text = recognizer.recognize_google(audio_data)
                        os.unlink(temp_wav_path)
                        return transcribed_text
                    except sr.UnknownValueError:
                        st.error("Could not understand the audio.")
                        return None
                    except sr.RequestError as e:
                        st.error(f"Could not request results from Google Speech Recognition service; {e}")
                        return None
        except Exception as e:
            st.error(f"Error processing uploaded audio file: {e}")
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

        # Convert analysis result to speech and play automatically with controls
        audio_base64 = text_to_speech(analysis_result)
        play_audio(audio_base64)

    # Interaction Section
    st.subheader("Ask a question (Text or Upload Audio)")

    # Text Input for Questions
    user_text_input = st.text_input("Type your question here:")
    if user_text_input and encoded_image:
        ai_response = analyze_image_and_voice(user_text_input, model, encoded_image, is_initial_analysis=False)
    elif user_text_input:
        ai_response = generate_ai_response(user_text_input)
    else:
        ai_response = None

    if ai_response:
        st.subheader("AI Response:")
        st.write(ai_response)
        response_audio_base64 = text_to_speech(ai_response)
        play_audio(response_audio_base64)

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
        uploaded_voice_audio_base64 = text_to_speech(ai_uploaded_voice_response)
        play_audio(uploaded_voice_audio_base64)

if __name__ == "__main__":
    main()
