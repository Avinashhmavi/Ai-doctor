# 🩺👨‍⚕️AI Doctor 2.0: Voice and Vision

Welcome to **AI Doctor 2.0**, a cutting-edge multimodal AI application that combines **image analysis**, **text-to-speech**, **speech-to-text**, and **natural language understanding** into one seamless platform. Whether you're diagnosing conditions from images, asking questions via text or voice, or transcribing audio files, this app empowers you to interact with AI in an intuitive and human-like way.

Live Demo: [AI Doctor 2.0](https://ai-doctor-1.streamlit.app/)

---

## Table of Contents
1. [Features](#features)
2. [Pre-Installation Steps](#pre-installation-steps)
3. [How to Run the App](#how-to-run-the-app)
4. [Application Workflow](#application-workflow)
5. [Dependencies](#dependencies)
6. [Contributing](#contributing)
7. [License](#license)

---

## Features

### 1. **Multimodal Interaction**
   - **Image Analysis**: Upload an image and get detailed insights about its content using advanced vision models.
   - **Text Input**: Ask questions via text and receive AI-generated responses.
   - **Voice Input**: Upload an audio file, transcribe it, and get AI-generated responses.
   - **Speech Output**: Every AI response is converted into lifelike speech using ElevenLabs' high-quality TTS engine.

### 2. **AI-Powered Insights**
   - Analyze medical images or any other visuals for conditions or anomalies.
   - Generate natural language responses based on uploaded images and user queries.

### 3. **Speech-to-Text Transcription**
   - Transcribe audio files (WAV, MP3, M4A) into text using Google Speech Recognition.

### 4. **Customizable Voice Responses**
   - Choose between different voices (e.g., "Aria") and formats for speech output.

### 5. **Streamlit Interface**
   - A clean, modern web-based interface powered by **Streamlit**.
   - Easy-to-use file uploaders, buttons, and interactive elements for a smooth user experience.

---

## Pre-Installation Steps

Before running the application, ensure you have the following prerequisites installed:

### 1. **Python Environment**
   - Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/).

### 2. **Install Dependencies**
   - Clone this repository:
     ```bash
     git clone https://github.com/your-repo/ai-doctor.git
     cd ai-doctor
     ```
   - Create a virtual environment (optional but recommended):
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```
   - Install the required libraries:
     ```bash
     pip install -r requirements.txt
     ```

### 3. **Environment Variables**
   - Create a `.env` file in the root directory of the project and add your API keys:
     ```plaintext
     GROQ_API_KEY=your_groq_api_key_here
     ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
     ```
   - Replace `your_groq_api_key_here` and `your_elevenlabs_api_key_here` with your actual API keys.

### 4. **System Tools**
   - Ensure you have the following tools installed:
     - **Google Speech Recognition**: Automatically included via `speech_recognition`.
     - **Audio Playback**: Streamlit handles audio playback seamlessly.

---

## How to Run the App

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Open the provided local URL in your browser (e.g., `http://localhost:8501`).
3. Follow the instructions in the app interface to analyze images, generate speech, or transcribe audio.

---

## Application Workflow

### Step 1: Image Analysis
   - Upload an image file (JPEG, PNG).
   - The AI will automatically analyze the image and describe its content.
   - Listen to the AI's spoken analysis.

### Step 2: Text-Based Questions
   - Type your question in the text input box.
   - The AI will respond with a detailed answer and convert it into speech.

### Step 3: Voice-Based Questions
   - Upload an audio file (WAV, MP3, M4A).
   - The app will transcribe the audio and generate an AI response.
   - Listen to the AI's spoken response.

---

## Dependencies

The application relies on the following Python libraries:

| Library          | Purpose                          |
|------------------|----------------------------------|
| `streamlit`      | Web interface                   |
| `groq`           | Image analysis and NLP          |
| `elevenlabs`     | High-quality TTS                |
| `speech_recognition` | Speech-to-text transcription |
| `dotenv`         | Load environment variables      |

Install all dependencies using:
```bash
pip install -r requirements.txt
```

---

## Contributing

We welcome contributions to improve this project! Here’s how you can help:
1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature description"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request on GitHub.

---

## Vibrant Description

**AI Doctor 2.0** is not just another AI tool—it's your personal assistant for understanding images, answering questions, and transcribing audio with ease. With its sleek Streamlit interface and robust backend powered by cutting-edge AI models, this application is designed to inspire creativity and efficiency.

Imagine uploading an X-ray image and instantly receiving a detailed diagnosis in both text and speech. Or asking complex questions via voice and getting back clear, concise answers. This app bridges the gap between human interaction and artificial intelligence, making technology accessible to everyone.

Unlock the power of AI today—analyze, speak, and listen like never before!

---
