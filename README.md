# Manim Video Generation Server

An AI-powered Flask server that generates educational videos using Manim animations, Gemini AI content generation, ElevenLabs text-to-speech, and Cloudinary hosting.

## Features

- 🎬 **AI-Generated Animations**: Custom Manim animations created by Gemini AI for each topic
- 🗣️ **Professional Voice-Over**: High-quality audio using ElevenLabs TTS
- ☁️ **Cloud Hosting**: Videos automatically uploaded to Cloudinary CDN
- 🎯 **30-Second Format**: Perfect for social media and quick learning
- 🔄 **Audio/Video Sync**: Automatic synchronization of audio and video lengths

## API Endpoints

### `POST /generate-video`

Generate a complete educational video for any topic.

**Request:**

```json
{
  "topic": "Quantum Physics"
}
```

**Response:**

```json
{
  "success": true,
  "video_url": "https://res.cloudinary.com/...",
  "topic": "Quantum Physics",
  "transcript": "Generated transcript...",
  "explanation_points": ["Point 1", "Point 2", "Point 3"],
  "duration": "~30 seconds"
}
```

### `GET /health`

Health check endpoint.

### `GET /api-status`

Check the status of all configured API keys.

## Local Development

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd manim-server
   ```

2. **Set up Python virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

5. **Run the server**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5001`

## Required API Keys

### Gemini AI (Google)

- Get from: https://makersuite.google.com/app/apikey
- Used for: Content generation, transcripts, and animation code

### ElevenLabs

- Get from: https://elevenlabs.io/app/settings/api-keys
- Used for: Text-to-speech audio generation

### Cloudinary

- Get from: https://cloudinary.com/console
- Used for: Video hosting and CDN

## Deployment

### Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Render

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy automatically

## Environment Variables

```bash
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
PORT=5001
```

## Dependencies

- **Flask**: Web framework
- **Manim**: Mathematical animation engine
- **Google Generative AI**: Content and animation generation
- **ElevenLabs**: Text-to-speech synthesis
- **Cloudinary**: Video hosting
- **FFmpeg-python**: Video/audio processing

## License

MIT License
