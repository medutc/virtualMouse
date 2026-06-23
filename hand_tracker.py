"""
Hand tracking module using MediaPipe.
Responsible for detecting hands, drawing landmarks, and extracting spatial coordinates.
"""

import cv2
import mediapipe as mp
import math

class HandTracker:
    def __init__(self, mode=False, max_hands=1, detection_con=0.7, track_con=0.5):
        """
        Initializes the MediaPipe Hands object.
        :param mode: False for video stream, True for static images.
        :param max_hands: We only want to track 1 hand for the mouse.
        :param detection_con: Minimum confidence threshold for initial detection.
        :param track_con: Minimum confidence threshold for continuous tracking.
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        # Initialize MediaPipe Hands solution
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        # Utility to draw landmarks on the OpenCV image
        self.mp_draw = mp.solutions.drawing_utils

        # Store landmarks to access across methods
        self.landmark_list = []

    def find_hands(self, img, draw=True):
        """
        Processes the image and optionally draws hand landmarks.
        """
        # MediaPipe requires RGB images, OpenCV captures in BGR
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    # Draw the nodes and connections on the image
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        return img

    def get_positions(self, img):
        """
        Extracts pixel coordinates for all 21 hand landmarks.
        :return: List of tuples -> [(id, x, y), ...]
        """
        self.landmark_list = []
        
        if self.results.multi_hand_landmarks:
            # Since max_hands=1, we grab the first detected hand
            my_hand = self.results.multi_hand_landmarks[0]
            
            # Get the dimensions of the image to convert normalized ratios to actual pixels
            h, w, c = img.shape
            
            for id, lm in enumerate(my_hand.landmark):
                # lm.x and lm.y are normalized between 0.0 and 1.0. 
                # Multiply by width and height to get pixel coordinates.
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.landmark_list.append((id, cx, cy))
                
        return self.landmark_list

    def calculate_distance(self, p1_id, p2_id):
        """
        Calculates the Euclidean distance between two specific landmarks.
        Used primarily to detect the pinch gesture (thumb and index).
        """
        if len(self.landmark_list) == 0:
            return 0, [0, 0], [0, 0]

        # Extract x, y coordinates using the landmark IDs
        x1, y1 = self.landmark_list[p1_id][1], self.landmark_list[p1_id][2]
        x2, y2 = self.landmark_list[p2_id][1], self.landmark_list[p2_id][2]

        # Euclidean distance formula
        distance = math.hypot(x2 - x1, y2 - y1)
        
        return distance, (x1, y1), (x2, y2)