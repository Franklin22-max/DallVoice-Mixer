# 🎙️ DallVoice Mixer

**DallVoice Mixer** is a dynamic, high-performance Python application for synchronized multi-speaker audio mixing and real-time visualization.

Built with a **mobile-first (9:20)** aesthetic, it lets you manage up to **5 speaker profiles**, each with its own audio stream, visual feedback, and independent controls.

Whether you're simulating a podcast, group conversation, or testing multi-track audio, DallVoice delivers a sleek **glass-morphism UI** that handles the complexity smoothly.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![UI](https://img.shields.io/badge/UI-PyQt5-green.svg)
![Audio](https://img.shields.io/badge/Audio-Pydub%20%7C%20SoundDevice-orange.svg)

---

## ✨ Key Features

### 🎯 Dynamic Circular UI
Profiles automatically rearrange and resize based on active speakers for a clean, centered layout.

### 🌟 Massive Glow Visualization
Real-time Voice Activity Detection (VAD) creates glowing auras around active speakers.

### 🔄 Hot-Audio Loading
Add speakers or audio while playback is running — tracks auto-sync with the current timeline.

### ⚙️ Advanced Management Menu
- 👁️ Visibility Toggle (audio continues playing)
- 🔊 Individual Volume Control (0–100%)
- 🔇 Mute/Unmute per speaker
- ✏️ Inline Renaming (double-click profile)
- 🎨 Light/Dark Mode toggle

---

## 🛠️ Technologies Used

- **Python 3.10+**
- **PyQt5** — GUI, animations, custom widgets  
- **Pydub** — audio processing  
- **NumPy** — precise mixing & sync  
- **Sounddevice** — low-latency playback  
- **FFmpeg** — audio decoding backend  

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python **3.8+**

---

### 2. Install FFmpeg

**Windows**
- Download from https://www.gyan.dev/ffmpeg/builds/
- Extract and add `bin` folder to **System PATH**

**macOS**
```bash
brew install ffmpeg
```

**Linux**
```bash
sudo apt install ffmpeg
```

---

### 3. Clone & Install Dependencies

```bash
git clone https://github.com/yourusername/DallVoiceMixer.git
cd DallVoiceMixer

pip install PyQt5 numpy sounddevice pydub
```

---

### 4. Font Setup

Place this file in the project directory:

```
Rowdy-Regular.ttf
```

If missing, the app will fall back to **Arial**.

---

## 📖 How to Use

### ▶️ Run the App
```bash
python main.py
```

### ➕ Add Profiles
Open the menu (☰) → **+ Add Profile**

### 🎵 Link Audio
Click **Audio** on a profile and select a file

### 🎨 Customize
- Double-click to rename  
- Click profile to add image  

### 🎚️ Mix & Play
- Press **Play (►)**
- Adjust volumes in real-time  

### 👁️ Hide/Show Profiles
Use the eye icon to hide visuals while keeping audio active

---

## ⚠️ Important Notes

- 🔒 **Streaming Lock**  
  Profiles cannot be deleted during playback

- 🔊 **Volume Normalization**  
  Prevents sudden volume jumps when tracks end

---

## 🤝 Contributing

Contributions are welcome!

- Open an **Issue**
- Submit a **Pull Request**

---

## 📄 License

Licensed under the **MIT License** — see `LICENSE` for details.

---

## ❤️

Developed for audio enthusiasts who love control, clarity, and clean UI.