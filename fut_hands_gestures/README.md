# Inatel Hand Gestures Recognition Repository
 
## Overview
 
Welcome to the Inatel Hand Gestures Recognition repository! This Python implementation utilizes OpenCV and MediaPipe frameworks for robust hand gestures detection.
 
## Features
 
- **Dual Hand Recognition**: Detects gestures for both left and right hands simultaneously;
- **Real-time Responsiveness**: Delivers instant feedback for seamless interaction;
- **Diverse Gestures**: Recognizes ten gestures for the left hand and six for the right hand. Gestures are described as follows:
    - **Left Hand**: Numbers 1 through 10;
    - **Right Hand**: Control on-off states, display variables either as numbers or within a graph and operates the dimerizer.
- **Customizable**: Easily adaptable for various applications and gesture sets.
 
## How to Use?
 
Follow these steps to run the hand gesture detector:
 
1. **Set Up Virtual Environment**: Create a virtual environment to manage dependencies cleanly by running
 
    ```bash
    ./scripts/fut_create_venv.sh <enviroment_name>
    ```
   
2. **Activate virtual envinroment**: Activate your virtual environment. You can do this by running:
 
    ```bash
    ./scripts/fut_activate_venv.sh <enviroment_name>
    ```
    
 
. **Run the Detector**: Execute the following command within your virtual environment to start the hand gesture detector:
 
    ```bash
    ./main.sh
    ```