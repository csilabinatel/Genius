# Creation Date: 2026-03-15
# Authors Alvaro Sampaio
# Developed by: CSI-Lab
# Copyright 2026, INATEL.
# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner

import math
import numpy as np
from utils.fut_enum_hand_utils import SLIHandEnum
 
 
def controll_dimmer(handLandmarks):
    """
    Calcula o valor do dimmer com base na distância entre polegar e indicador.
    
    A lógica usa o ângulo formado entre:
    - A linha do polegar até o indicador (comprimento)
    - A linha do polegar até seu MCP (base)
    
    Returns:
        tuple: (angulo em graus, valor interpolado de 0 a 100)
    """
    # Distância entre a ponta do polegar e a ponta do indicador
    length = math.hypot(
        handLandmarks.index_x1 - handLandmarks.thumb_x1,
        handLandmarks.index_y1 - handLandmarks.thumb_y1
    )
    # Tamanho de referência: do polegar até sua base (MCP)
    base = math.hypot(
        handLandmarks.thumb_x1 - handLandmarks.thumb_mcp_x1,
        handLandmarks.thumb_y1 - handLandmarks.thumb_mcp_y1
    )
    # Ângulo entre as duas linhas — normaliza a escala independente da distância da câmera
    length_angulo = math.atan2(length, base) * 180 / np.pi
 
    # Interpola: ângulo 13° = 0%, ângulo 40° = 100%
    return length_angulo, int(np.interp(length_angulo, [13, 40], [0, 100]))
 
 
def calculate_angle_between_lines(point_1, point_2):
    """
    Calcula o ângulo (em graus) da linha formada por dois pontos em relação ao eixo X.
    
    Args:
        point_1: tupla (x, y)
        point_2: tupla (x, y)
    
    Returns:
        float: ângulo em graus (0° a 90°)
    """
    dx = abs(point_1[0] - point_2[0])
    dy = abs(point_1[1] - point_2[1])
    return math.atan2(dy, dx) * 180 / np.pi
 
 
def is_number_one(hand_landmarks):
    """
    Detecta o gesto do número 1: apenas o indicador levantado.
    
    Condições:
    - Ângulo do polegar > 45° (polegar não está apontando para o lado)
    - Dedo médio, anelar e mínimo dobrados (ponta abaixo do MCP)
    - Indicador levantado (ponta acima do MCP)
    """
    angle = calculate_angle_between_lines(
        (hand_landmarks.thumb_x1, hand_landmarks.thumb_y1),
        (hand_landmarks.wrist_x1, hand_landmarks.wrist_y1)
    )
    if angle > 45 and hand_landmarks.middle_y1 > hand_landmarks.middle_mcp_y1:
        if hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1:
            if hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1:
                if hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1:
                    return True
    return False
 
 
def is_number_two(hand_landmarks):
    """
    Detecta o gesto do número 2: indicador e médio levantados.
    
    Condições:
    - Anelar e mínimo dobrados
    - Indicador e médio levantados
    - Polegar em qualquer posição horizontal
    """
    if hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1:
        if hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1:
            if hand_landmarks.middle_y1 < hand_landmarks.middle_mcp_y1:
                if hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1:
                    # Polegar pode estar em qualquer posição horizontal
                    if (hand_landmarks.thumb_x1 < hand_landmarks.index_x1) or \
                       (hand_landmarks.thumb_x1 > hand_landmarks.index_x1):
                        return True
    return False
 
 
def is_number_three(hand_landmarks):
    """
    Detecta o gesto do número 3: indicador, médio e anelar levantados.
    
    Condições:
    - Mínimo dobrado (abaixo do PIP do anelar)
    - Indicador, médio e anelar levantados
    """
    if (hand_landmarks.pink_y1 > hand_landmarks.ring_pip_y1) and \
       ((hand_landmarks.thumb_x1 < hand_landmarks.index_x1) or
        (hand_landmarks.thumb_x1 > hand_landmarks.index_x1)):
        if hand_landmarks.middle_y1 < hand_landmarks.middle_mcp_y1:
            if hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1:
                if hand_landmarks.ring_y1 < hand_landmarks.ring_mcp_y1:
                    return True
    return False
 
 
def is_number_four(hand_landmarks):
    """
    Detecta o gesto do número 4: todos os dedos levantados exceto o polegar.
    
    Condições:
    - Anelar levantado acima do DIP do médio
    - Polegar posicionado entre o MCP do mínimo e o MCP do indicador (dobrado)
    - Indicador, médio, anelar e mínimo levantados
    """
    if hand_landmarks.ring_y1 < hand_landmarks.middle_dip_y1:
        if hand_landmarks.thumb_x1 > hand_landmarks.pink_mcp_x1:
            if hand_landmarks.thumb_x1 < hand_landmarks.index_mcp_x1:
                if (hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1) and \
                   (hand_landmarks.middle_y1 < hand_landmarks.middle_mcp_y1):
                    if (hand_landmarks.ring_y1 < hand_landmarks.ring_mcp_y1) and \
                       (hand_landmarks.pink_y1 < hand_landmarks.pink_mcp_y1):
                        return True
    return False
 
 
def is_number_seven(hand_landmarks):
    """
    Detecta o gesto do número 7: apenas o indicador levantado com polegar horizontal.
    
    Diferença do número 1: o ângulo do polegar é menor que 40°
    (polegar mais horizontal, apontando para o lado)
    """
    angle = calculate_angle_between_lines(
        (hand_landmarks.thumb_x1, hand_landmarks.thumb_y1),
        (hand_landmarks.wrist_x1, hand_landmarks.wrist_y1)
    )
    if angle < 40 and hand_landmarks.middle_y1 > hand_landmarks.middle_mcp_y1:
        if hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1:
            if hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1:
                if hand_landmarks.index_y1 < hand_landmarks.index_mcp_y1:
                    return True
    return False
 
 
def is_number_six(hand_landmarks):
    """
    Detecta o gesto do número 6: todos os dedos dobrados com polegar horizontal.
    
    Condições:
    - Ângulo do polegar < 45° (polegar para o lado)
    - Todos os dedos dobrados (indicador, médio, anelar, mínimo)
    """
    angle = calculate_angle_between_lines(
        (hand_landmarks.thumb_x1, hand_landmarks.thumb_y1),
        (hand_landmarks.wrist_x1, hand_landmarks.wrist_y1)
    )
    if angle < 45 and hand_landmarks.index_y1 > hand_landmarks.index_mcp_y1:
        if hand_landmarks.middle_y1 > hand_landmarks.middle_mcp_y1 and \
           hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1:
            if hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1:
                return True
    return False
 
 
def is_number_nine(hand_landmarks):
    """
    Detecta o gesto do número 9.
    
    Condições baseadas na posição relativa do indicador e mínimo
    em relação ao médio e anelar.
    
    NOTA: Verifique calibração — coordenadas Y crescem para baixo na imagem.
    """
    if (hand_landmarks.index_y1 < hand_landmarks.middle_x1) and \
       (hand_landmarks.pink_y1 < hand_landmarks.middle_x1):
        if (hand_landmarks.index_y1 < hand_landmarks.ring_y1) and \
           (hand_landmarks.pink_y1 < hand_landmarks.ring_y1):
            if hand_landmarks.index_y1 < hand_landmarks.pink_y1:
                return True
    return False
 
 
def is_number_eight(hand_landmarks):
    """
    Detecta o gesto do número 8: mínimo mais alto que todos os outros dedos.
    
    Condições:
    - Ângulo do polegar > 40°
    - Mínimo levantado acima de anelar, médio e indicador
    """
    angle = calculate_angle_between_lines(
        (hand_landmarks.thumb_x1, hand_landmarks.thumb_y1),
        (hand_landmarks.wrist_x1, hand_landmarks.wrist_y1)
    )
    if angle > 40 and hand_landmarks.pink_y1 < hand_landmarks.ring_y1:
        if hand_landmarks.pink_y1 < hand_landmarks.middle_y1:
            if hand_landmarks.pink_y1 < hand_landmarks.index_y1:
                return True
    return False
 
 
def is_palm_open(hand_landmarks):
    """
    Detecta palma aberta: todos os dedos levantados e estendidos.
    
    Condições:
    - Anelar acima do DIP do médio
    - Médio é o dedo mais alto (abaixo do polegar, indicador, anelar e mínimo)
    - Anelar acima do seu MCP
    """
    if hand_landmarks.ring_y1 < hand_landmarks.middle_dip_y1:
        if hand_landmarks.middle_y1 < hand_landmarks.thumb_y1:
            if hand_landmarks.middle_y1 < hand_landmarks.index_y1:
                if hand_landmarks.middle_y1 < hand_landmarks.ring_y1:
                    if hand_landmarks.middle_y1 < hand_landmarks.pink_y1:
                        if hand_landmarks.ring_y1 < hand_landmarks.ring_mcp_y1:
                            return True
    return False
 
 
def is_fist_close(hand_landmarks, handpos):
    """
    Detecta punho fechado considerando se a mão está de frente ou de costas.
    
    Condições base:
    - Todos os 4 dedos dobrados (pontas abaixo dos MCPs)
    - Polegar posicionado sobre os dedos (entre o PIP e DIP do indicador)
    
    Para mão de frente: polegar cruzado sobre os dedos (lado esperado)
    Para mão de costas: polegar visível pelo lado oposto
    
    Args:
        hand_landmarks: objeto com os landmarks da mão
        handpos: 'Right' ou 'Left'
    
    Returns:
        bool: True se punho fechado detectado
    """
    if hand_landmarks.index_y1 > hand_landmarks.index_mcp_y1:
        if hand_landmarks.middle_y1 > hand_landmarks.middle_mcp_y1:
            if hand_landmarks.ring_y1 > hand_landmarks.ring_mcp_y1:
                if hand_landmarks.pink_y1 > hand_landmarks.pink_mcp_y1:
                    # Verifica posição do polegar — deve estar sobre os dedos fechados
                    thumb_over_fingers = (
                        hand_landmarks.index_finger_pip_y1 < hand_landmarks.thumb_y1 < hand_landmarks.index_finger_dip_y1
                    ) or (
                        abs(hand_landmarks.thumb_y1 - hand_landmarks.index_finger_pip_y1) < 10
                    )
                    if thumb_over_fingers:
                        # Mão direita de frente: polegar à esquerda do médio
                        if handpos == 'Right' and hand_landmarks.thumb_x1 < hand_landmarks.middle_x1:
                            return True
                        # Mão esquerda de frente: polegar à direita do médio
                        elif handpos == 'Left' and hand_landmarks.thumb_x1 > hand_landmarks.middle_x1:
                            return True
                        # Mão direita de costas
                        elif handpos == 'Right' and \
                             is_front_or_back(hand_landmarks, handpos) == SLIHandEnum.RIGHT_BACK and \
                             ((hand_landmarks.index_mcp_x1 > hand_landmarks.thumb_x1 > hand_landmarks.middle_mcp_x1) or
                              (hand_landmarks.index_mcp_y1 < hand_landmarks.thumb_y1 < hand_landmarks.index_y1)):
                            return True
                        # Mão esquerda de costas
                        elif handpos == 'Left' and \
                             is_front_or_back(hand_landmarks, handpos) == SLIHandEnum.LEFT_BACK and \
                             ((hand_landmarks.index_mcp_x1 > hand_landmarks.thumb_x1 > hand_landmarks.middle_mcp_x1) or
                              (hand_landmarks.index_mcp_y1 < hand_landmarks.thumb_y1 < hand_landmarks.index_y1)):
                            return True
    return False
 
 
def is_front_or_back(hand_landmarks, handpos):
    """
    Determina se a mão está de frente (palma para a câmera) ou de costas.
    
    Lógica: compara a posição horizontal do MCP do indicador com o MCP do mínimo.
    Na mão direita de frente, o indicador fica à esquerda do mínimo (menor X).
    
    Args:
        hand_landmarks: objeto com os landmarks da mão
        handpos: 'Right' ou 'Left'
    
    Returns:
        int: valor do enum SLIHandEnum correspondente
    """
    if handpos == 'Right':
        if hand_landmarks.index_mcp_x1 < hand_landmarks.pink_mcp_x1:
            return SLIHandEnum.RIGHT_FRONT.value
        return SLIHandEnum.RIGHT_BACK.value
 
    # Mão esquerda
    if hand_landmarks.pink_mcp_x1 < hand_landmarks.index_mcp_x1:
        return SLIHandEnum.LEFT_FRONT.value
    return SLIHandEnum.LEFT_BACK.value
 
 
def is_wave_moviment(middle_x1_vector, sensibility):
    """
    Detecta movimento de aceno horizontal analisando um histórico de posições.
    
    A ideia: divide as posições em "acima" e "abaixo" da média.
    Se o padrão '0011' (transição de baixo para cima) aparecer pelo menos
    `sensibility` vezes na janela, classifica como aceno.
    
    Args:
        middle_x1_vector: lista de posições X do dedo médio ao longo do tempo
        sensibility: número mínimo de transições para confirmar o aceno
    
    Returns:
        bool: True se aceno detectado
    """
    window = ''
    average = sum(middle_x1_vector) / len(middle_x1_vector)
 
    # Cada posição vira '1' se está acima da média, '0' se abaixo
    for middle_x1 in middle_x1_vector:
        window += '1' if middle_x1 > average else '0'
 
    # Conta quantas vezes a transição 0→1 aconteceu na janela
    if window.count('0011') >= sensibility:
        return True
    return False