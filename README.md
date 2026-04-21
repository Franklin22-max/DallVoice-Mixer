This is a professional and engaging README.md file tailored for your DallVoice Mixer project. It highlights the app's sophisticated features and provides clear instructions for users on GitHub.
🎙️ DallVoice Mixer
DallVoice Mixer is a dynamic, high-performance Python application designed for synchronized multi-speaker audio mixing and real-time visualization. Built with a "mobile-first" aesthetic (9:20 aspect ratio), it allows users to manage up to 5 speaking profiles, each with its own dedicated audio stream, visual feedback, and independent controls.
Whether you are simulating a podcast, a group conversation, or testing multi-track audio, DallVoice provides a sleek, "glass-morphism" inspired UI to handle the complexity for you.
![alt text](https://img.shields.io/badge/Python-3.8+-blue.svg)

![alt text](https://img.shields.io/badge/UI-PyQt5-green.svg)

![alt text](https://img.shields.io/badge/Audio-Pydub%20%7C%20SoundDevice-orange.svg)
✨ Key Features
Dynamic Circular UI: Profiles automatically rearrange and resize based on the number of active speakers to ensure a clean, centered look.
Massive Glow Visualization: Real-time Voice Activity Detection (VAD) triggers a vibrant glowing aura around speaker profiles when they are talking.
Hot-Audio Loading: Add a new speaker or link an audio file while the stream is already playing. New tracks automatically sync and skip ahead to match the current master playback time.
Advanced Management Menu:
Visibility Toggle: Hide a profile from the screen while its audio continues to play (remaining profiles automatically fill the gap).
Individual Volume Control: Independent sliders (0-100%) for every speaker.
Mute/Unmute: Instantly silence specific tracks without stopping the session.
Inline Renaming: Double-click any profile circle to rename the speaker on the fly.
Appearance Customization: Toggle between Light and Dark modes via the settings menu.
🛠️ Technologies Used
Python 3.10+
PyQt5: For the sophisticated GUI, property animations, and custom-painted widgets.
Pydub: For high-level audio manipulation and file format decoding.
NumPy: For mathematical precision in audio mixing and sample-level synchronization.
Sounddevice: Low-latency, professional-grade audio output streaming.
FFmpeg: Required as the backend for Pydub to process various audio formats (.mp3, .wav, .ogg).
🚀 Installation & Setup
1. Prerequisites
Ensure you have Python 3.8 or higher installed.
2. Install FFmpeg
The app requires FFmpeg to handle audio files.
Windows: Download from gyan.dev, extract it, and add the bin folder to your System PATH.
macOS: brew install ffmpeg
Linux: sudo apt install ffmpeg
3. Clone and Install Dependencies
code
Bash
# Clone the repository
git clone https://github.com/yourusername/DallVoiceMixer.git
cd DallVoiceMixer

# Install Python libraries
pip install PyQt5 numpy sounddevice pydub
4. Font Setup
The app uses the Rowdy font for its modern look.
Place Rowdy-Regular.ttf in the same directory as main.py. If missing, the app will safely fall back to Arial.
📖 How to Use
Run the App:
code
Bash
python main.py
Add Profiles: Open the Management Menu (☰) and click + Add Profile.
Link Audio: Click Audio on a speaker's card to choose an MP3 or WAV file.
Customize: Double-click a profile circle to change the name or click the circle to upload a profile image.
Mix & Play: Hit the Play (►) button. Use the sliders in the side menu to adjust levels in real-time.
Hide/Show: Use the eye icon (👁️) to hide profiles you don't need to see while keeping their audio active.
⚠️ Important Notes
Streaming Lock: To ensure stability, the app prevents deleting a profile while audio is currently streaming. Stop the playback to remove a speaker.
Volume Normalization: The app uses a fixed gain divisor based on the tracks present at the start of the session. This prevents volume "jumping" when one track finishes before others.
🤝 Contributing
Contributions are welcome! Feel free to open an Issue or submit a Pull Request to improve the mixing logic or UI animations.
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
Developed with ❤️ for audio enthusiasts.