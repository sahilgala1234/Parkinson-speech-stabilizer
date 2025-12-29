let mediaRecorder;
let audioChunks = [];
const recordBtn = document.getElementById('recordBtn');
const btnText = document.getElementById('btnText');
const statusText = document.getElementById('status');
const transcriptText = document.getElementById('transcriptText');
const audioPlayer = document.getElementById('audioPlayer');
const voiceSelect = document.getElementById('voiceSelect');

// Check for MediaRecorder support
if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    statusText.textContent = "Error: Audio recording not supported in this browser.";
    recordBtn.disabled = true;
    recordBtn.style.background = "#ccc";
}

let isRecording = false;

// Handle Button Interactions (Mouse & Touch)
// We want "Hold to Record" behavior for desktop, but "Toggle" might be better for accessiblity?
// Let's stick to "Toggle" (Click to start, Click to stop) for better accessibility for shaky hands.
// Changing text to "Tap to Speak" in logic if needed, but UI says "Hold".
// Actually, for Parkinson's, holding might be hard due to tremors.
// Let's implement TOGGLE behavior: One tap to start, one tap to end.

btnText.textContent = "Tap to Speak";

recordBtn.addEventListener('click', () => {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            processAudio();
        };

        mediaRecorder.start();
        isRecording = true;
        recordBtn.classList.add('recording');
        btnText.textContent = "Tap to Stop";
        statusText.textContent = "Listening...";
        transcriptText.textContent = "...";

    } catch (err) {
        console.error("Error accessing microphone:", err);
        statusText.textContent = "Error: Could not access microphone.";
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.classList.remove('recording');
        btnText.textContent = "Tap to Speak";
        statusText.textContent = "Processing...";

        // Stop all tracks to release mic
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
}

async function processAudio() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('audio_data', audioBlob, 'recording.webm');
    formData.append('voice_name', voiceSelect.value);

    try {
        const response = await fetch('/process_audio', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || 'Server error');
        }

        const data = await response.json();

        // Update UI
        transcriptText.textContent = data.transcript;
        statusText.textContent = "Playing stabilized speech";

        // Play Audio
        const audioSrc = `data:audio/mp3;base64,${data.audio_content}`;
        audioPlayer.src = audioSrc;
        audioPlayer.play();

        // Reset status after playback (rough estimate or event listener)
        audioPlayer.onended = () => {
            statusText.textContent = "Ready";
        };

    } catch (error) {
        console.error("Processing failed:", error);
        statusText.textContent = "Error: " + error.message;
        transcriptText.textContent = "Failed to process speech.";
    }
}
