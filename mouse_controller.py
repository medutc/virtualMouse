"""
Mouse control module.
Handles coordinate transformation, cursor smoothing, and OS-level inputs.
"""

import pyautogui
import numpy as np
import config

class MouseController:
    def __init__(self):
        # Disable fail-safe temporarily for edge-of-screen movements.
        # (Warning: Set to True if you want to abort by slamming mouse to a corner)
        pyautogui.FAILSAFE = False 
        
        # Get the actual resolution of your Windows monitor
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Variables to store the previous cursor position for our smoothing algorithm
        self.prev_x, self.prev_y = 0, 0

    def move_mouse(self, cam_x, cam_y):
        """
        Maps webcam coordinates to screen coordinates and moves the mouse.
        """
        # 1. Coordinate Transformation
        # np.interp linearly maps a value from one range to another.
        # It converts our 640x480 webcam space to your 1920x1080 (or similar) screen space.
        screen_x = np.interp(cam_x, (0, config.CAM_WIDTH), (0, self.screen_w))
        screen_y = np.interp(cam_y, (0, config.CAM_HEIGHT), (0, self.screen_h))
        
        # 2. Cursor Smoothing (Exponential Moving Average)
        # We don't jump straight to the new coordinate. We step towards it based on the SMOOTHING_FACTOR.
        curr_x = self.prev_x + (screen_x - self.prev_x) / config.SMOOTHING_FACTOR
        curr_y = self.prev_y + (screen_y - self.prev_y) / config.SMOOTHING_FACTOR
        
        # 3. Actuation
        pyautogui.moveTo(curr_x, curr_y)
        
        # Update state for the next frame
        self.prev_x, self.prev_y = curr_x, curr_y

    def click(self):
        """
        Executes a native Windows left-click.
        """
        pyautogui.click()