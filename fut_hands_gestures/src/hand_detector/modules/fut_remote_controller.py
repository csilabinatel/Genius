# Creation Date: 2024-06-07
# Authors Murilo Cruz Lopes, Ludwing Ferney Marenco Camacho
# Developed by: Inatel Competence Center
# Copyright 2024, INATEL.
# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner

from modules.fut_hand_detector import SLIHandDetector
from utils.fut_hand_landmarks_utils import SLIHandLandMarks
import modules.fut_gesture_detector as gd
import json


class SLIRemoteController():

    def __init__(self, dimmer_flag = False):
        self._hand_detector = SLIHandDetector(min_detection_confidence=0.9)
        self.dimmer_flag = dimmer_flag

    def __get_command_gesture(self, land_marks, hand_pos):
        command_dic = {}
        command_dic["hand"] = "Right"
        command_dic["number"] = None
        command_dic["open_palm"] = False
        command_dic["close_fist"] = False
        command_dic["env_var"] = False
        command_dic["graphs"] = False
        command_dic["remove_all"] = False
        command_dic["dimmer_value"]= None
        command_dic["thumbs_up"] = False

        if gd.is_thumbs_up(land_marks):
            command_dic["thumbs_up"] = True
            return command_dic

        number = self.__get_gesture_number(land_marks, hand_pos)
        if isinstance(number, int):
            command_dic["number"] = number

        if number == 1:
            command_dic["env_var"] = True
            return command_dic

        if number == 2:
            command_dic["graphs"] = True
            return command_dic

        if number == 3:
            command_dic["remove_all"] = True
            return command_dic

        if gd.is_palm_open(land_marks):
            command_dic["open_palm"] = True
            return command_dic

        if gd.is_fist_close(land_marks, hand_pos):
            command_dic["close_fist"] = True
            return command_dic

        angulo, relative_value = gd.controll_dimmer(land_marks)
        if angulo <= 43 and angulo >= 0:
            if self.dimmer_flag:
                command_dic["dimmer_value"] = relative_value
            return command_dic

        return command_dic


    def __get_gesture_number(self, hand_landmark, hand_position = None):

        number_one = gd.is_number_one(hand_landmark)
        if number_one and hand_position == "Left":
            return {"hand": "Left", "number": 1}
        elif number_one and hand_position == "Right":
            return 1

        number_two = gd.is_number_two(hand_landmark)
        if number_two and hand_position == "Left":
            return {"hand": "Left", "number": 2}
        elif number_two and hand_position == "Right":
            return 2

        number_three = gd.is_number_three(hand_landmark)
        if number_three and hand_position == "Left":
            return {"hand": "Left", "number": 3}
        elif number_three and hand_position == "Right":
            return 3


        if gd.is_number_four(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 4}

        if gd.is_number_four(hand_landmark) and hand_position == "Right":
            return 4

        if gd.is_palm_open(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 5}

        if gd.is_palm_open(hand_landmark) and hand_position == "Right":
            return 5

        if gd.is_number_six(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 6}

        if gd.is_number_six(hand_landmark) and hand_position == "Right":
            return 6

        if gd.is_number_seven(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 7}

        if gd.is_number_eight(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 9}

        if gd.is_number_nine(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 8}

        if gd.is_fist_close(hand_landmark, 'Left'):
            return {"hand": "Left", "number": 10}
        
        if hand_position == "Right":
            return None

        return {"hand": "Left", "number": None}


    def process_frame(self, frame, roi_side = None):
        
        hand_landmarks = self._hand_detector.find_hand_landmarks(image = frame, draw=True)

        hand_position = list(hand_landmarks.keys())

        if len(hand_position) != 0:
            land_marks = SLIHandLandMarks(hand_landmarks[hand_position[0]])

            if hand_position[0] == "Left" and roi_side == "Left":
                if gd.is_thumbs_up(land_marks):
                    return frame, {"hand": "Left", "number": None, "click_status": False, "thumbs_up": True}

                left_hand_dic = self.__get_gesture_number(land_marks, "Left")
                left_hand_dic["thumbs_up"] = False
                _, dimmer_value = gd.controll_dimmer(land_marks)
                if dimmer_value == 0:
                    left_hand_dic["click_status"] = True
                    left_hand_dic["number"] = None
                elif dimmer_value < 99 and (left_hand_dic["number"] == 7):
                    left_hand_dic["number"] = None
                    left_hand_dic["click_status"] = False
                else:
                    left_hand_dic['click_status'] = False
                return frame, left_hand_dic

            if hand_position[0] == "Right" and roi_side == "Right":
                return frame, self.__get_command_gesture(land_marks, hand_position[0])

        return frame, {}
