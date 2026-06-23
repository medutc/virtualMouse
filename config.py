"""
Configuration parameters for the Virtual Touchscreen.
Centralizing these values makes tuning the application much easier.
"""

# Webcam settings
CAM_WIDTH = 640
CAM_HEIGHT = 480
FPS_CAP = 60

# Mouse control settings
SMOOTHING_FACTOR = 5  # Higher number = smoother but slower cursor response
CLICK_THRESHOLD = 30  # Pixel distance between thumb and index to register a click

# MediaPipe IDs
INDEX_FINGER_TIP = 8
THUMB_TIP = 4

# Colors (BGR format for OpenCV)
COLOR_LANDMARK = (255, 0, 255)
COLOR_CLICK = (0, 255, 0)