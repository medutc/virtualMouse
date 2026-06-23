"""
Mouse Controller module.
Handles translating hand landmark positions into smooth mouse movements and clicks.
"""

import pyautogui
import numpy as np
import config

# Disable PyAutoGUI's built-in fail-safe pause (we handle timing ourselves)
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False


class MouseController:

    def __init__(self):
        # Get the screen resolution once at startup
        self.screen_w, self.screen_h = pyautogui.size()

        # Smoothing factor (0.0 = frozen, 1.0 = raw/jittery)
        # 0.2 means "move 20% toward new position each frame" → very smooth
        # Tune this between 0.1 (ultra smooth) and 0.4 (more responsive)
        self.smoothing = 0.18

        # Store the last smoothed cursor position
        # Start at the center of the screen
        self.smooth_x = self.screen_w / 2
        self.smooth_y = self.screen_h / 2

        # Click debounce: track whether we were already clicking last frame
        self.clicking = False

    def move_mouse(self, finger_x, finger_y):
        """
        Maps the finger position (in camera space) to screen space,
        then applies exponential smoothing before actually moving the cursor.
        """
        # --- 1. Map camera coords → screen coords ---
        # We use a reduced "active zone" in the center of the camera frame
        # so you don't have to reach the very edges of the frame to hit screen edges.
        # Clamp first, then interpolate.
        margin = getattr(config, 'FRAME_MARGIN', 80)

        cam_x = np.clip(finger_x, margin, config.CAM_WIDTH - margin)
        cam_y = np.clip(finger_y, margin, config.CAM_HEIGHT - margin)

        # Linear interpolation from camera active zone → full screen
        target_x = np.interp(cam_x, [margin, config.CAM_WIDTH - margin], [0, self.screen_w])
        target_y = np.interp(cam_y, [margin, config.CAM_HEIGHT - margin], [0, self.screen_h])

        # --- 2. Exponential smoothing (low-pass filter) ---
        # new_pos = old_pos + smoothing * (target - old_pos)
        # This prevents jittery raw landmark data from shaking the cursor.
        self.smooth_x += self.smoothing * (target_x - self.smooth_x)
        self.smooth_y += self.smoothing * (target_y - self.smooth_y)

        # --- 3. Move cursor ---
        pyautogui.moveTo(int(self.smooth_x), int(self.smooth_y))

    def click(self):
        """
        Performs a single click with debounce to avoid repeated clicks
        while the pinch gesture is held.
        """
        if not self.clicking:
            pyautogui.click()
            self.clicking = True

    def release(self):
        """
        Call this when the click gesture ends so the next pinch registers again.
        """
        self.clicking = False