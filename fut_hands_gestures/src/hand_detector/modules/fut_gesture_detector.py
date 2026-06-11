# Creation Date: 2024-06-07
# Authors Murilo Cruz Lopes, Ludwing Ferney Marenco Camacho
# Developed by: Inatel Competence Center
# Copyright 2024, INATEL.
# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner

import cv2
import math
import numpy as np
from utils.fut_enum_hand_utils import SLIHandEnum


def controll_dimmer(handLandmarks):
    length = math.hypot(handLandmarks.index_x1 - handLandmarks.thumb_x1,handLandmarks.index_y1 - handLandmarks.thumb_y1)
    base = math.hypot(handLandmarks.thumb_x1 - handLandmarks.thumb_mcp_x1, handLandmarks.thumb_y1 - handLandmarks.thumb_mcp_y1)
    length_angulo = math.atan2(length, base) * 180 / np.pi
    return length_angulo, int(np.interp(length_angulo, [13, 40], [0, 100])) # 13 smaller angle, 51 higher angle


def calculate_angle_between_lines(point_1, point_2):
    dx = abs(point_1[0] - point_2[0])
    dy = abs(point_1[1] - point_2[1])
    return math.atan2(dy, dx) * 180 / np.pi


def is_number_one(hand_landmarks):
    angle = calculate_angle_between_lines((hand_landmarks.thumb_x1, hand_landmarks.thumb_y1), (hand_landmarks.wirst_x1, hand_landmarks.wirst_y1))
    if (angle > 45) and (hand_landmarks.middle_y1 > hand_landmarks.middle_mcp_y1):
        if (hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1):
            if (hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1):
                if (hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1):
                    return True
    return False


def is_number_two(hand_landmarks):
    if (hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1):
        if (hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1):
            if (hand_landmarks.middle_y1 < hand_landmarks.middle_mcp_y1):
                if (hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1):
                    if (hand_landmarks.thumb_x1 < hand_landmarks.index_x1) or (hand_landmarks.thumb_x1 > hand_landmarks.index_x1):
                        return True
    return False


def is_number_three(hand_landmarks):
    if ((hand_landmarks.pink_y1 > hand_landmarks.ring_pip_y1) and ((hand_landmarks.thumb_x1 < hand_landmarks.index_x1) or (hand_landmarks.thumb_x1 > hand_landmarks.index_x1))):
        if (hand_landmarks.middle_y1 < hand_landmarks.middle_mcp_y1):
            if (hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1):
                if (hand_landmarks.ring_y1 < hand_landmarks.ring_mcp_y1):
                    return True
    return False


def is_number_four(hand_landmarks):
    if (hand_landmarks.ring_y1 < hand_landmarks.middle_dip_y1):
        thumb_inside_palm = (
            min(hand_landmarks.pink_mcp_x1, hand_landmarks.index_mcp_x1)
            < hand_landmarks.thumb_x1
            < max(hand_landmarks.pink_mcp_x1, hand_landmarks.index_mcp_x1)
        )
        if thumb_inside_palm:
            if ((hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1) and (hand_landmarks.middle_y1 < hand_landmarks.middle_mcp_y1)):
                if ((hand_landmarks.ring_y1 < hand_landmarks.ring_mcp_y1) and (hand_landmarks.pink_y1 < hand_landmarks.pink_mcp_y1)):
                    return True
    return False


def is_number_seven(hand_landmarks):
    angle = calculate_angle_between_lines((hand_landmarks.thumb_x1, hand_landmarks.thumb_y1), (hand_landmarks.wirst_x1, hand_landmarks.wirst_y1))
    if (angle < 40) and (hand_landmarks.middle_y1 > hand_landmarks.middle_mcp_y1):
        if (hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1):
            if (hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1):
                if (hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1):
                    return True
    return False


def is_number_six(hand_landmarks):
    angle = calculate_angle_between_lines((hand_landmarks.thumb_x1, hand_landmarks.thumb_y1), (hand_landmarks.wirst_x1, hand_landmarks.wirst_y1))
    if (angle < 45) and (hand_landmarks.index_y1 > hand_landmarks.index_mcp_y1):
        if (hand_landmarks.middle_y1 > hand_landmarks.middle_mcp_y1) and (hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1):
            if ((hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1)):
                return True
    return False


def is_number_nine(hand_landmarks):
    if (hand_landmarks.index_y1 < hand_landmarks.middle_x1) and (hand_landmarks.pink_y1 < hand_landmarks.middle_x1):
        if (hand_landmarks.index_y1 < hand_landmarks.ring_y1) and (hand_landmarks.pink_y1 < hand_landmarks.ring_y1):
            if (hand_landmarks.index_y1 < hand_landmarks.pink_y1):
                return True
    return False


def is_number_eight(hand_landmarks):
    angle = calculate_angle_between_lines((hand_landmarks.thumb_x1, hand_landmarks.thumb_y1), (hand_landmarks.wirst_x1, hand_landmarks.wirst_y1))
    if (angle > 40) and (hand_landmarks.pink_y1 < hand_landmarks.ring_y1):
        if (hand_landmarks.pink_y1 < hand_landmarks.middle_y1):
            if (hand_landmarks.pink_y1 < hand_landmarks.index_y1):
                return True
    return False


def is_palm_open(hand_landmarks):
    if (hand_landmarks.ring_y1 < hand_landmarks.middle_dip_y1):
        if (hand_landmarks.middle_y1 < hand_landmarks.thumb_y1):
            if (hand_landmarks.middle_y1 < hand_landmarks.index_y1):
                if (hand_landmarks.middle_y1 < hand_landmarks.ring_y1):
                    if (hand_landmarks.middle_y1 < hand_landmarks.pink_y1):
                        if (hand_landmarks.ring_y1 < hand_landmarks.ring_mcp_y1):
                            return True
    return False


def is_fist_close(hand_landmarks, handpos):
    if (hand_landmarks.index_y1 > hand_landmarks.index_mcp_y1):
        if (hand_landmarks.middle_y1 > hand_landmarks.middle_mcp_y1):
            if (hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1):
                if (hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1):
                    if ((hand_landmarks.index_finger_pip_y1 < hand_landmarks.thumb_y1 < hand_landmarks.index_finder_dip_y1) or (abs(hand_landmarks.thumb_y1 - hand_landmarks.index_finger_pip_y1) < 10)):
                        if (handpos == 'Right' and (hand_landmarks.thumb_x1 < hand_landmarks.middle_x1)) or (handpos == 'Left' and (hand_landmarks.thumb_x1 > hand_landmarks.middle_x1)):
                            return True # closed fist
                        elif handpos == 'Right' and is_front_or_back(hand_landmarks, handpos) == SLIHandEnum.RIGHT_BACK and ((hand_landmarks.index_mcp_x1 > hand_landmarks.thumb_x1 > hand_landmarks.middle_mcp_x1) or (hand_landmarks.index_mcp_y1 < hand_landmarks.thumb_y1 < hand_landmarks.index_y1)):
                            return True
                        elif handpos == 'Left' and is_front_or_back(hand_landmarks, handpos) == SLIHandEnum.LEFT_BACK and ((hand_landmarks.index_mcp_x1 > hand_landmarks.thumb_x1 > hand_landmarks.middle_mcp_x1) or (hand_landmarks.index_mcp_y1 < hand_landmarks.thumb_y1 < hand_landmarks.index_y1)):
                            return True
    return False


def is_front_or_back(hand_landmarks, handpos):
    if handpos == 'Right':
        if hand_landmarks.index_mcp_x1 < hand_landmarks.pink_mcp_x1:
            return SLIHandEnum.RIGHT_FRONT.value
        return SLIHandEnum.RIGHT_BACK.value

    # if handpos is not Right so it is left
    if hand_landmarks.pink_mcp_x1 < hand_landmarks.index_mcp_x1:
        return SLIHandEnum.LEFT_FRONT.value
    return SLIHandEnum.LEFT_BACK.value


def is_wave_moviment(middle_x1_vector, sensibility):

    window = ''
    average = sum(middle_x1_vector)/len(middle_x1_vector)

    for middle_x1 in middle_x1_vector:
        window += '1' if middle_x1 > average else '0'
    
    if window.count('0011') >= sensibility:
        return True
    else:
        return False
