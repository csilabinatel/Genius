import paho.mqtt.client as mqtt #pip install paho-mqtt
import json
import numpy as np

turno = True

# Criando uma matriz 3x3 inicializada com espaços vazios
tabuleiro = np.full((3, 3), "")

clientID_01 = ""
clientID_02 = ""

# Função para converter índice de 1 a 9 para índice de matriz
def indice_para_matriz(indice):
    if 1 <= indice <= 9:
        linha = (indice - 1) // 3
        coluna = (indice - 1) % 3
        return linha, coluna
    else:
        raise ValueError("Índice deve estar entre 1 e 9.")

# Função para definir o valor do tabuleiro usando índice de 1 a 9
def definir_valor(indice, valor):
    linha, coluna = indice_para_matriz(indice)
    if tabuleiro[linha, coluna] == '':
        tabuleiro[linha, coluna] = valor
    else:
        raise ValueError("Essa posição já está ocupada.")

# Função para verificar se um jogador venceu
def verificar_vitoria(jogador):
    # Verificar linhas
    for linha in tabuleiro:
        if np.all(linha == jogador):
            return True

    # Verificar colunas
    for coluna in tabuleiro.T:
        if np.all(coluna == jogador):
            return True

    # Verificar diagonais
    if np.all(np.diag(tabuleiro) == jogador):
        return True
    if np.all(np.diag(np.fliplr(tabuleiro)) == jogador):
        return True
    
    return False

# Função para verificar se houve empate
def verificar_empate(tabuleiro):
    # Se todas as posições estão preenchidas e não há vencedor
    if np.all(tabuleiro != ''):
        if not (verificar_vitoria('X') or verificar_vitoria('O')):
            return True
    return False

def obter_valor(indice):
    linha, coluna = indice_para_matriz(indice)
    return tabuleiro[linha, coluna]

def game_over(ganhador):
    global tabuleiro
    for i in range(3):
        for i in range(1,10):
            if ganhador == 'X':
                msg = '{"lampada":'+str(i)+',"r":255,"g":0,"b":0}'
            if ganhador == 'O':
                msg = '{"lampada":'+str(i)+',"r":0,"g":0,"b":255}'
            if ganhador == '-':
                msg = '{"lampada":'+str(i)+',"r":255,"g":255,"b":255}'
            client.publish("rgb_module/veia/setLampState",msg)

        for i in range(1,10):
            client.publish("rgb_module/veia/setLampState",'{"lampada":'+str(i)+',"r":0,"g":0,"b":0}')
    tabuleiro = np.full((3, 3), "")


def on_connect(client, userdata, flags, rc):
    print("Conectado - Codigo de resultado: "+str(rc))

    # Indique o tópico a ser assinado - "#" se inscreve em todos
    client.subscribe("JogoDaVelha/Session1/#")

#função onde recebe mensagens 
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode()))
    lista = msg.topic.split("/")
    global turno
    
    if len(lista) == 3:
        if lista[2] == "subClient":
            global clientID_01,clientID_02
            if clientID_01 == "":
                clientID_01 = msg.payload.decode()
                return
            if clientID_02 == "":
                clientID_02 = msg.payload.decode()
                return
            
    if len(lista) == 4:
        js = json.loads(str(msg.payload.decode()))
        if lista[2] == clientID_01:
            if turno != True:
                return
            if lista[3] == "escolha":
                if obter_valor(js["lampada"]) == "":
                    definir_valor(js["lampada"],'X')
                    client.publish("rgb_module/veia/setLampState",'{"lampada":'+str(js["lampada"])+',"r":255,"g":0,"b":0}')
                    turno = not(turno)
                    if verificar_vitoria('X'):
                        game_over('X')
                    if verificar_empate(tabuleiro):
                        game_over('-')

        if lista[2] == clientID_02:
            if turno != False:
                return
            if lista[3] == "escolha":
                if obter_valor(js["lampada"]) == "":
                    definir_valor(js["lampada"],'O')
                    client.publish("rgb_module/veia/setLampState",'{"lampada":'+str(js["lampada"])+',"r":0,"g":0,"b":255}')
                    turno = not(turno)
                    if verificar_vitoria('O'):
                        game_over('O')
                    if verificar_empate(tabuleiro):
                        game_over('-')


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