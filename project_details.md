# Project Details: AI Speech Stabilizer

## List of Google Technologies Used
1.  **Google Cloud Platform (GCP)**: The underlying infrastructure for managing APIs and authentication.
2.  **Google Cloud Speech-to-Text API**: Used to convert the user's spoken audio into text.
3.  **Google Cloud Text-to-Speech API**: Used to synthesize the text into clear, stabilized audio.
4.  **Google Fonts**: Utilized the "Outfit" font for a modern, accessible UI.
5.  **Google Cloud Run**: Recommended platform for serverless deployment (Docker containerization provided).

## List of Google AI Tools Integrated
1.  **Speech-to-Text "Latest_Long" Model**: An advanced ASR model optimized for longer, natural speech, capable of handling variable audio quality better than standard models.
2.  **Text-to-Speech "Studio" & "Neural2" Voices**: State-of-the-art voice synthesis models powered by DeepMind's WaveNet technology to produce human-like, expressive speech.

## Solution Description
The **AI Speech Stabilizer** is a web-based communication aid designed for individuals with Parkinson’s disease who experience hypophonia (soft voice) and dysarthria (slurred speech). By leveraging **Google Cloud’s Speech-to-Text API**, the application captures and accurately transcribes imperfect speech patterns. It then utilizes **Google Cloud’s Text-to-Speech API** to instantly regenerate the message in a clear, amplified, and authoritative voice. This "voice restoration" tool empowers users to be heard and understood effectively, bridging the gap between their communicative intent and vocal limitations through a seamless, accessible interface.
