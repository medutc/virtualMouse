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
    cap = cv2.VideoCapture(0)
    cap.set(3, config.CAM_WIDTH)
    cap.set(4, config.CAM_HEIGHT)

    tracker = HandTracker(max_hands=1)
    mouse = MouseController()

    p_time = 0

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame from camera. Exiting...")
            break

        img = cv2.flip(img, 1)
        img = tracker.find_hands(img, draw=True)
        landmark_list = tracker.get_positions(img)

        if len(landmark_list) != 0:
            _, x8, y8 = landmark_list[config.INDEX_FINGER_TIP]

            cv2.circle(img, (x8, y8), 10, config.COLOR_LANDMARK, cv2.FILLED)

            mouse.move_mouse(x8, y8)

            distance, _, _ = tracker.calculate_distance(config.THUMB_TIP, config.INDEX_FINGER_TIP)

            if distance is not None and distance < config.CLICK_THRESHOLD:
                cv2.circle(img, (x8, y8), 10, config.COLOR_CLICK, cv2.FILLED)
                mouse.click()
            else:
                # Pinch released — reset debounce so next pinch registers
                mouse.release()
        else:
            mouse.release()

        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time

        cv2.putText(img, f'FPS: {int(fps)}', (20, 50),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        cv2.imshow("Virtual Touchscreen", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()