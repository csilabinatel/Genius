import json
import time

import numpy as np
import paho.mqtt.client as mqtt  # pip install paho-mqtt


turno = True
jogada = 0
partida = 1
pontos = {"X": 0, "O": 0}
recorde = 0

tabuleiro = np.full((3, 3), "")

clientID_01 = ""
clientID_02 = ""

TOPICO_LAMPADAS = "rgb_module/veia/setLampState"
TOPICO_SCORE = "JogoDaVelha/Session1/score"

CORES = {
    "X": {"r": 255, "g": 0, "b": 0},
    "O": {"r": 0, "g": 0, "b": 255},
    "-": {"r": 255, "g": 255, "b": 255},
    "ok": {"r": 0, "g": 255, "b": 80},
    "erro": {"r": 255, "g": 180, "b": 0},
    "apagado": {"r": 0, "g": 0, "b": 0},
}


def indice_para_matriz(indice):
    if 1 <= indice <= 9:
        linha = (indice - 1) // 3
        coluna = (indice - 1) % 3
        return linha, coluna
    raise ValueError("Indice deve estar entre 1 e 9.")


def definir_valor(indice, valor):
    linha, coluna = indice_para_matriz(indice)
    if tabuleiro[linha, coluna] == "":
        tabuleiro[linha, coluna] = valor
        return
    raise ValueError("Essa posicao ja esta ocupada.")


def verificar_vitoria(jogador):
    for linha in tabuleiro:
        if np.all(linha == jogador):
            return True

    for coluna in tabuleiro.T:
        if np.all(coluna == jogador):
            return True

    if np.all(np.diag(tabuleiro) == jogador):
        return True
    if np.all(np.diag(np.fliplr(tabuleiro)) == jogador):
        return True

    return False


def verificar_empate(tabuleiro_atual):
    return np.all(tabuleiro_atual != "") and not (
        verificar_vitoria("X") or verificar_vitoria("O")
    )


def obter_valor(indice):
    linha, coluna = indice_para_matriz(indice)
    return tabuleiro[linha, coluna]


def publicar_lampada(lampada, cor):
    payload = {"lampada": int(lampada), **cor}
    client.publish(TOPICO_LAMPADAS, json.dumps(payload))


def publicar_pontuacao(evento, ganhador=None):
    payload = {
        "score_x": int(pontos["X"]),
        "score_o": int(pontos["O"]),
        "best": int(recorde),
        "move": int(jogada),
        "round": int(partida),
        "turn": "X" if turno else "O",
        "winner": ganhador,
        "event": evento,
    }
    client.publish(TOPICO_SCORE, json.dumps(payload))


def apagar_tabuleiro():
    for lampada in range(1, 10):
        publicar_lampada(lampada, CORES["apagado"])


def redesenhar_tabuleiro():
    for lampada in range(1, 10):
        valor = obter_valor(lampada)
        publicar_lampada(lampada, CORES[valor] if valor else CORES["apagado"])


def piscar_lampada(lampada, cor, vezes=2, pausa=0.08):
    cor_original = obter_valor(lampada)
    cor_final = CORES[cor_original] if cor_original else CORES["apagado"]
    for _ in range(vezes):
        publicar_lampada(lampada, cor)
        time.sleep(pausa)
        publicar_lampada(lampada, CORES["apagado"])
        time.sleep(pausa)
    publicar_lampada(lampada, cor_final)


def piscar_todos(cor, vezes=2, pausa=0.08):
    for _ in range(vezes):
        for lampada in range(1, 10):
            publicar_lampada(lampada, cor)
        time.sleep(pausa)
        apagar_tabuleiro()
        time.sleep(pausa)


def obter_linha_vitoria(jogador):
    linhas = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [1, 4, 7],
        [2, 5, 8],
        [3, 6, 9],
        [1, 5, 9],
        [3, 5, 7],
    ]
    for linha in linhas:
        if all(obter_valor(posicao) == jogador for posicao in linha):
            return linha
    return []


def celebrar_vitoria(ganhador):
    linha = obter_linha_vitoria(ganhador)
    for _ in range(4):
        redesenhar_tabuleiro()
        for lampada in linha:
            publicar_lampada(lampada, CORES["ok"])
        time.sleep(0.12)
        for lampada in linha:
            publicar_lampada(lampada, CORES[ganhador])
        time.sleep(0.12)
    piscar_todos(CORES[ganhador], vezes=2)


def game_over(ganhador):
    global tabuleiro, turno, jogada, partida

    publicar_pontuacao("game_over", ganhador)
    if ganhador == "-":
        piscar_todos(CORES["-"], vezes=3)
    else:
        celebrar_vitoria(ganhador)

    apagar_tabuleiro()
    tabuleiro = np.full((3, 3), "")
    turno = True
    jogada = 0
    partida += 1
    publicar_pontuacao("new_round")


def reiniciar_rodada():
    global tabuleiro, turno, jogada, partida

    piscar_todos(CORES["ok"], vezes=1)
    apagar_tabuleiro()
    tabuleiro = np.full((3, 3), "")
    turno = True
    jogada = 0
    partida += 1
    publicar_pontuacao("reset")


def registrar_jogada(lampada, jogador):
    global turno, jogada, recorde

    definir_valor(lampada, jogador)
    pontos[jogador] += 1
    jogada += 1
    recorde = max(recorde, pontos[jogador])
    publicar_lampada(lampada, CORES[jogador])
    piscar_lampada(lampada, CORES["ok"], vezes=1)
    turno = not turno
    publicar_pontuacao("move")

    if verificar_vitoria(jogador):
        pontos[jogador] += 3
        recorde = max(recorde, pontos[jogador])
        publicar_pontuacao("victory", jogador)
        game_over(jogador)
    elif verificar_empate(tabuleiro):
        publicar_pontuacao("draw", "-")
        game_over("-")


def jogada_invalida(lampada):
    if 1 <= lampada <= 9:
        piscar_lampada(lampada, CORES["erro"], vezes=2)
    publicar_pontuacao("invalid")


def on_connect(client, userdata, flags, rc):
    print("Conectado - Codigo de resultado: " + str(rc))
    client.subscribe("JogoDaVelha/Session1/#")
    apagar_tabuleiro()
    publicar_pontuacao("ready")


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload.decode()))
    lista = msg.topic.split("/")
    global clientID_01, clientID_02

    if len(lista) == 3 and lista[2] == "subClient":
        if clientID_01 == "":
            clientID_01 = msg.payload.decode()
            publicar_pontuacao("player_1_ready")
            return
        if clientID_02 == "":
            clientID_02 = msg.payload.decode()
            publicar_pontuacao("player_2_ready")
            return

    if len(lista) != 4:
        return

    try:
        js = json.loads(str(msg.payload.decode()))
    except (json.JSONDecodeError, TypeError, ValueError):
        publicar_pontuacao("invalid_payload")
        return

    if js.get("comando") == "reset":
        if lista[3] == "escolha" and lista[2] in (clientID_01, clientID_02):
            reiniciar_rodada()
        else:
            publicar_pontuacao("invalid_payload")
        return

    try:
        lampada = int(js["lampada"])
        indice_para_matriz(lampada)
    except (KeyError, TypeError, ValueError):
        publicar_pontuacao("invalid_payload")
        return

    if lista[2] == clientID_01:
        if turno is not True:
            jogada_invalida(lampada)
            return
        if lista[3] == "escolha":
            if obter_valor(lampada) == "":
                registrar_jogada(lampada, "X")
            else:
                jogada_invalida(lampada)

    if lista[2] == clientID_02:
        if turno is not False:
            jogada_invalida(lampada)
            return
        if lista[3] == "escolha":
            if obter_valor(lampada) == "":
                registrar_jogada(lampada, "O")
            else:
                jogada_invalida(lampada)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.username_pw_set("csilab", "WhoAmI#2024")
    client.connect("192.168.40.7", 1883, 60)
except:
    print("Nao foi possivel conectar ao MQTT...")
    print("Encerrando...")


try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Encerrando...")
