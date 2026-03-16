# Creation Date: 2026-03-15
# Authors Alvaro Sampaio
# Developed by: CSI-Lab
# Copyright 2026, INATEL.

# ═══════════════════════════════════════════════════════════════════
# RESUMO DAS MUDANÇAS NESTE ARQUIVO
# ═══════════════════════════════════════════════════════════════════
#
# MELHORIA 2 — Arquivo novo (separação de responsabilidades):
#   Antes: toda a lógica MQTT estava em fut_models_main.py,
#          misturada com câmera, UI e lógica de negócio.
#          Funções on_connect e on_message eram funções soltas (globais).
#   Depois: MQTT tem sua própria classe com métodos bem definidos.
#   Por quê: se precisar trocar o broker, mudar autenticação ou adicionar
#            TLS, você mexe só aqui. O resto do sistema não sabe nada
#            sobre como o MQTT funciona por baixo.
#
# BUG 3 CORRIGIDO (complemento) — Credenciais não ficam mais espalhadas:
#   Antes: client.username_pw_set("csilab", "WhoAmI#2024") estava hardcoded
#          diretamente no meio do fut_models_main.py.
#   Depois: as credenciais são passadas como parâmetro ao construtor.
#           O ideal futuro é usar python-dotenv para ler de um .env.
# ═══════════════════════════════════════════════════════════════════

import json
import paho.mqtt.client as mqtt


class SLIMQTTClient:
    """
    MELHORIA 2: encapsula toda a comunicação MQTT do sistema.

    Antes, o código tinha funções globais on_connect e on_message
    e o objeto client era manipulado diretamente em fut_models_main.py.
    Agora tudo fica aqui, isolado e reutilizável.
    """

    def __init__(self, host, port, user, password, keepalive=60):
        """
        Args:
            host:      IP ou hostname do broker MQTT
            port:      porta do broker (padrão MQTT é 1883, com TLS é 8883)
            user:      usuário MQTT
            password:  senha MQTT
            keepalive: intervalo em segundos para manter a conexão viva
        """
        self.host      = host
        self.port      = port
        self.keepalive = keepalive

        # Flag para saber se está conectado antes de tentar publicar.
        # Antes não havia esse controle — publish falhava silenciosamente.
        self.connected = False

        # Cria o cliente MQTT e já configura os callbacks e credenciais.
        # Antes isso estava espalhado em 4-5 linhas no main.
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.username_pw_set(user, password)

    def connect(self):
        """
        Conecta ao broker e inicia o loop MQTT em thread separada.

        MELHORIA 2: antes a conexão era feita com try/except genérico
        que apenas imprimia a exceção e continuava. Agora retorna bool
        para o chamador decidir o que fazer.

        loop_start() roda o MQTT em background — permite que o programa
        principal continue processando frames enquanto o MQTT envia/recebe.

        Returns:
            bool: True se conectou com sucesso
        """
        try:
            self._client.connect(self.host, self.port, self.keepalive)
            # loop_start() cria uma thread separada para o MQTT.
            # Alternativa seria loop_forever() que bloqueia o programa inteiro.
            self._client.loop_start()
            self.connected = True
            print(f"Conectando ao broker MQTT {self.host}:{self.port}...")
            return True
        except Exception as e:
            print(f"Não foi possível conectar ao MQTT: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """
        MELHORIA 2: encerra o loop e desconecta de forma limpa.
        Antes, loop_stop() era chamado diretamente no main, dentro do loop de captura.
        """
        self._client.loop_stop()
        self._client.disconnect()
        self.connected = False
        print("Desconectado do broker MQTT.")

    def publish(self, topic, payload):
        """
        Publica uma mensagem em um tópico MQTT.

        MELHORIA 2: aceita dict ou string como payload.
        Antes, o chamador precisava fazer json.dumps() manualmente toda vez.
        Agora a conversão é automática se payload for dict.

        Args:
            topic:   string do tópico MQTT (ex: "lamp_module/choice")
            payload: string JSON ou dict Python (convertido automaticamente)
        """
        # MELHORIA 3: verifica conexão antes de publicar.
        # Antes, publish() era chamado sem verificação e falhava silenciosamente.
        if not self.connected:
            print("AVISO: tentativa de publicar sem conexão MQTT ativa.")
            return

        # Converte dict para JSON automaticamente.
        # Antes: json.dumps() estava espalhado em vários pontos do main.
        if isinstance(payload, dict):
            payload = json.dumps(payload)

        self._client.publish(topic, payload)
        print(f"[MQTT] Publicado em [{topic}]: {payload}")

    def subscribe(self, topic="#"):
        """
        Inscreve o cliente em um tópico para receber mensagens.

        Args:
            topic: "#" significa todos os tópicos (padrão MQTT wildcard)
        """
        self._client.subscribe(topic)

    def _on_connect(self, client, userdata, flags, rc):
        """
        MELHORIA 2: callback de conexão agora é método privado da classe.
        Antes era função global — qualquer parte do código podia sobrescrevê-la.

        rc=0 significa conexão bem-sucedida.
        Outros valores indicam erro (ex: rc=5 = credenciais inválidas).
        """
        if rc == 0:
            print("Conectado ao broker MQTT com sucesso.")
            # Se inscreve em todos os tópicos para monitorar o sistema
            client.subscribe("#")
        else:
            print(f"Falha na conexão MQTT — código de erro: {rc}")

    def _on_message(self, client, userdata, msg):
        """
        MELHORIA 2: callback de mensagem encapsulado na classe.
        Chamado automaticamente quando chega mensagem em tópico inscrito.
        """
        print(f"[MQTT] {msg.topic}: {msg.payload.decode()}")
