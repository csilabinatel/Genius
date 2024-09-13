# Creation Date: 2024-06-07
# Authors Murilo Cruz Lopes, Ludwing Ferney Marenco Camacho
# Developed by: Inatel Competence Center
# Copyright 2024, INATEL.
# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner


from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from modules.fut_remote_controller import SLIRemoteController
import paho.mqtt.client as mqtt #pip install paho-mqtt
import json
import cv2
import sys

# Topics and PlayerID
playerID = "jogador1"
topic_genius = "lamp_module/choice"
topic_velha = f"JogoDaVelha/Session1/{playerID}/escolha"
topic_dimmer = "rgb_module/dimmer/setLampState"

# Draw the detection on the screen
def draw_detections(frame, message):
    if len(message) != 0:
        if message["hand"] == "Left":
            if message["click_status"]:
                cv2.putText(frame, "CLICKING", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA, False)
            else:
                cv2.putText(frame, str(message["number"]), (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA, False)
        if message["hand"] == "Right":
            if message["open_palm"]:
                cv2.putText(frame, "TURN ON", (360, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA, False)
            if message["close_fist"]:
                cv2.putText(frame, "TURN OFF", (360, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA, False)
            if message["env_var"]:
                cv2.putText(frame, "SHOW VAR STATUS", (360, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA, False)
            if message["graphs"]:
                cv2.putText(frame, "SHOW GRAPHS", (360, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA, False)
            if message["remove_all"]:
                cv2.putText(frame, "REMOVE EVERYTHING", (360, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA, False)
            if message["dimmer_value"] is not None:
                cv2.putText(frame, "DIMMER: " + str(message["dimmer_value"]), (360, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA, False)


# Organize the information about the hand and send it to the mqqt server
def control_objects(topic, right_hand_message, left_hand_message, system_status, client = None):
    lamp_number = None
    lamp_status = None
    dimmer = None
    msg = None

    if len(right_hand_message) != 0:
        if right_hand_message["open_palm"] == True and right_hand_message["close_fist"] == False:
            lamp_status = 1
        elif right_hand_message["open_palm"] == False and right_hand_message["close_fist"] == True:
            lamp_status = 0
        elif "dimmer_value" in right_hand_message:
            dimmer = right_hand_message['dimmer_value']
        
    if len(left_hand_message) != 0 and left_hand_message["number"] is not None:
        lamp_number = str(left_hand_message["number"])

    if lamp_number is not None and (lamp_status is not None or dimmer is not None):
        if system_status['lamp_status'] != lamp_status or system_status['lamp_number'] != lamp_number or system_status['dimmer_value'] != dimmer:
            if topic == topic_velha:
                if lamp_status == 1:
                    client.publish(topic, '{"lampada":'+str(lamp_number)+'}')
            else:
                msg = {"left_hand":int(lamp_number), "right_hand_message":lamp_status, "dimmer": dimmer}
                print(msg)
                client.publish(topic, json.dumps(msg))
            system_status['lamp_status'] = lamp_status
            system_status['lamp_number'] = lamp_number
            system_status['dimmer_value'] = dimmer


# Função para conexão
def on_connect(client, userdata, flags, rc):
    print("Conectado - Codigo de resultado: "+str(rc))
    # Indique o tópico a ser assinado - "#" se inscreve em todos
    client.subscribe("#")

#função onde recebe mensagens
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode()))

if __name__ == '__main__':

    # Realiza a conexão assim que o código inicia
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    print ("Connecting to the Server...")
    try:
        client.username_pw_set("csilab", "WhoAmI#2024")
        client.connect("192.168.40.7", 1883, 60) #Mude o hostname para o IP do servidor
    except:
        print("Não foi possivel conectar ao MQTT...")
        print("Encerrando...")

    # Interface de escolha de Módulo
    print("escolha o módulo desejado:")
    print("1 - Genius")
    print("2 - Jogo da VeIA")
    print("3 - Dimerizador")

    # Variável aux escolha
    x = int(input())

    # Tomada de decisão 
    if x == 1:
        print("Iniciando Genius ...")
        remote_controller = SLIRemoteController(dimmer_flag=False)
        topic = topic_genius
    elif x == 2:
        print("Iniciando Jogo da VeIA ...")
        remote_controller = SLIRemoteController(dimmer_flag=False)
        topic = topic_velha
        client.publish("JogoDaVelha/Session1/subClient", playerID)
    elif x == 3:
        print("Iniciando Dimerizador ...")
        remote_controller = SLIRemoteController(dimmer_flag=True)
        topic = topic_dimmer
    else:
        print("Escolha inválida!")
        sys.exit()

    system_status = {"lamp_status": None, "lamp_number": None}

    cap = cv2.VideoCapture(0)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    running=True

    ## This peace of code is to adjust the roi for each resolution video
    left_box_x1 = int(0*width) #0
    left_box_y1 = int(0.054*height) # 26
    left_box_x2 = int(0.4375*width) # 280
    left_box_y2 = int(0.7395*height) # 355

    right_box_x1 = int(0.5625*width) # 360
    right_box_y1 = int(0.054*height) # 26
    right_box_x2 = int(1*width) # 640
    right_box_y2 = int(0.7395*height) # 355

    while running:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        roi_right_hand = frame[right_box_y1:right_box_y2, right_box_x1:right_box_x2]
        roi_right_hand, right_hand_message = remote_controller.process_frame(roi_right_hand, roi_side = "Right") # passa o frame e retorna as detecções e a mensagem no formato json

        roi_left_hand = frame[left_box_y1:left_box_y2, left_box_x1:left_box_x2]
        roi_left_hand, left_hand_message = remote_controller.process_frame(roi_left_hand, roi_side = "Left")

        control_objects(topic, right_hand_message, left_hand_message, system_status, client)

        cv2.rectangle(frame, (left_box_x1, left_box_y1), (left_box_x2, left_box_y2), (255, 0, 0), 2)
        cv2.rectangle(frame, (right_box_x1, right_box_y1), (right_box_x2, right_box_y2), (255, 0, 0), 2)
        cv2.putText(frame, "RIGHT HAND HERE", (right_box_x1 - 5, right_box_y1*2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA, False)
        cv2.putText(frame, "LEFT HAND HERE", (left_box_x1 + 10, left_box_y1*2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA, False)

        draw_detections(frame, left_hand_message)
        draw_detections(frame, right_hand_message)

        cv2.imshow("Hands Landmarks", frame)
        if cv2.waitKey(1) == ord('q'):
            running=False
            client.loop_stop()

    cap.release()
    cv2.destroyAllWindows()