FormFit 
 *Real-Time AI Squat Counter & Depth Analyzer*
This is v1. See FormFit-AI-Squat-Tracker for the full version with radial analytics.
**FormFit** is a computer vision-powered fitness application that tracks body pose landmarks in real-time to analyze squat depth and count repetitions. 

Built using Python, OpenCV, and the modern MediaPipe Tasks API, the application calculates joint angles dynamically to provide instant visual feedback on exercise form.

---
Features
* **Real-Time Body Pose Tracking:** Tracks the key joints (left hip, left knee, left ankle) dynamically.
* **Depth Progress Bar:** Features a vertical progress bar that calculates how deep you are bending into your squat (from 0% to 100%).
* **Visual Form Feedback:** The progress bar changes color dynamically (orange to neon green) once a valid squat depth (below 100°) is achieved.
* **Modern Semi-Transparent HUD:** Built with a glassmorphic overlay displaying real-time reps and current stage (UP/DOWN).
* **Python 3.14 Compatible:** Architected to run smoothly on newer Python environments by using direct MediaPipe tasks and manual OpenCV coordinates mapping.

---

Technologies Used
* **Python** 
* **OpenCV** (Video capture, image flipping, drawing UI overlays, and skeletal frames)
* **MediaPipe** (Modern Pose Landmarker Tasks API)

---

Installation & Setup

Step 1 — Clone the Project
Run this command in your terminal: 
git clone https://github.com/April033/Squat-Rep-Counter-AI-Powered-Fitness-Tracker

Step 2 — Install Dependencies
Ensure you have Python installed, then run:
pip install opencv-python mediapipe

Step 3 — Download the Pose Model Manually
1. Download pose_landmarker_full.task from: https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
2. Create a folder named "models" inside your project directory.
3. Place the downloaded "pose_landmarker_full.task" file inside that "models" folder.

Your directory structure should look like this:
formfit/
├── main.py
├── README.md
└── models/
    └── pose_landmarker_full.task

---

How to Use
1. Run the application:
   python main.py
2. Step back so the webcam can capture your full side profile (specifically your left hip, knee, and ankle).
3. Perform a squat. As you lower your hips, you will see the depth meter on the right fill up. Once the depth meter crosses 90% and turns neon green, stand back up to complete the rep!
4. Click on the camera window and press "q" to close the camera and exit the application.

---

How It Works
1. **Webcam Capture:** OpenCV captures frames from your camera and mirrors them for natural interaction.
2. **AI Joint Landmark Detection:** The MediaPipe Pose Landmarker processes the image and extracts the normalized coordinates of the left hip (index 23), left knee (index 25), and left ankle (index 27).
3. **Knee Angle Calculation:** The script uses trigonometry to find the acute angle of the knee.
4. **State-Machine Logic:** 
   * **Stage UP:** Knee angle is straight (>160 degrees).
   * **Stage DOWN:** Knee angle is bent below the squat threshold (<100 degrees).
   * A rep is counted only when transitioning from DOWN back to UP.

---

Learning Outcomes
This project demonstrates hands-on experience in:
* **Computer Vision & Human-Computer Interaction (HCI):** Processing video frames and drawing custom graphics dynamically.
* **Applied Mathematics:** Using geometric vector math to calculate joint angles in a 2D plane.
* **State Machines:** Designing state logic (UP/DOWN stages) to handle human movement safely and prevent count errors.
* **Environment Troubleshooting:** Resolving namespace resolution challenges on newer experimental Python environments (Python 3.14).

---

Future Improvements
* Multi-exercise tracking (push-ups, lunges, and bicep curls).
* Voice feedback to announce reps and form corrections.
* AI-powered velocity tracking to analyze power output during exercise.
