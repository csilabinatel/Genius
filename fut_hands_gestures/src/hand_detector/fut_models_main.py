# Creation Date: 2026-03-15
# Authors Alvaro Sampaio
# Developed by: CSI-Lab
# Copyright 2026, INATEL.

# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner
# MELHORIA 2 — Arquivo simplificado (separação de responsabilidades):
#   Antes: ~130 linhas misturando câmera, MQTT, UI e lógica de negócio.
#   Depois: ~80 linhas, só orquestra os módulos camera_capture e mqtt_client.
#   O main agora responde apenas "o que fazer", não "como fazer".
#
# BUG 3 CORRIGIDO — Credenciais movidas para constantes nomeadas:
#   Antes: "csilab" e "WhoAmI#2024" estavam no meio do código.
#   Depois: constantes no topo, fáceis de encontrar e modificar.
#   Próximo passo: mover para arquivo .env com python-dotenv.
#
# BUG FIX — system_status sem chave "dimmer_value":
#   Antes: {"lamp_status": None, "lamp_number": None}
#          Causava KeyError ao comparar system_status["dimmer_value"] em control_objects.
#   Depois: a chave "dimmer_value" foi adicionada ao dicionário inicial.
#
# MELHORIA 3 — Tratamento de erro de câmera delegado ao SLICameraCapture:
#   Antes: if not ret: break — quebrava silenciosamente sem mensagem.
#   Depois: SLICameraCapture.read_frame() tenta reconectar e retorna None
#           se não conseguir. O main verifica o None e encerra de forma limpa.
# ═

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from modules.fut_remote_controller import SLIRemoteController
import paho.mqtt.client as mqtt #pip install paho-mqtt
import json
import cv2
import sys
import dotenv
import os

from dotenv import load_dotenv

load_dotenv()

# Topics and PlayerID
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
PLAYER_ID = os.getenv("PLAYER_ID")
TOPIC_GENIUS = os.getenv("TOPIC_GENIUS")
TOPIC_VELHA = f"JogoDaVelha/Session1/{PLAYER_ID}/escolha"
TOPIC_DIMMER = os.getenv("TOPIC_DIMMER")

# Draw the detection on the screen
def draw_detections(frame, message):
    """
    Desenha na tela o gesto detectado para feedback visual.

    MELHORIA 2: pequena refatoração — usa message.get() em vez de
    acessar as chaves diretamente, evitando KeyError se alguma chave
    estiver ausente no dicionário.
    """
    if not message:
        return

    if message.get("hand") == "Left":
        text = "CLICKING" if message.get("click_status") else str(message.get("number"))
        cv2.putText(frame, text, (100, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    if message.get("hand") == "Right":
        # Determina qual texto exibir baseado no comando ativo
        text = None
        if message.get("open_palm"):    text = "TURN ON"
        elif message.get("close_fist"): text = "TURN OFF"
        elif message.get("env_var"):    text = "SHOW VAR STATUS"
        elif message.get("graphs"):     text = "SHOW GRAPHS"
        elif message.get("remove_all"): text = "REMOVE EVERYTHING"
        elif message.get("dimmer_value") is not None:
            text = "DIMMER: " + str(message["dimmer_value"])

        if text:
            cv2.putText(frame, text, (360, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)


def control_objects(topic, right_hand_message, left_hand_message, system_status, mqtt):
    """
    Combina os gestos das duas mãos e publica o comando via MQTT.

    Lógica:
    - Mão direita define ESTADO: ligar (1), desligar (0) ou valor do dimmer
    - Mão esquerda define QUAL lâmpada/posição (número 1-10)
    - Só publica se algo mudou desde o último comando enviado

    Args:
        topic:              tópico MQTT de destino
        right_hand_message: dict do gesto da mão direita
        left_hand_message:  dict do gesto da mão esquerda
        system_status:      dict com o último estado publicado (evita republicar)
        mqtt:               instância de SLIMQTTClient
    """
    lamp_number = None
    lamp_status = None
    dimmer      = None

    # Interpreta mão direita → o QUE fazer com a lâmpada
    if right_hand_message:
        if right_hand_message.get("open_palm") and not right_hand_message.get("close_fist"):
            lamp_status = 1   # ligar
        elif not right_hand_message.get("open_palm") and right_hand_message.get("close_fist"):
            lamp_status = 0   # desligar
        elif right_hand_message.get("dimmer_value") is not None:
            dimmer = right_hand_message["dimmer_value"]

    # Interpreta mão esquerda → QUAL lâmpada
    if left_hand_message and left_hand_message.get("number") is not None:
        lamp_number = str(left_hand_message["number"])

    # Só executa se ambas as mãos deram informações válidas
    if lamp_number is not None and (lamp_status is not None or dimmer is not None):

        # Verifica se houve mudança de estado — evita spam de MQTT
        state_changed = (
            system_status["lamp_status"]  != lamp_status or
            system_status["lamp_number"]  != lamp_number or
            system_status["dimmer_value"] != dimmer   # BUG FIX: chave que faltava
        )

        if state_changed:
            if topic == TOPIC_VELHA:
                # Jogo da Velha: só publica quando o gesto é "ligar" (lamp_status == 1)
                if lamp_status == 1:
                    mqtt.publish(topic, '{"lampada":' + str(lamp_number) + '}')
            else:
                # Genius e Dimmer: publica o estado completo
                mqtt.publish(topic, {
                    "left_hand":          int(lamp_number),
                    "right_hand_message": lamp_status,
                    "dimmer":             dimmer
                })

            # Atualiza o estado salvo para a próxima comparação
            system_status["lamp_status"]  = lamp_status
            system_status["lamp_number"]  = lamp_number
            system_status["dimmer_value"] = dimmer  # BUG FIX: chave que faltava


if __name__ == '__main__':

    # ── MQTT ──────────────────────────────────────────────────────
    # MELHORIA 2: antes eram ~6 linhas com client, callbacks e connect espalhadas.
    # Agora é uma instância de classe com interface limpa.
    mqtt_client = SLIMQTTClient(MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD)
    if not mqtt_client.connect():
        # MELHORIA 3: antes o código continuava mesmo sem conexão MQTT.
        # Agora encerra de forma limpa com código de saída 1 (erro).
        print("Encerrando por falha de conexão MQTT.")
        sys.exit(1)

    # ── Menu ──────────────────────────────────────────────────────
    print("\nEscolha o módulo desejado:")
    print("1 - Genius")
    print("2 - Jogo da VeIA")
    print("3 - Dimerizador")

    try:
        x = int(input("> "))
    except ValueError:
        print("Entrada inválida! Digite 1, 2 ou 3.")
        sys.exit(1)

    if x == 1:
        print("Iniciando Genius...")
        remote_controller = SLIRemoteController(dimmer_flag=False)
        topic = TOPIC_GENIUS
    elif x == 2:
        print("Iniciando Jogo da VeIA...")
        remote_controller = SLIRemoteController(dimmer_flag=False)
        topic = TOPIC_VELHA
        mqtt_client.publish(f"JogoDaVelha/Session1/subClient", PLAYER_ID)
    elif x == 3:
        print("Iniciando Dimerizador...")
        remote_controller = SLIRemoteController(dimmer_flag=True)
        topic = TOPIC_DIMMER
    else:
        print("Escolha inválida!")
        sys.exit(1)

    # BUG FIX: "dimmer_value" adicionado ao dicionário inicial.
    # Antes estava ausente, causando KeyError na função control_objects
    # quando o módulo dimerizador tentava comparar o estado anterior.
    system_status = {
        "lamp_status":  None,
        "lamp_number":  None,
        "dimmer_value": None  # ← chave que faltava
    }

    # ── Câmera ────────────────────────────────────────────────────
    # MELHORIA 2: antes eram ~15 linhas de cálculo de ROI e VideoCapture
    # espalhadas no main. Agora são 3 linhas.
    camera = SLICameraCapture(camera_index=0)
    if not camera.open():
        print("Encerrando por falha na câmera.")
        mqtt_client.disconnect()
        sys.exit(1)

    print("Sistema iniciado. Pressione 'q' para encerrar.")
    running = True

    while running:
        # MELHORIA 3: read_frame() já trata reconexão internamente.
        # Se retornar None, a câmera não pôde ser recuperada — encerra.
        frame = camera.read_frame()
        if frame is None:
            print("Câmera indisponível. Encerrando.")
            break

        # MELHORIA 2: get_roi() encapsula o recorte — o main não precisa
        # saber as coordenadas das ROIs.
        roi_right = camera.get_roi(frame, "Right")
        roi_right, right_hand_message = remote_controller.process_frame(roi_right, roi_side="Right")

        roi_left = camera.get_roi(frame, "Left")
        roi_left, left_hand_message = remote_controller.process_frame(roi_left, roi_side="Left")

        # Publica no MQTT se gestos válidos foram confirmados
        control_objects(topic, right_hand_message, left_hand_message, system_status, mqtt_client)

        # MELHORIA 2: draw_rois() encapsula o desenho dos retângulos.
        camera.draw_rois(frame)
        draw_detections(frame, left_hand_message)
        draw_detections(frame, right_hand_message)

        cv2.imshow("Hands Landmarks", frame)

        if cv2.waitKey(1) == ord('q'):
            running = False

    # ── Limpeza ───────────────────────────────────────────────────
    # MELHORIA 2: encerramento explícito e organizado dos recursos.
    # Antes: cap.release() e client.loop_stop() estavam soltos no final do main.
    camera.release()
    mqtt_client.disconnect()
    cv2.destroyAllWindows()