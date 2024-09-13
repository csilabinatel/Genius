import paho.mqtt.client as mqtt #pip install paho-mqtt
import random
import time
import json

rodada = 0
cont = 0
seq = list()
seq.append(random.randint(1, 6))

def errou():
    for x in range(2):

        client.publish("lamp_module/setState",'{"lampada": 1,"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": 2,"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": 3,"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": 4,"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": 5,"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": 6,"estado": 1}')

        client.publish("lamp_module/setState",'{"lampada": 1,"estado": 0}')
        client.publish("lamp_module/setState",'{"lampada": 2,"estado": 0}')
        client.publish("lamp_module/setState",'{"lampada": 3,"estado": 0}')
        client.publish("lamp_module/setState",'{"lampada": 4,"estado": 0}')
        client.publish("lamp_module/setState",'{"lampada": 5,"estado": 0}')
        client.publish("lamp_module/setState",'{"lampada": 6,"estado": 0}')

def mostrar_seq(rodada):
    global cont

    client.publish("lamp_module/setState",'{"lampada": 1,"estado": 0}')
    client.publish("lamp_module/setState",'{"lampada": 2,"estado": 0}')
    client.publish("lamp_module/setState",'{"lampada": 3,"estado": 0}')
    client.publish("lamp_module/setState",'{"lampada": 4,"estado": 0}')
    client.publish("lamp_module/setState",'{"lampada": 5,"estado": 0}')
    client.publish("lamp_module/setState",'{"lampada": 6,"estado": 0}')

    
    for x in range (0,rodada+1):
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 1}')
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 0}')
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 0}')
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 0}')
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 0}')
        client.publish("lamp_module/setState",'{"lampada": '+ str( seq[x] ) +',"estado": 0}')

    print(seq)

    cont = 0


def verifica(lamp):
    global rodada,cont,seq
    if seq[cont] == lamp:
        if cont == rodada:
            rodada += 1
            cont = 0
            seq.append(random.randint(1, 6))
            mostrar_seq(rodada)
        else:
            cont += 1   
        client.publish("lamp_module/setState",'{"lampada": '+ str( lamp ) +',"estado": 0}')
    else:
        errou()
        rodada = 0
        cont = 0
        seq.clear()
        seq.append(random.randint(1, 6))
        mostrar_seq(rodada)

def on_connect(client, userdata, flags, rc):
    print("Conectado - Codigo de resultado: "+str(rc))

    # Indique o tópico a ser assinado - "#" se inscreve em todos
    client.subscribe("lamp_module/#")
    mostrar_seq(rodada)

#função onde recebe mensagens 
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode()))
    lista = msg.topic.split("/")

    if lista[0] == "lamp_module":

        if lista[1] == "choice":
            print(msg.payload.decode())
            aux = json.loads(msg.payload.decode())
            if aux["right_hand_message"] == 1:
                lamp = aux['left_hand']
                client.publish("lamp_module/setState",'{"lampada": '+str(lamp)+',"estado": 1}')
                verifica(int(lamp))
        
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
		
try:
    client.username_pw_set("csilab", "WhoAmI#2024")    
    client.connect("192.168.40.7", 1883, 60) #Mude o hostname para o IP do servidor
except:
    print("Não foi possivel conectar ao MQTT...")
    print("Encerrando...")

 
try:
    client.loop_forever()
except KeyboardInterrupt:  #precionar Crtl + C para salir
    print("Encerrando...")