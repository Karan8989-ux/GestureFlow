#  GestureFlow: AI Virtual Mouse

**Control your computer with simple hand gestures.** *No hardware required—just your webcam and Python.*

##  About
**GestureFlow** is a computer vision project that allows users to control their mouse cursor, click, scroll, and drag files using hand gestures. It uses **MediaPipe** for robust hand tracking and **PyAutoGUI** to interface with the operating system. This tool is perfect for touchless interfaces, presentations, or accessibility purposes.

##  Features
* **Cursor Control:** Smooth movement using the index finger.
* **Left Click:** Pinch your index and middle fingers together.
* **Drag & Drop:** Pinch your index finger and thumb to grab and move items.
* **Scrolling:** Use three fingers to scroll pages up and down.
* **Multitasking:** Show all open windows (Task View) by raising four fingers.
* **Smoothed Motion:** built-in algorithm to reduce jitter and shakiness.

##  Tech Stack
* **Python 3.x**
* **OpenCV** (Video capture & image processing)
* **MediaPipe** (Hand landmark detection)
* **PyAutoGUI** (Mouse automation)
* **NumPy** (Math & coordinate interpolation)

##  Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/GestureFlow.git](https://github.com/YOUR_USERNAME/GestureFlow.git)
    cd GestureFlow
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *(If you don't have a requirements file, run: `pip install opencv-python mediapipe pyautogui numpy`)*

## 🚀 How to Run
1.  Connect your webcam.
2.  Run the script:
    ```bash
    python main.py
    ```
3.  Stand about 1 meter away from the camera for best detection.
4.  Press **`Esc`** to exit the program.

## 🖐️ Gesture Guide

| Action | Hand Gesture | Visual Indicator |
| :--- | :--- | :--- |
| **Move Cursor** | **Index Finger UP** (other fingers down) | 🔵 Blue Dot |
| **Left Click** | **Index + Middle Fingers UP** | "LEFT CLICK" Text |
| **Scroll** | **3 Fingers UP** (Index, Middle, Ring) | "SCROLLING" Text |
| **Drag & Drop** | **Index + Thumb PINCH** | 🔴 Red Dot |
| **Task View** | **4 Fingers UP** (Index to Pinky) | "MULTITASKING" Text |

##  Troubleshooting
* **Laggy Mouse?** The script uses a smoothing factor to reduce jitter. You can adjust the `smooth_factor` variable in the code (higher = smoother but slower).
* **Gestures Not Working?** Ensure you have good lighting and your hand is clearly visible. Backgrounds with skin-tone colors might confuse the detector.
* **Safety Feature:** If the mouse gets stuck, move your real mouse to any corner of the screen (Fail-Safe) or press `Esc`.

##  Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request if you have ideas for new gestures (like Right Click or Volume Control).

##  License
This project is open-source and available for educational purposes.
