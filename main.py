"""
Squat Repetition Counter - Social Media Edition
Includes semi-transparent HUD and real-time depth progress bar.
"""
import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import os
import urllib.request
import ssl
import math

# --- AUTOMATIC MODEL DOWNLOADER ---
model_dir = "models"
model_path = os.path.join(model_dir, "pose_landmarker_full.task")

if not os.path.exists(model_path):
    os.makedirs(model_dir, exist_ok=True)
    url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
    print("Downloading Pose Landmarker Model (approx. 15MB)... Please wait.")
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        urllib.request.urlretrieve(url, model_path)
        print("✓ Model download complete!")
    except Exception as e:
        print(f"Error downloading model: {e}")
        exit(1)

# --- INITIALIZE POSE LANDMARKER (TASKS API) ---
base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False
)
landmarker = vision.PoseLandmarker.create_from_options(options)

# --- AUTOMATIC CAMERA SCANNER ---
cap = None
backends = [None, cv2.CAP_DSHOW, cv2.CAP_MSMF]

print("Scanning for available webcams...")
for index in [0, 1, 2]:
    for backend in backends:
        try:
            if backend is not None:
                temp_cap = cv2.VideoCapture(index, backend)
            else:
                temp_cap = cv2.VideoCapture(index)
            
            if temp_cap.isOpened():
                success, test_frame = temp_cap.read()
                if success:
                    cap = temp_cap
                    print(f"✓ Success! Connected to Camera Index {index}")
                    break
                else:
                    temp_cap.release()
        except Exception:
            continue
    if cap is not None:
        break

if cap is None or not cap.isOpened():
    print("Error: Could not connect to any camera.")
    exit(1)

# Counter variables
counter = 0
stage = "up"  # "up" or "down"

def calculate_angle(a, b, c):
    """Calculate the angle between hip (a), knee (b), and ankle (c)"""
    ax, ay = a.x, a.y
    bx, by = b.x, b.y
    cx, cy = c.x, c.y
    
    angle_rad = math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx)
    angle_deg = abs(angle_rad * 180.0 / math.pi)
    
    if angle_deg > 180.0:
        angle_deg = 360.0 - angle_deg
        
    return int(angle_deg)

while True:
    success, frame = cap.read()
    if not success:
        print("Error: Failed to read frame from webcam.")
        break

    h, w, c = frame.shape

    # Recolor image to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Run Pose Detection
    detection_result = landmarker.detect(mp_image)

    # Default values for progress bar
    progress_percent = 0
    angle = 180

    if detection_result.pose_landmarks:
        pose_landmarks = detection_result.pose_landmarks[0]
        
        try:
            # Extract Left Hip (23), Left Knee (25), Left Ankle (27)
            hip = pose_landmarks[23]
            knee = pose_landmarks[25]
            ankle = pose_landmarks[27]
            
            # Calculate knee angle
            angle = calculate_angle(hip, knee, ankle)
            
            # Convert normalized coordinates to screen pixel coordinates
            hip_px = (int(hip.x * w), int(hip.y * h))
            knee_px = (int(knee.x * w), int(knee.y * h))
            ankle_px = (int(ankle.x * w), int(ankle.y * h))
            
            # Map the angle dynamically to depth percentage (160 deg = 0%, 90 deg = 100%)
            val = (angle - 160) / (90 - 160)
            progress_percent = max(0, min(100, int(val * 100)))

            # --- DRAW SKELETON GRAPHICS (Neon Green/Pink) ---
            # Joint Outer Outline (Shadow effect)
            for pt in [hip_px, knee_px, ankle_px]:
                cv2.circle(frame, pt, 12, (0, 0, 0), -1)
                cv2.circle(frame, pt, 10, (50, 255, 50), -1)   # Neon Green Inner
                cv2.circle(frame, pt, 4, (255, 255, 255), -1)  # White core
            
            # Skeletal Connection Lines
            cv2.line(frame, hip_px, knee_px, (255, 50, 150), 4)  # Sleek Neon Pink line
            cv2.line(frame, knee_px, ankle_px, (255, 50, 150), 4)
            
            # Display angle text near the knee
            cv2.putText(
                frame, 
                f"{angle} deg", 
                (knee_px[0] + 15, knee_px[1] - 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, 
                (255, 255, 255), 
                2, 
                cv2.LINE_AA
            )
            
            # --- SQUAT COUNTING LOGIC ---
            if angle > 160:
                stage = "up"
                
            if angle < 100 and stage == "up":
                stage = "down"
                counter += 1
                print(f"Rep counted! Total Squats: {counter}")
                
        except Exception as e:
            pass

    # --- DRAW TRANSLUCENT GLASSMORPHIC OVERLAY CARD ---
    overlay = frame.copy()
    cv2.rectangle(overlay, (20, 20), (340, 120), (30, 30, 30), -1)  # Semi-dark slate card
    
    # Blend overlay to create transparent effect
    alpha = 0.65
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # --- RENDER MODERN HUD TEXT ---
    # Draw Reps Section
    cv2.putText(frame, 'REPS', (40, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, str(counter), (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 3, cv2.LINE_AA)
    
    # Draw Stage Section (Changes color dynamically based on state)
    stage_color = (0, 255, 0) if stage == "down" else (255, 255, 255)  # Green when DOWN, White when UP
    cv2.putText(frame, 'STAGE', (200, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, stage.upper(), (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.4, stage_color, 3, cv2.LINE_AA)

    # --- DRAW DEPTH PROGRESS BAR (Right side of screen) ---
    bar_x1, bar_y1 = w - 60, 150
    bar_x2, bar_y2 = w - 30, 400
    
    # Draw background bar (Dark gray)
    cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y2), (50, 50, 50), -1)
    
    # Calculate filled bar height
    bar_fill_y = int(bar_y2 - (progress_percent / 100.0) * (bar_y2 - bar_y1))
    
    # Determine bar color dynamically (Turns neon green when a squat is reached)
    bar_color = (0, 255, 0) if progress_percent >= 90 else (255, 127, 0)
    
    # Draw active depth fill
    cv2.rectangle(frame, (bar_x1, bar_fill_y), (bar_x2, bar_y2), bar_color, -1)
    
    # Draw active depth percentage text
    cv2.putText(frame, f"{progress_percent}%", (bar_x1 - 10, bar_y1 - 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # Display the modern window
    cv2.imshow('Squat Counter Feed', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()