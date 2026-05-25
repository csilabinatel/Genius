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
import os
import sys
import time


# ------------------------------
# UI helpers (kid-friendly HUD)
# ------------------------------

UI_THEME = {
    "bg": (20, 20, 20),
    "panel": (35, 35, 35),
    "white": (245, 245, 245),
    "yellow": (0, 255, 255),
    "green": (0, 220, 120),
    "red": (40, 40, 240),
    "blue": (255, 140, 60),
    "purple": (200, 80, 200),
}


def _clamp_int(v, lo, hi):
    return int(max(lo, min(hi, int(v))))


def _alpha_rect(frame, x1, y1, x2, y2, color, alpha=0.55):
    h, w = frame.shape[:2]
    x1 = _clamp_int(x1, 0, w - 1)
    x2 = _clamp_int(x2, 0, w - 1)
    y1 = _clamp_int(y1, 0, h - 1)
    y2 = _clamp_int(y2, 0, h - 1)
    if x2 <= x1 or y2 <= y1:
        return

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def _rounded_panel(frame, x1, y1, x2, y2, color, alpha=0.55, radius=14, border_color=None, border_thickness=2):
    # Rounded rectangle using rectangles + corner circles.
    h, w = frame.shape[:2]
    x1 = _clamp_int(x1, 0, w - 1)
    x2 = _clamp_int(x2, 0, w - 1)
    y1 = _clamp_int(y1, 0, h - 1)
    y2 = _clamp_int(y2, 0, h - 1)
    if x2 <= x1 or y2 <= y1:
        return

    radius = int(max(0, min(radius, (x2 - x1) // 2, (y2 - y1) // 2)))
    overlay = frame.copy()

    # Fill (rounded)
    cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
    cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
    if radius > 0:
        cv2.circle(overlay, (x1 + radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x1 + radius, y2 - radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y2 - radius), radius, color, -1)

    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Border
    if border_color is not None and border_thickness > 0:
        cv2.rectangle(frame, (x1 + radius, y1), (x2 - radius, y1), border_color, border_thickness)
        cv2.rectangle(frame, (x1 + radius, y2), (x2 - radius, y2), border_color, border_thickness)
        cv2.rectangle(frame, (x1, y1 + radius), (x1, y2 - radius), border_color, border_thickness)
        cv2.rectangle(frame, (x2, y1 + radius), (x2, y2 - radius), border_color, border_thickness)
        if radius > 0:
            cv2.ellipse(frame, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, border_color, border_thickness)
            cv2.ellipse(frame, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, border_color, border_thickness)
            cv2.ellipse(frame, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, border_color, border_thickness)
            cv2.ellipse(frame, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, border_color, border_thickness)


def _put_text(frame, text, org, scale=0.8, color=(255, 255, 255), thickness=2):
    cv2.putText(frame, str(text), org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA, False)


def _text_size(text, scale=0.8, thickness=2):
    (w, h), baseline = cv2.getTextSize(str(text), cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    return w, h, baseline


def _label_chip(frame, text, x, y, chip_color, text_color=(255, 255, 255), scale=0.7):
    pad_x, pad_y = 10, 8
    tw, th, baseline = _text_size(text, scale=scale, thickness=2)
    x1, y1 = x, y
    x2, y2 = x + tw + 2 * pad_x, y + th + 2 * pad_y
    _rounded_panel(frame, x1, y1, x2, y2, chip_color, alpha=0.75, radius=12, border_color=None)
    _put_text(frame, text, (x + pad_x, y + pad_y + th), scale=scale, color=text_color, thickness=2)
    return x2


def _progress_ring(frame, center, radius, progress, color, thickness=10, bg_color=(70, 70, 70)):
    progress = max(0.0, min(1.0, float(progress)))
    cv2.circle(frame, center, radius, bg_color, thickness)
    end_angle = int(360 * progress)
    if end_angle > 0:
        cv2.ellipse(frame, center, (radius, radius), -90, 0, end_angle, color, thickness)

# Topics and PlayerID
playerID = "jogador2"
topic_genius = "lamp_module/choice"
topic_velha = f"JogoDaVelha/Session1/{playerID}/escolha"
topic_dimmer = "rgb_module/dimmer/setLampState"
MQTT_HOST = os.environ.get("MQTT_HOST", "192.168.66.11")

GENIUS_CONFIRM_HOLD_S = 1.0  # era 1.5s; diminua/aumente aqui
GENIUS_CONFIRMED_TOAST_S = 0.7
VELHA_CONFIRM_HOLD_S = 0.75
VELHA_CONFIRMED_TOAST_S = 0.7
VELHA_RESET_HOLD_S = 1.2


def draw_genius_confirm_ui(frame, system_status):
    now = time.monotonic()

    score = system_status.get("genius_score")
    best = system_status.get("genius_best")
    # Fonte preferencial: genius.py publica score (acertos) em lamp_module/score.
    # A fase exibida é o próprio score (começa em 0 e incrementa a cada acerto).
    phase = system_status.get("genius_phase")

    target = system_status.get("genius_target_number")
    progress = float(system_status.get("genius_progress", 0.0) or 0.0)
    latched = bool(system_status.get("genius_latched", False))
    last_ok = system_status.get("genius_last_confirmed_at")

    # Painel do Genius no topo (evita sobreposição com outros textos)
    h, w = frame.shape[:2]
    panel_h = int(max(86, h * 0.14))
    _alpha_rect(frame, 0, 0, w, panel_h, UI_THEME["bg"], alpha=0.25)
    _rounded_panel(frame, 12, 10, w - 12, panel_h - 10, UI_THEME["panel"], alpha=0.65, radius=18, border_color=UI_THEME["yellow"], border_thickness=2)

    def _draw_score_chips(frame, w, h, score, best, phase):
        phase_int = int(phase) if phase is not None else 0
        phase_text = f"Numeros corretos {max(0, phase_int)}"
        tw, _, _ = _text_size(phase_text, scale=1.1, thickness=3)
        bx = w // 2 - tw // 2 - 14
        by = h - 70
        _label_chip(frame, phase_text, bx, by, UI_THEME["green"], text_color=(20, 20, 20), scale=1.1)
        if score is not None:
            sx = max(24, w - 320)
            _label_chip(frame, f"PONTOS {int(score)}", sx, 18, UI_THEME["yellow"], text_color=(20, 20, 20), scale=0.68)
            if best is not None:
                _label_chip(frame, f"REC {int(best)}", sx, 54, UI_THEME["blue"], scale=0.62)

    # Toast rápido após confirmar
    if latched and last_ok is not None and (now - float(last_ok)) <= GENIUS_CONFIRMED_TOAST_S:
        chip_x = 24
        chip_x = _label_chip(frame, "GENIUS", chip_x, 20, UI_THEME["purple"], scale=0.75)
        _label_chip(frame, f"MUITO BEM! {target}", chip_x + 10, 20, UI_THEME["green"], scale=0.75)
        _draw_score_chips(frame, w, h, score, best, phase)
        return

    if target is None:
        chip_x = 24
        chip_x = _label_chip(frame, "GENIUS", chip_x, 20, UI_THEME["purple"], scale=0.75)
        _label_chip(frame, "Faca o MESMO numero nas 2 maos", chip_x + 10, 20, UI_THEME["blue"], scale=0.75)
        _draw_score_chips(frame, w, h, score, best, phase)
        return

    # Indicador com anel de progresso (mais divertido que barra)
    progress = max(0.0, min(1.0, progress))
    ring_center = (w - 70, panel_h // 2)
    _progress_ring(frame, ring_center, radius=26, progress=progress, color=UI_THEME["green"], thickness=9)
    _put_text(frame, "OK", (ring_center[0] - 14, ring_center[1] + 10), scale=0.7, color=UI_THEME["white"], thickness=2)

    remaining = max(0.0, GENIUS_CONFIRM_HOLD_S * (1.0 - progress))
    chip_x = 24
    chip_x = _label_chip(frame, "GENIUS", chip_x, 20, UI_THEME["purple"], scale=0.75)
    _label_chip(frame, f"Segure o {target}  ({remaining:.1f}s)", chip_x + 10, 20, UI_THEME["green"], scale=0.75)
    _draw_score_chips(frame, w, h, score, best, phase)


def _put_centered_text(frame, text, center, scale=0.8, color=(255, 255, 255), thickness=2):
    tw, th, _ = _text_size(text, scale=scale, thickness=thickness)
    org = (int(center[0] - tw / 2), int(center[1] + th / 2))
    _put_text(frame, text, org, scale=scale, color=color, thickness=thickness)


def _draw_velha_board(frame, board, selected, x, y, size):
    if not isinstance(board, list) or len(board) != 9:
        board = [""] * 9

    _rounded_panel(frame, x - 6, y - 6, x + size + 6, y + size + 6, UI_THEME["panel"], alpha=0.72, radius=12, border_color=UI_THEME["white"], border_thickness=1)
    cell = size // 3

    if selected is not None and 1 <= selected <= 9:
        idx = int(selected) - 1
        sx = x + (idx % 3) * cell
        sy = y + (idx // 3) * cell
        cv2.rectangle(frame, (sx + 3, sy + 3), (sx + cell - 3, sy + cell - 3), UI_THEME["yellow"], 2)

    for i in range(1, 3):
        cv2.line(frame, (x + i * cell, y), (x + i * cell, y + size), UI_THEME["white"], 2)
        cv2.line(frame, (x, y + i * cell), (x + size, y + i * cell), UI_THEME["white"], 2)

    for idx, value in enumerate(board):
        cx = x + (idx % 3) * cell + cell // 2
        cy = y + (idx // 3) * cell + cell // 2
        if value == "X":
            _put_centered_text(frame, "X", (cx, cy), scale=0.8, color=UI_THEME["red"], thickness=3)
        elif value == "O":
            _put_centered_text(frame, "O", (cx, cy), scale=0.8, color=UI_THEME["blue"], thickness=3)
        else:
            _put_centered_text(frame, str(idx + 1), (cx, cy), scale=0.48, color=(180, 180, 180), thickness=1)


def draw_velha_ui(frame, system_status):
    now = time.monotonic()
    h, w = frame.shape[:2]
    panel_h = int(max(108, h * 0.17))
    _alpha_rect(frame, 0, 0, w, panel_h, UI_THEME["bg"], alpha=0.25)
    _rounded_panel(frame, 12, 10, w - 12, panel_h - 10, UI_THEME["panel"], alpha=0.65, radius=18, border_color=UI_THEME["green"], border_thickness=2)

    board = system_status.get("velha_board", [""] * 9)
    turn = system_status.get("velha_turn", "X")
    score_x = int(system_status.get("velha_score_x", 0) or 0)
    score_o = int(system_status.get("velha_score_o", 0) or 0)
    round_number = int(system_status.get("velha_round", 1) or 1)
    target = system_status.get("velha_target_number")
    progress = float(system_status.get("velha_progress", 0.0) or 0.0)
    reset_progress = float(system_status.get("velha_reset_progress", 0.0) or 0.0)
    last_ok = system_status.get("velha_last_confirmed_at")
    last_reset = system_status.get("velha_last_reset_at")

    board_size = int(min(96, panel_h - 28, max(72, w * 0.16)))
    board_x = w - board_size - 28
    board_y = 20
    _draw_velha_board(frame, board, target, board_x, board_y, board_size)

    chip_x = 24
    chip_x = _label_chip(frame, "VELHA", chip_x, 20, UI_THEME["purple"], scale=0.75)

    result_text = system_status.get("velha_result_text")
    result_at = system_status.get("velha_result_at")
    event = system_status.get("velha_event")
    event_at = system_status.get("velha_event_at")
    fresh_result = result_text and result_at is not None and (now - float(result_at)) <= 2.5
    fresh_event = event_at is not None and (now - float(event_at)) <= 1.4

    if reset_progress > 0:
        status_text = f"Resetando ({max(0.0, VELHA_RESET_HOLD_S * (1.0 - reset_progress)):.1f}s)"
        status_color = UI_THEME["red"]
        text_color = UI_THEME["white"]
    elif last_reset is not None and (now - float(last_reset)) <= 1.5:
        status_text = "Jogo resetado"
        status_color = UI_THEME["green"]
        text_color = (20, 20, 20)
    elif fresh_result:
        status_text = result_text
        status_color = UI_THEME["yellow"]
        text_color = (20, 20, 20)
    elif fresh_event and event == "occupied":
        status_text = "Casa ocupada"
        status_color = UI_THEME["red"]
        text_color = UI_THEME["white"]
    elif fresh_event and event == "wrong_turn":
        status_text = "Aguarde a vez"
        status_color = UI_THEME["red"]
        text_color = UI_THEME["white"]
    elif target is not None and last_ok is not None and (now - float(last_ok)) <= VELHA_CONFIRMED_TOAST_S:
        status_text = f"Jogada enviada {target}"
        status_color = UI_THEME["green"]
        text_color = (20, 20, 20)
    elif target is None:
        status_text = f"Vez {turn}: escolha 1-9"
        status_color = UI_THEME["blue"] if turn == "O" else UI_THEME["red"]
        text_color = UI_THEME["white"]
    elif progress > 0:
        remaining = max(0.0, VELHA_CONFIRM_HOLD_S * (1.0 - progress))
        status_text = f"Segure palma: casa {target} ({remaining:.1f}s)"
        status_color = UI_THEME["green"]
        text_color = (20, 20, 20)
    else:
        status_text = f"Casa {target}: abra a palma"
        status_color = UI_THEME["yellow"]
        text_color = (20, 20, 20)

    chip_x = _label_chip(frame, status_text, chip_x + 10, 20, status_color, text_color=text_color, scale=0.72)
    score_y = 62
    score_x_pos = 24
    score_x_pos = _label_chip(frame, f"X {score_x}", score_x_pos, score_y, UI_THEME["red"], scale=0.65)
    score_x_pos = _label_chip(frame, f"O {score_o}", score_x_pos + 8, score_y, UI_THEME["blue"], scale=0.65)
    _label_chip(frame, f"Rodada {round_number}", score_x_pos + 8, score_y, UI_THEME["green"], text_color=(20, 20, 20), scale=0.65)

    ring_center = (max(42, board_x - 42), panel_h // 2)
    if reset_progress > 0:
        _progress_ring(frame, ring_center, radius=23, progress=reset_progress, color=UI_THEME["red"], thickness=8)
        _put_text(frame, "RST", (ring_center[0] - 19, ring_center[1] + 8), scale=0.52, color=UI_THEME["white"], thickness=2)
    elif target is not None:
        _progress_ring(frame, ring_center, radius=23, progress=progress, color=UI_THEME["green"], thickness=8)
        _put_text(frame, "OK", (ring_center[0] - 13, ring_center[1] + 8), scale=0.62, color=UI_THEME["white"], thickness=2)

# Draw the detection on the screen
def draw_detections(frame, message):
    if len(message) == 0:
        return

    h, w = frame.shape[:2]

    # Reservar espaço no topo para o Genius (se estiver ativo) e evitar “fase em cima de fase”.
    top_margin = int(max(8, h * 0.15))

    hand = message.get("hand")
    if hand == "Left":
        # Cartão da mão esquerda (escolha de número)
        x1, y1 = 14, top_margin + 10
        x2, y2 = int(w * 0.36), top_margin + 110
        _rounded_panel(frame, x1, y1, x2, y2, UI_THEME["panel"], alpha=0.62, radius=18, border_color=UI_THEME["blue"], border_thickness=2)
        _label_chip(frame, "MÃO ESQ.", x1 + 10, y1 + 10, UI_THEME["blue"], scale=0.65)

        if message.get("click_status"):
            _label_chip(frame, "CLIQUE!", x1 + 10, y1 + 52, UI_THEME["yellow"], text_color=(20, 20, 20), scale=0.85)
        else:
            number = message.get("number")
            if number is None:
                _put_text(frame, "Mostre um número", (x1 + 12, y1 + 90), scale=0.75, color=UI_THEME["white"], thickness=2)
            else:
                # Número grande (mais “infantil”)
                _put_text(frame, "NÚMERO", (x1 + 12, y1 + 78), scale=0.65, color=UI_THEME["white"], thickness=2)
                _put_text(frame, str(number), (x1 + 140, y1 + 95), scale=1.8, color=UI_THEME["green"], thickness=4)

    if hand == "Right":
        # Cartão da mão direita (ações)
        x2, y1 = w - 14, top_margin + 10
        x1, y2 = int(w * 0.64), top_margin + 110
        _rounded_panel(frame, x1, y1, x2, y2, UI_THEME["panel"], alpha=0.62, radius=18, border_color=UI_THEME["purple"], border_thickness=2)
        _label_chip(frame, "MÃO DIR.", x1 + 10, y1 + 10, UI_THEME["purple"], scale=0.65)

        chip_x = x1 + 10
        chip_y = y1 + 52

        # Mostra só 1 ação principal para não poluir.
        if message.get("open_palm"):
            _label_chip(frame, "", chip_x, chip_y, UI_THEME["green"], scale=0.85)
        elif message.get("close_fist"):
            _label_chip(frame, "", chip_x, chip_y, UI_THEME["red"], scale=0.85)
        elif message.get("env_var"):
            _label_chip(frame, "", chip_x, chip_y, UI_THEME["yellow"], text_color=(20, 20, 20), scale=0.85)
        elif message.get("graphs"):
            _label_chip(frame, "", chip_x, chip_y, UI_THEME["yellow"], text_color=(20, 20, 20), scale=0.85)
        elif message.get("remove_all"):
            _label_chip(frame, "", chip_x, chip_y, UI_THEME["red"], scale=0.85)
        elif message.get("dimmer_value") is not None:
            _label_chip(frame, f"DIMMER {message.get('dimmer_value')}", chip_x, chip_y, UI_THEME["blue"], scale=0.78)
        else:
            _put_text(frame, "Faça um gesto", (x1 + 12, y1 + 90), scale=0.75, color=UI_THEME["white"], thickness=2)


# Organize the information about the hand and send it to the mqqt server
def control_objects(topic, right_hand_message, left_hand_message, system_status, client = None):
    # Genius: confirmação por tempo usando o mesmo número nas duas mãos.
    # Confirma quando (left_number == right_number) em [1..6] por GENIUS_CONFIRM_HOLD_S.
    if topic == topic_genius:
        now = time.monotonic()

        # Contador local de fase (fallback) caso o genius.py não publique lamp_module/score.
        system_status.setdefault("genius_phase", 0)
        system_status["_genius_last_choice_at"] = system_status.get("_genius_last_choice_at")

        left_number = None
        if len(left_hand_message) != 0:
            left_number = left_hand_message.get("number", None)

        right_number = None
        if len(right_hand_message) != 0:
            right_number = right_hand_message.get("number", None)

        system_status.setdefault("genius_last_number", None)
        system_status.setdefault("genius_hold_started_at", None)
        system_status.setdefault("genius_latched", False)
        system_status.setdefault("genius_progress", 0.0)
        system_status.setdefault("genius_target_number", None)
        system_status.setdefault("genius_last_confirmed_at", None)
        system_status.setdefault("genius_round", 0)

        valid_choice = (left_number is not None) and (right_number is not None)
        if valid_choice:
            try:
                left_number_int = int(left_number)
                right_number_int = int(right_number)
            except Exception:
                valid_choice = False
            else:
                valid_choice = (
                    1 <= left_number_int <= 6
                    and 1 <= right_number_int <= 6
                    and left_number_int == right_number_int
                )

        if valid_choice:
            if system_status["genius_last_number"] != left_number_int:
                system_status["genius_last_number"] = left_number_int
                system_status["genius_hold_started_at"] = now
                system_status["genius_latched"] = False

            system_status["genius_target_number"] = left_number_int

            if system_status["genius_hold_started_at"] is None:
                system_status["genius_hold_started_at"] = now

            elapsed = now - system_status["genius_hold_started_at"]
            system_status["genius_progress"] = min(1.0, max(0.0, elapsed / GENIUS_CONFIRM_HOLD_S))
            if elapsed >= GENIUS_CONFIRM_HOLD_S and not system_status["genius_latched"]:
                msg = {"left_hand": left_number_int, "right_hand_message": 1, "dimmer": None}
                print(msg)
                client.publish(topic, json.dumps(msg))
                system_status["_genius_last_choice_at"] = now

                # Fallback: assume acerto até o jogo sinalizar erro.
                # (Se o player errar, o padrão do errou() reseta a fase em on_message.)
                system_status["genius_phase"] = int(system_status.get("genius_phase", 0)) + 1

                system_status["genius_latched"] = True
                system_status["genius_last_confirmed_at"] = now
        else:
            # Soltou / mudou número → libera para confirmar de novo
            system_status["genius_last_number"] = None
            system_status["genius_hold_started_at"] = None
            system_status["genius_latched"] = False
            system_status["genius_progress"] = 0.0
            system_status["genius_target_number"] = None

        return

    if topic == topic_velha:
        now = time.monotonic()

        left_number = None
        if len(left_hand_message) != 0:
            left_number = left_hand_message.get("number", None)

        right_open = False
        right_close = False
        if len(right_hand_message) != 0:
            right_open = bool(right_hand_message.get("open_palm", False))
            right_close = bool(right_hand_message.get("close_fist", False))

        system_status.setdefault("velha_last_number", None)
        system_status.setdefault("velha_hold_started_at", None)
        system_status.setdefault("velha_latched", False)
        system_status.setdefault("velha_progress", 0.0)
        system_status.setdefault("velha_target_number", None)
        system_status.setdefault("velha_last_confirmed_at", None)
        system_status.setdefault("velha_reset_started_at", None)
        system_status.setdefault("velha_reset_latched", False)
        system_status.setdefault("velha_reset_progress", 0.0)
        system_status.setdefault("velha_last_reset_at", None)

        if right_close:
            system_status["velha_last_number"] = None
            system_status["velha_hold_started_at"] = None
            system_status["velha_latched"] = False
            system_status["velha_progress"] = 0.0
            system_status["velha_target_number"] = None

            if system_status["velha_reset_started_at"] is None:
                system_status["velha_reset_started_at"] = now

            elapsed = now - system_status["velha_reset_started_at"]
            system_status["velha_reset_progress"] = min(1.0, max(0.0, elapsed / VELHA_RESET_HOLD_S))
            if elapsed >= VELHA_RESET_HOLD_S and not system_status["velha_reset_latched"]:
                reset_topic = topic.rsplit("/", 1)[0] + "/reset"
                msg = {"reset": True}
                print(msg)
                client.publish(reset_topic, json.dumps(msg))
                system_status["velha_reset_latched"] = True
                system_status["velha_last_reset_at"] = now
            return

        system_status["velha_reset_started_at"] = None
        system_status["velha_reset_latched"] = False
        system_status["velha_reset_progress"] = 0.0

        valid_number = False
        try:
            left_number_int = int(left_number)
            valid_number = 1 <= left_number_int <= 9
        except Exception:
            left_number_int = None

        if not valid_number:
            system_status["velha_last_number"] = None
            system_status["velha_hold_started_at"] = None
            system_status["velha_latched"] = False
            system_status["velha_progress"] = 0.0
            system_status["velha_target_number"] = None
            return

        system_status["velha_target_number"] = left_number_int

        if not right_open:
            system_status["velha_last_number"] = left_number_int
            system_status["velha_hold_started_at"] = None
            system_status["velha_latched"] = False
            system_status["velha_progress"] = 0.0
            return

        if system_status["velha_last_number"] != left_number_int:
            system_status["velha_last_number"] = left_number_int
            system_status["velha_hold_started_at"] = now
            system_status["velha_latched"] = False

        if system_status["velha_hold_started_at"] is None:
            system_status["velha_hold_started_at"] = now

        elapsed = now - system_status["velha_hold_started_at"]
        system_status["velha_progress"] = min(1.0, max(0.0, elapsed / VELHA_CONFIRM_HOLD_S))
        if elapsed >= VELHA_CONFIRM_HOLD_S and not system_status["velha_latched"]:
            msg = {"lampada": left_number_int}
            print(msg)
            client.publish(topic, json.dumps(msg))
            system_status["velha_latched"] = True
            system_status["velha_last_confirmed_at"] = now

        return

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
    payload = msg.payload.decode()
    print(msg.topic+" "+str(payload))

    if userdata is None:
        return

    if msg.topic == "JogoDaVelha/Session1/score":
        try:
            data = json.loads(payload)
        except Exception:
            return

        now = time.monotonic()
        try:
            userdata["velha_score_x"] = int(data.get("score_x", userdata.get("velha_score_x", 0)))
            userdata["velha_score_o"] = int(data.get("score_o", userdata.get("velha_score_o", 0)))
            userdata["velha_round"] = int(data.get("round", userdata.get("velha_round", 1)))
            userdata["velha_move"] = int(data.get("move", userdata.get("velha_move", 0)))
            userdata["velha_turn"] = data.get("turn", userdata.get("velha_turn", "X"))
            userdata["velha_winner"] = data.get("winner")
            userdata["velha_event"] = data.get("event")
            userdata["velha_event_at"] = now
            board = data.get("board")
            if isinstance(board, list) and len(board) == 9:
                userdata["velha_board"] = board

            event = data.get("event")
            winner = data.get("winner")
            if event == "victory" and winner in ("X", "O"):
                userdata["velha_result_text"] = f"{winner} venceu!"
                userdata["velha_result_at"] = now
            elif event == "draw" or winner == "-":
                userdata["velha_result_text"] = "Empate!"
                userdata["velha_result_at"] = now
            elif event == "reset":
                userdata["velha_result_text"] = "Jogo resetado"
                userdata["velha_result_at"] = now
                userdata["velha_last_reset_at"] = now
        except Exception:
            return
        return

    # ------------------------------
    # Fallback de fase via setState
    # ------------------------------
    # Se detectar padrão de ERRO (todas as 6 lâmpadas ligam), reseta fase para 0.
    if msg.topic == "lamp_module/setState":
        try:
            data = json.loads(payload)
            lamp = int(data.get("lampada", 0))
            state = int(data.get("estado", -1))
            now = time.monotonic()

            # Inicialização
            userdata.setdefault("genius_phase", 0)
            userdata.setdefault("_genius_err_on", set())
            userdata.setdefault("_genius_err_on_ts", None)
            userdata.setdefault("_genius_err_recent", False)
            # Não contamos fase por "início de sequência" aqui porque o usuário quer
            # incrementar a cada acerto de botão.

            # Detecta ERRO: 6 lâmpadas ON dentro de uma janela curta.
            if state == 1 and 1 <= lamp <= 6:
                if userdata["_genius_err_on_ts"] is None or (now - float(userdata["_genius_err_on_ts"])) > 0.9:
                    userdata["_genius_err_on_ts"] = now
                    userdata["_genius_err_on"] = set()
                userdata["_genius_err_on"].add(lamp)
                if len(userdata["_genius_err_on"]) >= 6:
                    userdata["genius_phase"] = 0
                    userdata["genius_score"] = 0
                    userdata["_genius_err_recent"] = True
                    userdata["_genius_err_on"] = set()

        except Exception:
            pass

    # Atualiza fase e placar via MQTT do genius.py (quando disponível).
    if msg.topic == "lamp_module/score":
        try:
            data = json.loads(payload)
        except Exception:
            return
        try:
            if "score" in data:
                userdata["genius_score"] = int(data["score"])
                userdata["genius_phase"] = int(data["score"])
            if "best" in data:
                userdata["genius_best"] = int(data["best"])
        except Exception:
            return

if __name__ == '__main__':

    # Realiza a conexão assim que o código inicia
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    print ("Connecting to the Server...")
    try:
        client.username_pw_set("csilab", "WhoAmI#2024")
        print(f"MQTT host: {MQTT_HOST}")
        client.connect(MQTT_HOST, 1883, 60) #Mude o hostname para o IP do servidor
    except Exception as exception:
        print("Não foi possivel conectar ao MQTT...", exception)
        print("Encerrando...")
        sys.exit(1)

    # Necessário para receber mensagens (ex.: lamp_module/score)
    system_status = {"lamp_status": None, "lamp_number": None, "dimmer_value": None}
    client.user_data_set(system_status)
    client.loop_start()

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

        # ROI boxes mais bonitos e discretos
        roi_alpha = 0.12
        _alpha_rect(frame, left_box_x1, left_box_y1, left_box_x2, left_box_y2, UI_THEME["blue"], alpha=roi_alpha)
        _alpha_rect(frame, right_box_x1, right_box_y1, right_box_x2, right_box_y2, UI_THEME["purple"], alpha=roi_alpha)
        cv2.rectangle(frame, (left_box_x1, left_box_y1), (left_box_x2, left_box_y2), UI_THEME["blue"], 2)
        cv2.rectangle(frame, (right_box_x1, right_box_y1), (right_box_x2, right_box_y2), UI_THEME["purple"], 2)

        # Chips de label (evita texto solto sobrepondo)
        _label_chip(frame, "MÃO ESQ.", left_box_x1 + 10, max(10, left_box_y1 - 44), UI_THEME["blue"], scale=0.65)
        _label_chip(frame, "MÃO DIR.", right_box_x1 + 10, max(10, right_box_y1 - 44), UI_THEME["purple"], scale=0.65)

        draw_detections(frame, left_hand_message)
        draw_detections(frame, right_hand_message)
        if topic == topic_genius:
            draw_genius_confirm_ui(frame, system_status)
        elif topic == topic_velha:
            draw_velha_ui(frame, system_status)

        cv2.imshow("Hands Landmarks", frame)
        if cv2.waitKey(1) == ord('q'):
            running=False
            client.loop_stop()

    try:
        client.disconnect()
    except Exception:
        pass

    cap.release()
    cv2.destroyAllWindows()
