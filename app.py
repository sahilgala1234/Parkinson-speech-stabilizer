
import os
import io
import base64
from flask import Flask, render_template, request, jsonify
from google.cloud import speech
from google.cloud import texttospeech
from google.oauth2 import service_account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Explicit Credential Setup
CREDENTIALS_FILE = "credentials.json"
credentials = None

if os.path.exists(CREDENTIALS_FILE):
    try:
        credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
        print(f"Successfully loaded credentials from {CREDENTIALS_FILE}")
    except Exception as e:
        print(f"Error loading credentials file: {e}")
else:
    print(f"WARNING: {CREDENTIALS_FILE} not found in {os.getcwd()}")

app = Flask(__name__)

def transcribe_audio(audio_content):
    """Transcribes speech using Google Cloud Speech-to-Text."""
    # Pass credentials explicitly
    if credentials:
        client = speech.SpeechClient(credentials=credentials)
    else:
        client = speech.SpeechClient() # Fallback to default auth

    audio = speech.RecognitionAudio(content=audio_content)
    
    # Configure for typical web audio (WebM or Wav)
    # Using 'medical_conversation' or 'latest_long' with boosted confidence for stability
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS, 
        sample_rate_hertz=48000, 
        language_code="en-US",
        model="latest_long", 
        use_enhanced=True,
        # enable_automatic_punctuation=True,
    )


    try:
        response = client.recognize(config=config, audio=audio)
    except Exception as e:
        print(f"First attempt failed: {e}. Trying default configuration.")
        # Sometimes WebM comes as linear16 or other formats effectively
        config = speech.RecognitionConfig(
            language_code="en-US",
            model="default"
        )
        response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "
    
    return transcript.strip()

def synthesize_text(text, voice_name="en-US-Studio-M"):
    """Synthesizes text to speech using Google Cloud Text-to-Speech."""
    # Pass credentials explicitly
    if credentials:
        client = texttospeech.TextToSpeechClient(credentials=credentials)
    else:
        client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request
    # "Studio" voices are higher quality.
    # language_code = "-".join(voice_name.split("-")[:2])
    name = voice_name
    # Extract language code dynamically (e.g., "en-GB-Neural2-B" -> "en-GB")
    language_code = "-".join(name.split("-")[:2])

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=name
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.9, # Slightly slower for better clarity for listeners
        volume_gain_db=1.0 # Slight boost
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response.audio_content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio data provided'}), 400
    
    audio_file = request.files['audio_data']
    audio_content = audio_file.read()

    # 1. Transcribe
    try:
        transcript = transcribe_audio(audio_content)
        print(f"Transcript: {transcript}")
        
        if not transcript:
             return jsonify({'error': 'Could not understand audio', 'transcript': ''}), 400

    except Exception as e:
        print(f"STT Error: {e}")
        return jsonify({'error': f"Speech recognition failed: {str(e)}"}), 500

    # 2. Synthesize
    try:
        # Get selected voice from form data or default
        voice_name = request.form.get('voice_name', 'en-US-Studio-M')
        
        output_audio = synthesize_text(transcript, voice_name)
        
        # Encode to base64 for easy transport
        audio_b64 = base64.b64encode(output_audio).decode('utf-8')
        
        return jsonify({
            'transcript': transcript,
            'audio_content': audio_b64
        })

    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({'error': f"Speech synthesis failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
