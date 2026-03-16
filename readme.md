# 🎮 Genius - Hand Gesture Recognition System

[![License](https://img.shields.io/badge/License-INATEL-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-orange)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-blue)

Welcome to the **Genius Hand Gesture Recognition System**! A comprehensive Python implementation that leverages computer vision and AI to detect and interpret hand gestures in real-time, enabling intuitive control of lamp modules and interactive games.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Applications](#applications)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Hardware Requirements](#hardware-requirements)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Genius system is a sophisticated gesture recognition platform developed at **INATEL CSI Lab** that uses:

- **MediaPipe** for robust hand landmark detection (21 points per hand)
- **OpenCV** for real-time video processing and rendering
- **MQTT** for IoT communication with smart home devices
- **Deep Learning** models for gesture classification

The system supports simultaneous detection of **both left and right hands**, enabling complex multi-hand command sequences for controlling smart devices and playing interactive games.

## ✨ Features

### Core Capabilities

- ✅ **Dual Hand Recognition**: Detects and tracks both left and right hands simultaneously
- ✅ **Real-time Processing**: Achieves smooth 30+ FPS gesture detection and feedback
- ✅ **10 Left-Hand Gestures**: Number selection (1-10) using finger encoding
- ✅ **6 Right-Hand Gestures**: Device control (on/off, dimmer, modes)
- ✅ **MQTT Integration**: Publishes gestures to IoT devices via MQTT broker
- ✅ **Multi-Application Support**: 3 interactive games/applications in one codebase
- ✅ **Environment Configuration**: Flexible setup via `.env` file
- ✅ **Automatic Reconnection**: Camera and MQTT auto-recovery on connection loss
- ✅ **Visual Feedback**: Real-time gesture display on screen for user guidance

### Right-Hand Gestures

| Gesture | Command | Purpose |
|---------|---------|---------|
| **Open Palm** | Turn On | Activate lamp/device |
| **Close Fist** | Turn Off | Deactivate lamp/device |
| **Pinch (Thumb+Index)** | Dimmer Control | Adjust brightness (0-100%) |
| **Pointing** | Show Variables | Display system status |
| **Victory Sign** | Show Graphs | Display visualization |
| **All Fingers** | Reset All | Clear everything |

### Left-Hand Gestures

- Sequential number detection: **1, 2, 3, 4, 5, 6, 7, 8, 9, 10**
- Used to select which lamp/position to control

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│            Hand Gesture Recognition System          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐         ┌──────────────┐        │
│  │   Camera     │─────►   │  MediaPipe   │        │
│  │ (OpenCV)     │         │ Hand Detector│        │
│  └──────────────┘         └──────┬───────┘        │
│                                  │                │
│                           ┌──────▼───────┐       │
│                           │ Left/Right    │       │
│                           │ Recognition   │       │
│                           └──────┬───────┘       │
│                                  │                │
│  ┌──────────────┐         ┌──────▼───────┐       │
│  │ MQTT Broker  │◄────────│ Application   │       │
│  │ (Smart Home) │         │ Logic         │       │
│  └──────────────┘         └───────────────┘       │
│                                  │                │
│  ┌──────────────┐         ┌──────▼───────┐       │
│  │ Smart Lamps  │         │ Display      │       │
│  │ Devices      │◄────────│ Interface    │       │
│  └──────────────┘         └───────────────┘       │
│                                                   │
└─────────────────────────────────────────────────────┘
```

## 🎮 Applications

### 1. **Genius** (Simon Says Game)
An interactive memory game where:
- System displays a random sequence of lights
- Player must repeat the sequence using hand gestures
- Sequence grows after each successful round
- Game ends if player makes a mistake

**Topics**:
- Subscribe: `lamp_module/choice`
- Controls 6 lamps in sequence

### 2. **Jogo da Velha** (Tic Tac Toe)
Multiplayer game with hand gesture input:
- 3x3 board mapped to positions 1-9
- Two players control using hand gestures
- Real-time MQTT communication
- Session-based gameplay

**Topics**:
- Subscribe: `JogoDaVelha/Session1/{PLAYER_ID}/escolha`
- Player ID configurable via `.env`

### 3. **RGB Dimmer Module**
Smart lighting control system:
- Select lamp (1-10) with left hand
- Adjust brightness (0-100%) with right hand pinch
- Real-time RGB light control
- Smooth dimming transitions

**Topics**:
- Subscribe: `rgb_module/dimmer/setLampState`
- Supports PWM dimming values

## 📦 Requirements

### Software
- **Python** 3.8 or higher
- **pip** package manager

### Hardware
- Webcam/USB Camera (minimum 720p resolution recommended)
- **MQTT Broker** (mosquitto or similar)
- **Smart Lamp Module** (with MQTT support)
- Computer with adequate CPU (Intel i5 or equivalent minimum)

### Network
- Local network connection to MQTT broker
- Optional: Remote MQTT access for cloud deployment

## 🚀 Installation

### Step 1: Clone the Repository
```bash
cd c:\Users\alvaro.careli\Documents\Genius
git clone https://github.com/csilabinatel/Genius.git
cd fut_hands_gestures
```

### Step 2: Create Virtual Environment
```bash
# On Windows
./scripts/fut_create_venv.sh myenv

# On Linux/Mac
bash scripts/fut_create_venv.sh myenv
```

### Step 3: Activate Virtual Environment
```bash
# On Windows
./scripts/fut_activate_venv.sh myenv

# On Linux/Mac
source scripts/fut_activate_venv.sh myenv
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- `mediapipe==0.10.9` - Hand pose detection
- `opencv-python` - Computer vision & image processing
- `paho-mqtt` - MQTT client library
- `numpy` - Numerical computing
- `python-dotenv` - Environment variable management

## ⚙️ Configuration

### 1. Configure `.env` file

Create a `.env` file in the project root with your MQTT broker details:

```bash
# MQTT Broker Configuration
MQTT_HOST="192.168.66.11"
MQTT_PORT=1883
MQTT_USER="your_mqtt_user"
MQTT_PASSWORD="your_mqtt_password"

# Application Configuration
PLAYER_ID="jogador1"
TOPIC_GENIUS="lamp_module/choice"
TOPIC_VELHA="JogoDaVelha/Session1/escolha"
TOPIC_DIMMER="rgb_module/dimmer/setLampState"
```

**Configuration Variables**:

| Variable | Type | Description |
|----------|------|-------------|
| `MQTT_HOST` | IP/Hostname | MQTT broker address |
| `MQTT_PORT` | Integer | MQTT broker port (default: 1883) |
| `MQTT_USER` | String | MQTT authentication username |
| `MQTT_PASSWORD` | String | MQTT authentication password |
| `PLAYER_ID` | String | Unique player identifier for multiplayer games |
| `TOPIC_GENIUS` | String | MQTT topic for Genius game |
| `TOPIC_VELHA` | String | MQTT topic for Tic Tac Toe game |
| `TOPIC_DIMMER` | String | MQTT topic for dimmer control |

### 2. Set Up MQTT Broker

**Using Mosquitto** (recommended):

```bash
# Install mosquitto
sudo apt-get install mosquitto mosquitto-clients

# Configure user authentication
sudo mosquitto_passwd -c /etc/mosquitto/passwd csilab

# Update mosquitto config
sudo nano /etc/mosquitto/mosquitto.conf

# Add these lines:
# listener 1883
# allow_anonymous false
# password_file /etc/mosquitto/passwd
```

**Test connection**:
```bash
mosquitto_sub -h 192.168.66.11 -u csilab -P WhoAmI#2024 -t "test"
```

## 💻 Usage

### Start the Application

```bash
# Option 1: Using the main script
./main.sh

# Option 2: Direct Python execution
python3 src/hand_detector/fut_models_main.py
```

### Interactive Menu
```
Escolha o módulo desejado:
1 - Genius
2 - Jogo da VeIA
3 - Dimerizador
> 
```

### Controls During Execution

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `ESC` | Exit full-screen (if enabled) |

### Example Session

```bash
# 1. Activate environment
./scripts/fut_activate_venv.sh myenv

# 2. Start the application
./main.sh

# 3. Select application (e.g., "1" for Genius)
# 4. Position yourself in front of camera
# 5. Left hand: show numbers (1-10)
# 6. Right hand: open palm to turn on, close fist to turn off
# 7. Press 'q' to exit
```

## 📁 Project Structure

```
fut_hands_gestures/
├── src/                                 # Source code
│   ├── api/                            # Game/Application logic
│   │   ├── genius.py                   # Genius game (Simon Says)
│   │   └── jogoDaVelha.py             # Tic Tac Toe game
│   │
│   ├── hand_detector/                  # Core gesture detection
│   │   ├── fut_models_main.py         # Main orchestrator
│   │   ├── config/
│   │   │   └── fut_models_params.yaml # Model parameters
│   │   ├── modules/
│   │   │   ├── fut_hand_detector.py           # Hand landmark detection
│   │   │   ├── fut_gesture_detector.py        # Gesture classification
│   │   │   ├── fut_remote_controller.py       # Gesture processing
│   │   │   ├── camera_capture.py              # Camera abstraction (NEW)
│   │   │   └── mqtt_client.py                 # MQTT abstraction (NEW)
│   │   └── utils/
│   │       ├── fut_enum_hand_utils.py         # Hand enum definitions
│   │       ├── fut_hand_landmarks_utils.py   # Landmark helpers
│   │       └── fut_models_utils.py            # Utility functions
│   │
│   ├── data/                           # Data processing
│   │   ├── fut_main_data.py           # Data pipeline orchestrator
│   │   ├── config/
│   │   ├── modules/
│   │   └── utils/
│   │
│   ├── features/                       # Feature engineering
│   │   ├── fut_main_features.py
│   │   ├── config/
│   │   ├── modules/
│   │   └── utils/
│   │
│   ├── visualization/                  # Plotting & visualization
│   │   ├── fut_visua_main.py
│   │   ├── config/
│   │   ├── modules/
│   │   └── utils/
│   │
│   ├── config/                         # Global configuration
│   │   └── fut_params.yaml
│   │
│   └── utils/
│       └── fut_utils.py
│
├── test/                               # Unit tests
│   └── fut_test.py
│
├── scripts/                            # Utility scripts
│   ├── fut_create_venv.sh             # Create virtual environment
│   ├── fut_activate_venv.sh           # Activate environment
│   ├── fut_git_commit.sh              # Git commit helper
│   ├── fut_add_copyright.sh           # Add copyright headers
│   └── fut_initial_config.sh          # Initial setup
│
├── docs/                               # Documentation
│   ├── 01_initial_configuration.md
│   ├── 02_project_structure.md
│   └── 03_configure_DVC.md
│
├── env/                                # Environment configs
│   └── fut_global_params.yaml
│
├── hardware/                           # Arduino firmware
│   ├── Genius_Module/
│   │   └── Genius_Module.ino
│   └── lampadas_rgb/
│       └── lampadas_rgb.ino
│
├── .env                                # Environment variables (CREATE THIS)
├── .dockerignore
├── .gitignore
├── docker-compose.yaml                # Docker Compose config
├── Dockerfile                         # Container image
├── Jenkinsfile                        # CI/CD pipeline
├── requirements.txt                   # Python dependencies
├── tox.ini                           # Testing configuration
├── sonar-project.properties          # Code quality config
├── dvc.yaml                          # Data version control
├── main.sh                           # Main entry point
└── README.md                         # This file
```

### Key Architectural Components

#### **fut_models_main.py** (Orchestrator)
- Entry point for the application
- Manages menu selection for different games
- Coordinates between camera, gesture detection, and MQTT
- Handles main event loop

#### **camera_capture.py** (Camera Abstraction)
- Encapsulates all camera-related operations
- Handles USB camera connection/disconnection
- Implements auto-reconnection logic
- Computes region-of-interest (ROI) proportionally

#### **mqtt_client.py** (MQTT Abstraction)
- Manages connection to MQTT broker
- Publishes gesture commands
- Handles authentication and reconnection

#### **fut_gesture_detector.py** (Gesture Logic)
- Implements gesture recognition algorithms
- Calculates finger angles and distances
- Determines dimmer values from hand pinches

#### **fut_hand_detector.py** (MediaPipe Interface)
- Wraps MediaPipe hand detection
- Returns 21 hand landmarks per hand
- Handles multiple hand detection (up to 2)

## 🖥️ Hardware Setup

### Recommended Hardware

**Minimum:**
- Intel Core i5 (5th gen) or equivalent
- 4GB RAM
- USB 2.0 Webcam (1280x720 minimum)
- Ethernet or WiFi connection

**Recommended:**
- Intel Core i7 or better
- 8GB+ RAM
- USB 3.0 Webcam (1920x1080+)
- 5GHz WiFi or Ethernet

### Smart Lamp Module

The system communicates with smart lamps via MQTT:

```json
// Example message for Genius/Dimmer
{
  "left_hand": 1,           // Which lamp (1-10)
  "right_hand_message": 1,  // On/Off (1 or 0)
  "dimmer": 75              // Brightness (0-100)
}

// Example message for Jogo da Velha
{
  "lampada": 5              // Board position (1-9)
}
```

## 🔧 Troubleshooting

### Camera Not Found
```bash
# Check if camera is connected
ls /dev/video0  # Linux
# or check Device Manager on Windows

# Try different camera index in fut_models_main.py
# Change: SLICameraCapture(camera_index=0)
# To:     SLICameraCapture(camera_index=1)
```

### MQTT Connection Failed
```bash
# Test broker connectivity
mosquitto_sub -h 192.168.66.11 -u csilab -P WhoAmI#2024 -t "test"

# Check firewall
sudo ufw allow 1883

# Verify credentials in .env file
```

### Low FPS / Slow Performance
```bash
# Reduce video resolution in camera_capture.py
# or use a newer camera with USB 3.0
```

## 📚 Recent Improvements (v2.0)

### Separation of Concerns (MELHORIA 2)
- ✅ Extracted camera logic to `camera_capture.py`
- ✅ Extracted MQTT logic to `mqtt_client.py`
- ✅ Reduced main file from ~130 to ~80 lines
- ✅ Improved code maintainability and testability

### Error Handling (MELHORIA 3)
- ✅ Automatic camera reconnection
- ✅ Graceful MQTT failure handling
- ✅ System status tracking (prevents command spam)
- ✅ Clean shutdown procedures

### Security (BUG FIX)
- ✅ Credentials moved to `.env` file
- ✅ Removed hardcoded passwords from source
- ✅ Environment variable management with `python-dotenv`

## 🤝 Contributing

Contributions are welcome! Please follow the guidelines:

1. **Code Style**: Follow PEP 8
2. **Comments**: Write clear, Portuguese comments for complex logic
3. **Testing**: Add unit tests for new features
4. **Documentation**: Update README for significant changes
5. **Commit Messages**: Use descriptive commit messages

### Adding New Gestures

1. Modify `fut_gesture_detector.py` to define new gesture
2. Add detection logic based on landmarks
3. Update `fut_remote_controller.py` to handle new gesture
4. Update messaging in `fut_models_main.py`
5. Test with different hand positions

## 👨‍💻 Authors

| Name | Role | Organization |
|------|------|--------------|
| Álvaro Sampaio | Lead Developer | INATEL CSI-Lab |
| Murilo Cruz Lopes | Research | INATEL Competence Center |
| Ludwing Ferney Marenco | Research | INATEL Competence Center |

## 📝 License

**Copyright © 2026 INATEL**

All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner.

For licensing inquiries, contact the INATEL CSI Lab team.

---

## 📞 Support & Contact

- **Repository**: [csilabinatel/Genius](https://github.com/csilabinatel/Genius)
- **Branch**: `Up-Alvaro`
- **Issues**: Report bugs via GitHub Issues
- **Documentation**: See `/docs` folder

## 🙏 Acknowledgments

- **MediaPipe** - Hand detection models and pipeline
- **OpenCV** - Computer vision library
- **INATEL** - Research institution and support
- **CSI Lab** - Development and testing facilities

---

**Last Updated**: March 2026  
**Version**: 2.0 (Refactored with separation of concerns)
