"""
Main application loop for the Virtual Touchscreen.
Ties together the webcam, MediaPipe tracking, and PyAutoGUI control.
"""

import cv2
import time
import config
from hand_tracker import HandTracker
from mouse_controller import MouseController

def main():
    # 1. Initialize Camera (0 is usually the default built-in webcam)
    cap = cv2.VideoCapture(0)
    cap.set(3, config.CAM_WIDTH)
    cap.set(4, config.CAM_HEIGHT)
    
    # 2. Initialize our OOP modules
    tracker = HandTracker(max_hands=1)
    mouse = MouseController()
    
    p_time = 0  # Previous time (used for calculating FPS)

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame from camera. Exiting...")
            break
            
        # 3. Mirror the image horizontally
        # If we don't flip it, moving your hand right moves the cursor left.
        img = cv2.flip(img, 1)
        
        # 4. Find hands and get landmarks
        img = tracker.find_hands(img, draw=True)
        landmark_list = tracker.get_positions(img)
        
        # If a hand is detected in the frame
        if len(landmark_list) != 0:
            
            # Extract the coordinates of the Index Finger Tip (Landmark 8)
            _, x8, y8 = landmark_list[config.INDEX_FINGER_TIP]
            
            # Draw a prominent circle on the index finger for visual feedback
            cv2.circle(img, (x8, y8), 10, config.COLOR_LANDMARK, cv2.FILLED)
            
            # Move the cursor
            mouse.move_mouse(x8, y8)
            
            # 5. Check for Click Gesture (Distance between Thumb and Index)
            distance, _, _ = tracker.calculate_distance(config.THUMB_TIP, config.INDEX_FINGER_TIP)
            
            # If fingers are pinched together, execute a click
            if distance < config.CLICK_THRESHOLD:
                # Change the circle color to green to indicate a click registered
                cv2.circle(img, (x8, y8), 10, config.COLOR_CLICK, cv2.FILLED)
                mouse.click()
                
                # A brief sleep prevents one pinch from registering as 10 rapid clicks
                time.sleep(0.15)

        # 6. Performance Tracking (FPS)
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        
        cv2.putText(img, f'FPS: {int(fps)}', (20, 50), 
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        
        # 7. Render the UI
        cv2.imshow("Virtual Touchscreen", img)
        
        # Press 'q' on your keyboard to kill the application safely
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    # Cleanup resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()