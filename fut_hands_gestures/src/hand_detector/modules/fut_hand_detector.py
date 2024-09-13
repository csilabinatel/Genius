# Creation Date: 2024-06-07
# Authors Murilo Cruz Lopes, Ludwing Ferney Marenco Camacho
# Developed by: Inatel Competence Center
# Copyright 2024, INATEL.
# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils


class SLIHandDetector:

    def __init__(self, max_num_hands = 2, min_detection_confidence=0.5, min_tracking_confidence = 0.5):
        self.hands = mpHands.Hands(model_complexity = 1, max_num_hands=max_num_hands, min_detection_confidence=min_detection_confidence,
                                   min_tracking_confidence=min_tracking_confidence)


    def find_hand_landmarks(self, image, draw=False):
        dic = {}
        originalImage = image
        image  = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)

        if results.multi_hand_landmarks:

            if len(results.multi_handedness) == 2:
                hand_pos1, hand_pos2 = self.__get_hand_position(results)
                dic[hand_pos1] = self.__get_land_marks(results.multi_hand_landmarks[0], originalImage.shape)
                dic[hand_pos2] = self.__get_land_marks(results.multi_hand_landmarks[1], originalImage.shape)
                mpDraw.draw_landmarks(originalImage, results.multi_hand_landmarks[0], mpHands.HAND_CONNECTIONS, mpDraw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4), mpDraw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2))
                mpDraw.draw_landmarks(originalImage, results.multi_hand_landmarks[1], mpHands.HAND_CONNECTIONS, mpDraw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4), mpDraw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))

            else:
                hand_pos1 = self.__get_hand_position(results)
                dic[hand_pos1] = self.__get_land_marks(results.multi_hand_landmarks[0], originalImage.shape)
                mpDraw.draw_landmarks(originalImage, results.multi_hand_landmarks[0], mpHands.HAND_CONNECTIONS, mpDraw.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=4), mpDraw.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2))

        return dic

    def __get_land_marks(self, hand, originalImageShape):
        landMarkList = []
        imgH, imgW, _ = originalImageShape
        for id, landMark in enumerate(hand.landmark):
            xPos, yPos = int(landMark.x*imgW), int(landMark.y * imgH)
            landMarkList.append([id, xPos, yPos])
        return landMarkList

    def __get_hand_position(self, results):
        if len(results.multi_handedness) == 2:
            return results.multi_handedness[0].classification[0].label, results.multi_handedness[1].classification[0].label
        return results.multi_handedness[0].classification[0].label