# Creation Date: 2026-03-15
# Authors Alvaro Sampaio
# Developed by: CSI-Lab
# Copyright 2026, INATEL.
# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner

class SLIHandLandMarks:
    """
    Organiza os 21 landmarks da mão retornados pelo MediaPipe em atributos nomeados.
 
    O MediaPipe retorna uma lista plana indexada de 0 a 20.
    Esta classe transforma esses índices em nomes semânticos para tornar
    o código de detecção de gestos legível.
 
    Mapa dos 21 landmarks do MediaPipe Hands:
    ┌──────────────────────────────────────────────────────┐
    │  0  = Pulso (wrist)                                  │
    │  1  = Polegar CMC  (thumb_mcp)                       │
    │  2  = Polegar MCP                                    │
    │  3  = Polegar IP                                     │
    │  4  = Polegar TIP  (thumb)  ← ponta                  │
    │  5  = Indicador MCP (index_mcp)                      │
    │  6  = Indicador PIP (index_finger_pip)               │
    │  7  = Indicador DIP (index_finger_dip)               │
    │  8  = Indicador TIP (index) ← ponta                  │
    │  9  = Médio MCP     (middle_mcp)                     │
    │  10 = Médio PIP                                      │
    │  11 = Médio DIP     (middle_dip)                     │
    │  12 = Médio TIP     (middle)  ← ponta                │
    │  13 = Anelar MCP    (ring_mcp)                       │
    │  14 = Anelar PIP    (ring_pip)                       │
    │  15 = Anelar DIP                                     │
    │  16 = Anelar TIP    (ring)    ← ponta                │
    │  17 = Mínimo MCP    (pink_mcp)                       │
    │  18 = Mínimo PIP                                     │
    │  19 = Mínimo DIP                                     │
    │  20 = Mínimo TIP    (pink)    ← ponta                │
    └──────────────────────────────────────────────────────┘
 
    Convenção de coordenadas na imagem:
    - X cresce da esquerda para a direita
    - Y cresce de CIMA para BAIXO (padrão de imagem)
    - Portanto: dedo levantado → ponta tem Y MENOR que a base
    """
 
    def __init__(self, hand_landmarks):
        """
        Args:
            hand_landmarks: lista de [[id, x, y], ...] com 21 landmarks em pixels
        """
 
        # --- Pontas dos dedos (TIP) ---
        self.thumb_x1,  self.thumb_y1  = hand_landmarks[4][1],  hand_landmarks[4][2]   # Polegar
        self.index_x1,  self.index_y1  = hand_landmarks[8][1],  hand_landmarks[8][2]   # Indicador
        self.middle_x1, self.middle_y1 = hand_landmarks[12][1], hand_landmarks[12][2]  # Médio
        self.ring_x1,   self.ring_y1   = hand_landmarks[16][1], hand_landmarks[16][2]  # Anelar
        self.pink_x1,   self.pink_y1   = hand_landmarks[20][1], hand_landmarks[20][2]  # Mínimo
 
        # --- Articulações MCP (base dos dedos, onde se dobram) ---
        self.index_mcp_x1,  self.index_mcp_y1  = hand_landmarks[5][1],  hand_landmarks[5][2]
        self.middle_mcp_x1, self.middle_mcp_y1 = hand_landmarks[9][1],  hand_landmarks[9][2]
        self.ring_mcp_x1,   self.ring_mcp_y1   = hand_landmarks[13][1], hand_landmarks[13][2]
        self.pink_mcp_x1,   self.pink_mcp_y1   = hand_landmarks[17][1], hand_landmarks[17][2]
        self.thumb_mcp_x1,  self.thumb_mcp_y1  = hand_landmarks[1][1],  hand_landmarks[1][2]
 
        # --- Pulso --- CORRIGIDO: "wirst" → "wrist"
        self.wrist_x1, self.wrist_y1 = hand_landmarks[0][1], hand_landmarks[0][2]
 
        # --- Articulações intermediárias (PIP e DIP) ---
        # PIP = articulação proximal (primeira dobra do dedo)
        # DIP = articulação distal (segunda dobra do dedo)
        self.ring_pip_x1,          self.ring_pip_y1          = hand_landmarks[14][1], hand_landmarks[14][2]
        self.index_finger_pip_x1,  self.index_finger_pip_y1  = hand_landmarks[6][1],  hand_landmarks[6][2]
        self.middle_dip_x1,        self.middle_dip_y1        = hand_landmarks[11][1], hand_landmarks[11][2]
        # CORRIGIDO: "index_finder_dip" → "index_finger_dip"
        self.index_finger_dip_x1,  self.index_finger_dip_y1  = hand_landmarks[7][1],  hand_landmarks[7][2]