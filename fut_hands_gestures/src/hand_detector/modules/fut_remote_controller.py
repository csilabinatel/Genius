# Creation Date: 2026-03-15
# Authors Alvaro Sampaio
# Developed by: CSI-Lab
# Copyright 2026, INATEL.
# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner

'''
Mudanças :
Bug1 = Numeros 8 e 9 estavam com retornos TROCADOS
    Antes : is_number_eight retornava {'number' : 9}
    Depois : is_number_eight retorna {'number' : 8}
    Impacto : Mapeando as lampadas erradas no sistema

Melhoria 1: Debouce adicionado
    Antes : 1 unico frame de gesto detectado ja disparava o comando no mqtt
    Depois : O gesto precisa aparecer em DEBOUNCES_FRAME seguidos
    Impacto : Evita que o comando seja disparado varias vezes por um unico gesto

Melhoria 2: Removido import JSON
    Antes : import json estava no arquivo mas nunca era usado
    Depois : Import removido


'''
from modules.fut_hand_detector import SLIHandDetector
from utils.fut_hand_landmarks_utils import SLIHandLandMarks
import modules.fut_gesture_detector as gd
from collections import deque # Import deque para implementar o debounce
import json

#Melhoria 1: CTe que define quantos frames seguidos preisa aparecer
# Valor 5 ~= 166ms em 30fps, se aumentar, temos menos sensibilidade
#Mais responsividade, se diminuir, temos mais estabilidade
DEBOUNCE_FRAMES = 5


class SLIRemoteController():
    '''
    Controlador remoto baseado nos gestos

    Mao direita -> Comandos de controle (liga/desliga, dimmer, gráficos)
    Mao esquerda -> Seleciona numero de 1 a 10 (lampada ou posição)
    
    '''

    def __init__(self, dimmer_flag = False, debounce_frames = DEBOUNCE_FRAMES):
        '''
        DIMMER FLAG : Habilita ou desabilita o controle de dimmer, caso seja habilitado, o valor do dimmer é retornado no dicionário de comando, caso seja desabilitado, o valor do dimmer é retornado como None
            Dimmer = true = controle ativo de dimmer pela mão direita, o valor do dimmer é retornado no dicionário de comando
            Dimmer = false = controle de dimmer desativado, o valor do dimmer
        Debounce frames : Define quantos frames seguidos o mesmo gesto precisa aparecer para ser considerado um comando válido, isso ajuda a evitar que um comando seja disparado várias vezes por um único gesto, aumentando a estabilidade do sistema, mas reduzindo a sensibilidade
        
        # MELHORIA 1: dois buffers circulares, um para cada mão.
        # Cada buffer guarda os últimos `debounce_frames` gestos detectados.
        # Exemplo com DEBOUNCE_FRAMES=5:
        #   Frame 1: "open_palm" → buffer: ["open_palm"]
        #   Frame 2: "open_palm" → buffer: ["open_palm", "open_palm"]
        #   Frame 3: "None"      → buffer: ["open_palm", "open_palm", "None"]  ← resetou
        #   Frame 4: "open_palm" → buffer: ["open_palm", "open_palm", "None", "open_palm"]
        #   Frame 5: "open_palm" → buffer: [5x "open_palm"] → CONFIRMADO!
        '''
        self._hand_detector = SLIHandDetector(min_detection_confidence=0.9)
        self.dimmer_flag = dimmer_flag
        self.debounce_frames = debounce_frames
        self._gesture_buffer = {
            'Left' : deque(maxlen=debounce_frames),  # Buffer para a mão esquerda
            'Right': deque(maxlen=debounce_frames)   # Buffer para a mão direita
        }

        #Guardando  o ultimo comando para cada mão, para comparar com o buffer e evitar repetições
        #Para nao disparar o mesmo comando varias vezes, caso o gesto seja mantido por muitos frames
        self._last_confirmed = {
            'Left' : None,
            'Right': None
        }

    def _debounce(self, side, gesture_key):
        """
        Controle geral do debounce
        Recebe : Gesto detectado no frame atual e decide se ele foi
        confirmado (apareceu N vezes seguidos) ou nao
        Exemplo visual com DEBOUNCE_FRAMES = 3:
            Chamada 1: gesture_key="1" → buffer=["1"]           → retorna None
            Chamada 2: gesture_key="1" → buffer=["1","1"]       → retorna None
            Chamada 3: gesture_key="1" → buffer=["1","1","1"]   → retorna "1" ✓
            Chamada 4: gesture_key="1" → buffer=["1","1","1"]   → retorna None (mesmo gesto, não dispara de novo)
            Chamada 5: gesture_key="2" → buffer=["1","1","2"]   → retorna None (quebrou a sequência)
        """


        buffer = self._gesture_buffer[side]
        #Adicionar o gesto atual ao buffer
        #Se o buffer estiver cheio o elemento mais antigo é retirado
        buffer.append(gesture_key)
        #Verificar se o buffer está cheio e se todos os elementos são iguais
        if len(buffer) == self.debounce_frames and len(set(buffer)) == 1:
            confirmed = buffer[0]

            # Só dispara se for diferente do último gesto confirmado.
            # Sem isso, ficaria disparando o mesmo comando enquanto o gesto fosse mantido.
            if confirmed != self._last_confirmed[side]:
                self._last_confirmed[side] = confirmed
                return confirmed
        #Gesto ainda nao confirmado, o chamador deve ignorar esse resultado
        return None

    def __get_command_gesture(self, land_marks, hand_pos):
        """
        Interpreta o gesto da mao DIREITA  e retorna o comando correspondente em um dicionário, o dicionário tem as seguintes chaves:

        Mudança : Agora aplica debounce antes de retornar qualquer comando
        O dimmer é uma exceção, ele é retornado em tempo real, sem debounce, para permitir um controle mais fluido, mas os outros comandos (open_palm, close_fist, env_var, graphs, remove_all) só são retornados quando o gesto é confirmado pelo debounce


        
        """
        command_dic = {}
        command_dic["hand"] = "Right"
        command_dic["open_palm"] = False
        command_dic["close_fist"] = False
        command_dic["env_var"] = False
        command_dic["graphs"] = False
        command_dic["remove_all"] = False
        command_dic["dimmer_value"]= None

        number = self.__get_gesture_number(land_marks, hand_pos)
        # MElhoria 1 : Cada gesto vira uma string-chave para o debounce
        #Antes o gesto era retornado diretamente, agora ele é processado pelo debounce antes de ser considerado um comando válido
        if number == 1:
            gesture_key = "env_var"
        elif number == 2:
            gesture_key = "graphs"
        elif number == 3:
            gesture_key = "remove_all"
        elif gd.is_palm_open(land_marks):
            gesture_key = "open_palm"
        elif gd.is_fist_close(land_marks, hand_pos):
            gesture_key = "close_fist"
        else:
            # Dimmer: valor contínuo entre 0-100, atualiza todo frame.
            # Não aplica debounce pois o usuário espera resposta imediata ao mover os dedos.
            angulo, relative_value = gd.controll_dimmer(land_marks)
            if 0 <= angulo <= 43 and self.dimmer_flag:
                command_dic["dimmer_value"] = relative_value
            return command_dic
        #Preenche o comando se o debounce confirmar
        #Se retornar NONE, comand_dic volta com todos os flags
        #O sistema ignora esse frame se nenhum gesto for confirmado
        confirmed = self._debounce("Right", gesture_key)
        if confirmed:
            command_dic[confirmed] = True
        return command_dic


    def __get_gesture_number(self, hand_landmark, hand_position = None):
        '''
        Identifica qual numero esta sendo gesticulado
        Mao direita = retorna inteiro (1,2,3)  ou None
        Mao esquerda = retorna dict{'hand' : 'Left', 'number' : int} ou {'hand' : 'Left', 'number' : None}
        '''

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

        if gd.is_palm_open(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 5}

        if gd.is_number_six(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 6}

        if gd.is_number_seven(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 7}

        if gd.is_number_eight(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 8}

        if gd.is_number_nine(hand_landmark) and hand_position == "Left":
            return {"hand": "Left", "number": 9}

        if gd.is_fist_close(hand_landmark, 'Left'):
            return {"hand": "Left", "number": 10}
        
        if hand_position == "Right":
            return None

        return {"hand": "Left", "number": None}


    def process_frame(self, frame, roi_side = None):
        """
        Processa um frame da ROI e retorna o gesto detectado em um dicionário, o formato do dicionário depende da mão que está presente na ROI:

        Args : frame : imagem RGB ja recortada para ROI
                roi_side : "Left" ou "Right", indica qual lado da ROI está sendo processado, isso é importante para interpretar corretamente os gestos, já que a mesma configuração de dedos pode significar coisas diferentes dependendo da mão (ex: palma aberta na mão esquerda é número 5, enquanto na mão direita é um comando de controle)
        
        Retorno : tupla com as landmarks desenhadas no frame e um dicionário com o gesto detectado, o formato do dicionário depende da mão que está presente na ROI:
            Se a mão for a esquerda, o dicionário tem as chaves 'hand'
        """
        
        hand_landmarks = self._hand_detector.find_hand_landmarks(image = frame, draw=True)

        hand_position = list(hand_landmarks.keys())

        if len(hand_position) != 0:
            land_marks = SLIHandLandMarks(hand_landmarks[hand_position[0]])

            if hand_position[0] == "Left" and roi_side == "Left":
                left_hand_dic = self.__get_gesture_number(land_marks, "Left")
                _, dimmer_value = gd.controll_dimmer(land_marks)
                
                #Convertendo o numero para string para usar como chave no debounce
                # None (string) representa a ausência de um gesto reconhecido, ou seja, quando o número detectado não é nenhum dos gestos válidos (1-10)
                number_key = str(left_hand_dic["number"]) if left_hand_dic["number"] is not None else "None"
                #Aplicando debounce no gesto de número
                confirmed_number = self._debounce("Left", number_key)


                if dimmer_value == 0:
                    # Dimmer no mínimo = clique (confirma seleção da lâmpada)
                    left_hand_dic["click_status"] = True
                    left_hand_dic["number"] = None
                elif dimmer_value < 99 and left_hand_dic.get("number") == 7:
                    # Gesto 7 conflita com posição do dimmer — ignora o número
                    left_hand_dic["number"] = None
                    left_hand_dic["click_status"] = False
                else:
                    # MELHORIA 1: se o debounce não confirmou, anula o número.
                    # Antes, o número era propagado mesmo sem confirmação.
                    if not confirmed_number:
                        left_hand_dic["number"] = None
                    left_hand_dic["click_status"] = False

                return frame, left_hand_dic

            if hand_position[0] == "Right" and roi_side == "Right":
                return frame, self.__get_command_gesture(land_marks, hand_position[0])

        else:
            # MELHORIA 1: quando a mão sai de cena, limpa o buffer.
            # Sem isso, gestos de frames anteriores continuariam acumulados
            # e poderiam confirmar um gesto incorretamente na próxima vez
            # que a mão entrasse na ROI.
            if roi_side in self._gesture_buffer:
                self._gesture_buffer[roi_side].clear()
                self._last_confirmed[roi_side] = None

        return frame, {}