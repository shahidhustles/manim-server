import os
import tempfile
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import elevenlabs
from elevenlabs import Voice, VoiceSettings
import cloudinary
import cloudinary.uploader
import ffmpeg
from manim import *
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure APIs
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
elevenlabs.set_api_key(os.getenv("ELEVENLABS_API_KEY"))

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


class TopicExplanationScene(Scene):
    def __init__(self, topic, explanation_points, **kwargs):
        self.topic = topic
        self.explanation_points = explanation_points
        super().__init__(**kwargs)

    def construct(self):
        # Title
        title = Text(self.topic, font_size=48, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title), run_time=1)

        # Main content area
        content_group = VGroup()

        # Create explanation points
        points = []
        for i, point in enumerate(
            self.explanation_points[:3]
        ):  # Limit to 3 points for 30 seconds
            point_text = Text(f"• {point}", font_size=28, color=WHITE)
            points.append(point_text)

        # Arrange points vertically
        points_group = VGroup(*points)
        points_group.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        points_group.next_to(title, DOWN, buff=1)

        # Animate points appearing one by one
        for i, point in enumerate(points):
            self.play(FadeIn(point), run_time=1.5)
            if i < len(points) - 1:
                self.wait(0.5)

        # Add some visual elements
        if len(points) > 0:
            # Create a box around the content
            box = SurroundingRectangle(points_group, color=YELLOW, buff=0.3)
            self.play(Create(box), run_time=1)

        # Hold the final scene
        self.wait(2)


def generate_explanation_points(topic):
    """Generate explanation points using Gemini API"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-002")
        prompt = f"""
        Create a concise educational explanation for the topic: "{topic}"
        
        Provide exactly 3 key points that explain this topic clearly and simply.
        Each point should be:
        - One sentence long
        - Easy to understand
        - Educational and informative
        - Suitable for a 30-second video
        
        Format your response as a simple list with each point on a new line, no numbering or bullets.
        """

        response = model.generate_content(prompt)
        points = [
            line.strip() for line in response.text.strip().split("\n") if line.strip()
        ]
        return points[:3]  # Ensure only 3 points
    except Exception as e:
        logger.error(f"Error generating explanation points: {e}")
        return [
            f"{topic} is an important concept to understand",
            f"Learning about {topic} helps build foundational knowledge",
            f"Understanding {topic} opens doors to advanced topics",
        ]


def generate_transcript(topic, explanation_points):
    """Generate a natural transcript using Gemini API"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-002")
        points_text = "\n".join([f"- {point}" for point in explanation_points])

        prompt = f"""
        Create a natural, engaging 30-second video transcript about "{topic}".
        
        Key points to cover:
        {points_text}
        
        Requirements:
        - Should be exactly 30 seconds when spoken (approximately 75-90 words)
        - Natural, conversational tone
        - Educational but engaging
        - Clear and easy to follow
        - No stage directions or formatting
        - Just the spoken words
        
        Make it sound like an enthusiastic teacher explaining the concept.
        """

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating transcript: {e}")
        return f"Welcome to this quick explanation of {topic}. This is an important concept that helps us understand fundamental principles. Let's explore the key ideas that make this topic essential for learning."


def generate_audio(transcript, output_path):
    """Generate audio using ElevenLabs API"""
    try:
        import requests

        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"

        headers = {
            "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
            "Content-Type": "application/json",
        }

        data = {
            "text": transcript,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True,
            },
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            logger.error(
                f"ElevenLabs API error: {response.status_code} - {response.text}"
            )
            return False

    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        return False


def generate_manim_code(topic, explanation_points):
    """Generate Manim animation code using Gemini API"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-002")
        points_text = "\n".join([f"- {point}" for point in explanation_points])

        prompt = f"""
        Create a professional Manim animation code for an educational video about "{topic}".
        
        Key points to animate:
        {points_text}
        
        CRITICAL CONSTRAINTS:
        - Create a class called TopicScene that extends Scene
        - Animation should be exactly 30 seconds long
        - NEVER use ImageMobject, SVGMobject, or any external files
        - ONLY use built-in Manim objects: Text, Circle, Rectangle, Square, Triangle, Arrow, Line, Dot, etc.
        - ALL coordinates must be 3D: use UP, DOWN, LEFT, RIGHT, or [x, y, 0] format
        - NEVER use 2D coordinates like [x, y] - always include the z-component
        - For Polygon, use format: Polygon([x1, y1, 0], [x2, y2, 0], [x3, y3, 0])
        - No external dependencies or file references
        
        SCENE MANAGEMENT (VERY IMPORTANT):
        - Use FadeOut() to remove elements before introducing new ones
        - Use self.clear() to clear the entire scene when transitioning between major sections
        - Don't overcrowd scenes - remove old elements before adding new ones
        - Each explanation point should have its own clean section
        - Example: self.play(FadeOut(old_group)) before self.play(FadeIn(new_group))
        
        Requirements:
        - Use engaging animations like Write, FadeIn, GrowFromCenter, Create, Transform, etc.
        - Include colorful visual elements (different colors for different concepts)
        - Add geometric shapes, arrows, or diagrams relevant to the topic
        - Use proper timing with self.wait() between animations
        - Make it visually appealing and educational
        - Include intro animation and conclusion
        - Use professional typography and spacing
        
        Animation Structure:
        1. Engaging intro (2-3 seconds)
        2. Topic title with decorative elements (3-4 seconds)
        3. Clear previous elements, then animated explanation point 1 (6-7 seconds)
        4. Clear previous elements, then animated explanation point 2 (6-7 seconds)  
        5. Clear previous elements, then animated explanation point 3 (6-7 seconds)
        6. Clear and show conclusion with call-to-action (3-4 seconds)
        
        Visual Guidelines:
        - Use colors: BLUE, GREEN, ORANGE, PURPLE, YELLOW, RED, GOLD
        - Add shapes like Circle, Rectangle, Square, Triangle, Arrow, Line when relevant
        - Use VGroup to organize elements for easy clearing
        - Include borders, underlines, or decorative elements
        - Make text readable with proper font sizes
        - Create visual metaphors using basic shapes
        - Example coordinates: ORIGIN, UP*2, DOWN*1.5, LEFT*3, RIGHT*2.5, [1, 2, 0]
        
        Scene Clearing Examples:
        ```python
        # Clear everything before new section
        self.clear()
        
        # Or clear specific elements
        self.play(FadeOut(title_group), FadeOut(decorations))
        
        # Or fade out a VGroup
        old_content = VGroup(text1, shape1, arrow1)
        self.play(FadeOut(old_content))
        ```
        
        Example reference (adapt this style):
        ```python
        from manim import *
        
        class ArchimedesPrinciple(Scene):
            def construct(self):
                # Intro title
                title = Text("Hello jury at InnoHack 2.0!", font_size=36)
                self.play(Write(title))
                self.wait(1)
                self.play(FadeOut(title))
        
                # Water container
                water = Rectangle(width=4, height=2, color=BLUE, fill_opacity=0.5)
                water.move_to(DOWN * 1.5)
        
                # Object (cube)
                cube = Square(side_length=0.6, fill_color=GREY, fill_opacity=1)
                cube.move_to(UP * 2)
        
                # Buoyant force arrow
                arrow = Arrow(start=DOWN, end=UP, color=YELLOW)
                arrow.next_to(cube, DOWN)
        
                # Labels
                arch_label = Text("Archimedes' Principle", font_size=28).to_edge(UP)
                force_label = Text("Buoyant Force", font_size=24).next_to(arrow, RIGHT)
        
                # Scene animation
                self.play(Create(water))
                self.play(Create(cube))
                self.wait(0.5)
                self.play(cube.animate.move_to(DOWN * 0.5), run_time=1.5)
                self.play(GrowArrow(arrow), Write(force_label), run_time=1)
                self.play(Write(arch_label))
                self.wait(2)
        ```
        
        Now create a similar engaging animation for "{topic}" that incorporates the explanation points naturally into visual elements. Be creative and make it topic-specific!
        
        IMPORTANT: Only return the Python code, no explanations or markdown formatting.
        """

        response = model.generate_content(prompt)

        # Clean the response - remove markdown formatting if present
        code = response.text.strip()
        if code.startswith("```python"):
            code = code[9:]  # Remove ```python
        if code.startswith("```"):
            code = code[3:]  # Remove ```
        if code.endswith("```"):
            code = code[:-3]  # Remove ending ```

        return code.strip()
    except Exception as e:
        logger.error(f"Error generating Manim code: {e}")
        # Fallback to a simple animation
        return f"""
from manim import *

class TopicScene(Scene):
    def construct(self):
        # Intro
        intro = Text("Educational Hub", font_size=32, color=GOLD)
        self.play(Write(intro))
        self.wait(0.5)
        self.play(FadeOut(intro))
        
        # Title
        title = Text("{topic}", font_size=44, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title), run_time=1.5)
        
        # Points
        points = [
            Text("• {explanation_points[0] if len(explanation_points) > 0 else 'Key concept'}", font_size=26, color=GREEN),
            Text("• {explanation_points[1] if len(explanation_points) > 1 else 'Important details'}", font_size=26, color=ORANGE),
            Text("• {explanation_points[2] if len(explanation_points) > 2 else 'Applications'}", font_size=26, color=PURPLE)
        ]
        
        points_group = VGroup(*points)
        points_group.arrange(DOWN, aligned_edge=LEFT, buff=0.7)
        points_group.next_to(title, DOWN, buff=1.5)
        
        for i, point in enumerate(points):
            self.play(FadeIn(point, shift=RIGHT), run_time=1.2)
            self.wait(0.3)
        
        # Border
        border = SurroundingRectangle(points_group, color=YELLOW, buff=0.5)
        self.play(Create(border), run_time=1)
        
        # Conclusion
        conclusion = Text("Keep Learning!", font_size=28, color=GREEN)
        conclusion.to_edge(DOWN)
        self.play(FadeIn(conclusion, shift=UP))
        self.wait(2)
"""


def create_manim_video(topic, explanation_points, output_path):
    """Create video using AI-generated Manim code"""
    try:
        # Generate Manim code using AI
        logger.info("Generating Manim animation code...")
        manim_code = generate_manim_code(topic, explanation_points)

        # Create a temporary scene file
        scene_file = os.path.join(
            tempfile.gettempdir(),
            f"scene_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
        )

        with open(scene_file, "w") as f:
            f.write(manim_code)

        # Render the scene
        import subprocess
        import shutil

        # Find manim executable dynamically
        manim_path = shutil.which("manim")
        if not manim_path:
            # Fallback: try common locations
            possible_paths = [
                "/opt/venv/bin/manim",  # Railway/Render common path
                "/usr/local/bin/manim",  # System install
                "manim",  # Hope it's in PATH
            ]
            for path in possible_paths:
                if shutil.which(path) or os.path.exists(path):
                    manim_path = path
                    break
            else:
                manim_path = "manim"  # Last resort - let subprocess handle the error

        logger.info(f"Using manim executable: {manim_path}")

        cmd = [
            manim_path,
            "-qm",  # Medium quality
            "--format",
            "mp4",
            scene_file,
            "TopicScene",
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=tempfile.gettempdir()
        )

        if result.returncode == 0:
            # Find the generated video file
            media_dir = os.path.join(
                tempfile.gettempdir(),
                "media",
                "videos",
                os.path.basename(scene_file)[:-3],
                "720p30",
            )
            video_file = os.path.join(media_dir, "TopicScene.mp4")

            if os.path.exists(video_file):
                # Copy to desired output path
                import shutil

                shutil.copy2(video_file, output_path)

                # Cleanup
                os.remove(scene_file)
                return True

        logger.error(f"Manim rendering failed: {result.stderr}")
        return False

    except Exception as e:
        logger.error(f"Error creating Manim video: {e}")
        return False


def combine_video_audio(video_path, audio_path, output_path):
    """Combine video and audio using ffmpeg with automatic synchronization"""
    try:
        # Get video duration
        video_probe = ffmpeg.probe(video_path)
        video_duration = float(video_probe["streams"][0]["duration"])

        # Get audio duration
        audio_probe = ffmpeg.probe(audio_path)
        audio_duration = float(audio_probe["streams"][0]["duration"])

        logger.info(
            f"Video duration: {video_duration:.2f}s, Audio duration: {audio_duration:.2f}s"
        )

        # Calculate speed adjustment for audio to match video
        audio_speed = audio_duration / video_duration

        # Apply speed adjustment to audio if needed
        if abs(audio_speed - 1.0) > 0.1:  # Only adjust if difference > 10%
            logger.info(f"Adjusting audio speed by {audio_speed:.2f}x to match video")
            audio_input = ffmpeg.input(audio_path).filter("atempo", audio_speed)
        else:
            logger.info(
                "Audio and video lengths are close enough, no speed adjustment needed"
            )
            audio_input = ffmpeg.input(audio_path)

        # Combine video and adjusted audio
        (
            ffmpeg.output(
                ffmpeg.input(video_path),
                audio_input,
                output_path,
                vcodec="copy",
                acodec="aac",
                shortest=None,
            )
            .overwrite_output()
            .run(quiet=True)
        )
        return True
    except Exception as e:
        logger.error(f"Error combining video and audio: {e}")
        return False


def upload_to_cloudinary(file_path, public_id):
    """Upload video to Cloudinary"""
    try:
        result = cloudinary.uploader.upload(
            file_path,
            resource_type="video",
            public_id=public_id,
            overwrite=True,
            quality="auto:good",
            format="mp4",
        )
        return result.get("secure_url")
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {e}")
        return None


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/generate-video", methods=["POST"])
def generate_video():
    """Main endpoint to generate educational video"""
    try:
        data = request.get_json()
        topic = data.get("topic")

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        logger.info(f"Starting video generation for topic: {topic}")

        # Create temporary directory for this request
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, "video.mp4")
        audio_path = os.path.join(temp_dir, "audio.wav")
        final_path = os.path.join(temp_dir, "final_video.mp4")

        try:
            # Step 1: Generate explanation points
            logger.info("Generating explanation points...")
            explanation_points = generate_explanation_points(topic)

            # Step 2: Generate transcript
            logger.info("Generating transcript...")
            transcript = generate_transcript(topic, explanation_points)

            # Step 3: Generate video with Manim
            logger.info("Creating video with Manim...")
            if not create_manim_video(topic, explanation_points, video_path):
                return jsonify({"error": "Failed to create video"}), 500

            # Step 4: Generate audio
            logger.info("Generating audio...")
            if not generate_audio(transcript, audio_path):
                return jsonify({"error": "Failed to generate audio"}), 500

            # Step 5: Combine video and audio
            logger.info("Combining video and audio...")
            if not combine_video_audio(video_path, audio_path, final_path):
                return jsonify({"error": "Failed to combine video and audio"}), 500

            # Step 6: Upload to Cloudinary
            logger.info("Uploading to Cloudinary...")
            public_id = f"educational_videos/{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            video_url = upload_to_cloudinary(final_path, public_id)

            if not video_url:
                return jsonify({"error": "Failed to upload video"}), 500

            logger.info(f"Video generation completed successfully: {video_url}")

            return jsonify(
                {
                    "success": True,
                    "video_url": video_url,
                    "topic": topic,
                    "transcript": transcript,
                    "explanation_points": explanation_points,
                    "duration": "~30 seconds",
                }
            )

        finally:
            # Cleanup temporary files
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        logger.error(f"Error in generate_video: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api-status", methods=["GET"])
def api_status():
    """Check the status of all required API keys"""
    status = {
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "elevenlabs": bool(os.getenv("ELEVENLABS_API_KEY")),
        "cloudinary": bool(
            os.getenv("CLOUDINARY_CLOUD_NAME")
            and os.getenv("CLOUDINARY_API_KEY")
            and os.getenv("CLOUDINARY_API_SECRET")
        ),
    }

    all_configured = all(status.values())

    return jsonify(
        {
            "all_apis_configured": all_configured,
            "api_status": status,
            "missing_keys": [
                key for key, configured in status.items() if not configured
            ],
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
