import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math

# --- CONFIGURATION ---
pyautogui.FAILSAFE = False  # Prevents crash when mouse hits screen corners
pyautogui.PAUSE = 0         # Removes default 0.1s delay for smoother movement

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

# Screen size
screen_w, screen_h = pyautogui.size()

# Webcam setup
cap = cv2.VideoCapture(0)
wCam, hCam = 640, 480
cap.set(3, wCam)
cap.set(4, hCam)
frame_margin = 100  # Frame reduction to reach corners easily

# Timing & State variables
click_cooldown = 0.5
last_click_time = 0
dragging = False

# Motion smoothing variables
smooth_factor = 0.5    # Higher = smoother but more lag
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0

# Scroll variables
prev_scroll_y = None
scroll_sensitivity = 1.5
scroll_cooldown = 0.05
last_scroll_time = 0

# Multitasking variables
multitask_cooldown = 2.5
last_multitask_time = 0

def fingers_up(lm_list, is_right_hand=True):
    """
    Returns [Thumb, Index, Middle, Ring, Pinky] booleans.
    Adjusted for mirror view (flipped frame).
    """
    fingers = []

    # 1. Thumb Logic (X-axis depends on hand side)
    # For a mirrored right hand, thumb tip (4) should be to the LEFT of knuckle (3)
    # The original logic `lm_list[4][0] > lm_list[3][0]` assumes specific orientation.
    # We will use a simpler absolute distance check or x-check based on handedness.
    
    # Simple logic: If tip is further 'out' than the knuckle relative to the pinky side.
    # For mirrored frame:
    if lm_list[4][0] < lm_list[3][0]: # Adjusted for mirrored Right hand
        fingers.append(True)
    else:
        fingers.append(False)

    # 2. Fingers (Index to Pinky) - Check Y axis (Tip above Pip)
    # Note: Y coordinates increase downwards in OpenCV. So Tip < Pip means finger is UP.
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        if lm_list[tip][1] < lm_list[pip][1]:
            fingers.append(True)
        else:
            fingers.append(False)
            
    return fingers

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

print("Gesture Mouse Started. Press 'Esc' to exit.")

try:
    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture frame.")
            break

        # Flip for mirror view
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)
        
        current_time = time.time()

        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
                
                # Get landmarks
                lm_list = []
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = frame.shape
                    lm_list.append([int(lm.x * w), int(lm.y * h)])

                if len(lm_list) != 0:
                    index_x, index_y = lm_list[8]
                    thumb_x, thumb_y = lm_list[4]

                    # Check which fingers are up
                    fingers = fingers_up(lm_list)

                    # --- MODE 1: MULTITASKING (4 Fingers) ---
                    # Index, Middle, Ring, Pinky UP. Thumb ignored/down.
                    if fingers[1] and fingers[2] and fingers[3] and fingers[4]:
                        cv2.putText(frame, "MULTITASKING", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 0), 2)
                        
                        if current_time - last_multitask_time > multitask_cooldown:
                            pyautogui.hotkey('win', 'tab')
                            last_multitask_time = current_time
                        
                        # Freeze cursor during gesture to prevent accidental clicks
                        continue 

                    # --- MODE 2: SCROLLING (3 Fingers) ---
                    # Index, Middle, Ring UP. Pinky DOWN.
                    elif fingers[1] and fingers[2] and fingers[3] and not fingers[4]:
                        avg_y = (lm_list[8][1] + lm_list[12][1] + lm_list[16][1]) / 3
                        
                        cv2.putText(frame, "SCROLLING", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                        if prev_scroll_y is not None:
                            dy = avg_y - prev_scroll_y
                            # Check deadzone to prevent jitter scrolling
                            if abs(dy) > 5: 
                                # Direction inverted for natural scrolling
                                scroll_amount = int(dy * scroll_sensitivity)
                                pyautogui.scroll(-scroll_amount * 10) 
                        
                        prev_scroll_y = avg_y
                        continue # Skip cursor movement
                    else:
                        prev_scroll_y = None

                    # --- MODE 3: CLICKING (2 Fingers - Index + Middle) ---
                    # Index & Middle UP. Ring & Pinky DOWN.
                    if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
                        # Optional: Check distance between fingers to ensure it's intentional
                        dist_im = distance(lm_list[8], lm_list[12])
                        if dist_im < 60: # Only click if fingers are somewhat close
                            cv2.putText(frame, "LEFT CLICK", (10, 60), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            
                            if current_time - last_click_time > click_cooldown:
                                pyautogui.click()
                                last_click_time = current_time
                        
                        # Allow cursor movement while in click mode for easier aiming
                        # (Fall through to cursor control)

                    # --- MODE 4: DRAGGING (Pinch Index + Thumb) ---
                    # Index UP. Thumb close to Index.
                    drag_dist = distance([index_x, index_y], [thumb_x, thumb_y])
                    
                    if drag_dist < 40 and fingers[1]:
                        if not dragging:
                            pyautogui.mouseDown()
                            dragging = True
                            cv2.circle(frame, (index_x, index_y), 15, (0, 0, 255), cv2.FILLED)
                    else:
                        if dragging:
                            pyautogui.mouseUp()
                            dragging = False

                    # --- CURSOR CONTROL (1 Finger or Dragging) ---
                    # Only moves if Index is UP and Ring/Pinky are DOWN (to avoid conflict with scroll/multitask)
                    if fingers[1] and not fingers[3] and not fingers[4]:
                        
                        # Convert coordinates
                        # Interpolate to span the full screen even if hand is in the center frame
                        target_x = np.interp(index_x, (frame_margin, wCam - frame_margin), (0, screen_w))
                        target_y = np.interp(index_y, (frame_margin, hCam - frame_margin), (0, screen_h))

                        # Smoothen values
                        curr_x = prev_x + (target_x - prev_x) * smooth_factor
                        curr_y = prev_y + (target_y - prev_y) * smooth_factor

                        # Move mouse
                        pyautogui.moveTo(curr_x, curr_y)
                        prev_x, prev_y = curr_x, curr_y
                        
                        cv2.circle(frame, (index_x, index_y), 10, (255, 0, 0), cv2.FILLED)

        cv2.imshow("Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == 27: # ESC key
            break

except Exception as e:
    print(f"Error: {e}")
finally:
    if dragging:
        pyautogui.mouseUp() # Ensure mouse isn't stuck holding down
    cap.release()
    cv2.destroyAllWindows()