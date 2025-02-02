###🚀 AI Doctor 2.0: Voice & Vision

An AI-powered medical assistant that can analyze images, respond to text and voice queries, and generate speech-based answers. Built with Streamlit, Groq’s LLaMA 3, and ElevenLabs, this app offers a seamless experience for interactive AI-driven medical insights.

🌟 Features

✅ Image Analysis – Upload an image (e.g., skin conditions, X-rays), and AI will describe it.
✅ Voice Interaction – Speak your question, and AI will listen, analyze, and respond.
✅ Text-to-Speech (TTS) – Get AI-generated responses read aloud in a natural voice.
✅ Speech-to-Text (STT) – Convert voice queries into text using Google Speech Recognition.
✅ Powered by AI – Utilizes LLaMA 3.2-90B Vision for powerful medical insights.

🛠 Tech Stack

🔹 Streamlit – Interactive UI for easy access.
🔹 Groq API – AI processing with LLaMA 3 models.
🔹 ElevenLabs API – High-quality speech synthesis.
🔹 Google Speech Recognition – Real-time voice transcription.
🔹 Pydub & FFmpeg – Audio processing & conversion.

🚀 Installation

1️⃣ Clone the Repository

git clone https://github.com/yourusername/ai-doctor-2.0.git
cd ai-doctor-2.0

2️⃣ Install Dependencies

Ensure Python 3.8+ is installed, then run:

pip install -r requirements.txt

3️⃣ Set Up API Keys

Create a .env file OR a config.toml file with your API keys:

Option 1: .env File

GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
KITS_AI_API_KEY=your_kits_ai_api_key

Option 2: config.toml File

GROQ_API_KEY = "your_groq_api_key"
ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
KITS_AI_API_KEY = "your_kits_ai_api_key"

4️⃣ Run the App

streamlit run app.py

📸 How It Works

1️⃣ Upload an Image – AI analyzes and describes it.
2️⃣ Ask a Question – Type or speak your question.
3️⃣ Get a Response – AI provides a text answer.
4️⃣ Hear the Answer – AI reads the response aloud.

📌 Requirements
	•	Python 3.8+
	•	FFmpeg (for audio processing)
	•	Windows: Install from ffmpeg.org and add to PATH
	•	Linux/macOS:

sudo apt install ffmpeg  # Debian/Ubuntu
brew install ffmpeg  # macOS

🔥 Example Usage

📷 Image Analysis

Upload a picture of a rash or X-ray, and AI will analyze the condition.

🎤 Voice Interaction

Press the “Ask Using Voice” button, and AI will listen, process, and respond.

📝 Text Queries

Type a medical question, and AI will generate an intelligent response.

🎤 Audio & Speech Capabilities
	•	Uses Google Speech Recognition for voice-to-text.
	•	Converts text responses into natural-sounding AI speech with ElevenLabs.
	•	Saves AI-generated speech as an MP3 file for playback.

🎯 Roadmap

✅ Current Features:
	•	Image recognition
	•	Text & voice queries
	•	AI-powered responses
	•	Speech synthesis

🔜 Future Plans:
	•	Medical chatbot with follow-up questions
	•	Multi-language support
	•	More AI models for specialized analysis

🛡 Security Warning

🚨 Never share API keys publicly! If this is your first time using API keys, store them safely in .env or config.toml.

🤝 Contributing

Want to improve AI Doctor 2.0? Contributions are welcome!
	1.	Fork this repo
	2.	Create a new branch
	3.	Make your changes
	4.	Submit a pull request


🎤 Connect with Me

📧 Email: avi.hm24@gmail.com


💡 AI Doctor 2.0 – Bringing AI & Healthcare Together! 🚀
