# Creation Date: 2026-03-15
# Authors Alvaro Sampaio
# Developed by: CSI-Lab
# Copyright 2026, INATEL.

# ═══════════════════════════════════════════════════════════════════
# RESUMO DAS MUDANÇAS NESTE ARQUIVO
# ═══════════════════════════════════════════════════════════════════
#
# MELHORIA 2 — Arquivo novo (separação de responsabilidades):
#   Antes: toda a lógica de câmera estava em fut_models_main.py,
#          misturada com MQTT, UI e lógica de negócio.
#   Depois: câmera tem seu próprio arquivo e sua própria classe.
#   Por quê: se a câmera quebrar, você sabe exatamente onde olhar.
#            Também facilita trocar a câmera (ex: usar IP cam) sem
#            mexer no resto do sistema.
#
# MELHORIA 3 — Reconexão automática da câmera:
#   Antes: se a câmera desconectasse, o programa travava silenciosamente
#          (cap.read() retornava ret=False e o loop continuava com frame None).
#   Depois: tentativas de reconexão automática com limite configurável.
#           Se não reconectar, retorna None e o main encerra de forma limpa.
# ═══════════════════════════════════════════════════════════════════

import cv2


class SLICameraCapture:
    """
    MELHORIA 2: classe nova que encapsula toda a lógica de câmera.

    Responsabilidades:
    - Abrir e fechar a câmera
    - Capturar e espelhar frames
    - Calcular as ROIs proporcionalmente à resolução
    - Reconectar automaticamente se a câmera cair (MELHORIA 3)
    """

    def __init__(self, camera_index=0, max_reconnect_attempts=5):
        """
        Args:
            camera_index:           índice da câmera (0 = câmera padrão do sistema).
                                    Use 1, 2... para câmeras externas.
            max_reconnect_attempts: MELHORIA 3 — quantas vezes tenta reconectar
                                    antes de desistir e encerrar.
        """
        self.camera_index           = camera_index
        self.max_reconnect_attempts = max_reconnect_attempts
        self._cap                   = None   # objeto VideoCapture do OpenCV
        self.width                  = 0
        self.height                 = 0

        # MELHORIA 2: ROIs ficam como atributos da classe.
        # Antes eram variáveis soltas em fut_models_main.py,
        # dificultando reutilização e testes.
        self.left_roi  = None  # tupla (x1, y1, x2, y2) em pixels
        self.right_roi = None  # tupla (x1, y1, x2, y2) em pixels

    def open(self):
        """
        Abre a câmera, lê a resolução e calcula as ROIs.

        MELHORIA 3: antes não havia verificação de isOpened().
        Se a câmera não existisse, o programa avançava e dava erro
        obscuro mais adiante.

        Returns:
            bool: True se a câmera abriu com sucesso, False caso contrário.
        """
        self._cap = cv2.VideoCapture(self.camera_index)

        # MELHORIA 3: verifica se a câmera foi aberta de fato.
        # Antes, o código assumia que sempre abriria.
        if not self._cap.isOpened():
            print(f"Erro: não foi possível abrir a câmera {self.camera_index}.")
            return False

        # Lê a resolução real da câmera para calcular ROIs proporcionais.
        # Isso garante que o sistema funcione em qualquer resolução (720p, 1080p, etc.)
        self.width  = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self._calculate_rois()

        print(f"Câmera aberta: {int(self.width)}x{int(self.height)}")
        return True

    def read_frame(self):
        """
        Captura um frame da câmera e espelha horizontalmente.

        MELHORIA 3: se cap.read() falhar (câmera desconectada),
        tenta reabrir a câmera até max_reconnect_attempts vezes.
        Antes o código não tratava essa situação — o sistema simplesmente
        parava de funcionar sem mensagem de erro clara.

        Returns:
            numpy.ndarray: frame BGR espelhado, pronto para processar.
            None: se não conseguiu reconectar após todas as tentativas.
        """
        for attempt in range(self.max_reconnect_attempts):
            ret, frame = self._cap.read()

            if ret:
                # cv2.flip(frame, 1) espelha no eixo vertical (esquerda/direita).
                # Necessário para que o usuário veja sua mão como num espelho —
                # move a mão direita, o espelho move para a direita.
                return cv2.flip(frame, 1)

            # ret=False significa que a câmera não entregou frame válido.
            # MELHORIA 3: em vez de silenciar o erro, tenta reconectar.
            print(f"Câmera perdida. Tentando reconectar ({attempt + 1}/{self.max_reconnect_attempts})...")
            self._cap.release()
            self._cap = cv2.VideoCapture(self.camera_index)

        # Esgotou todas as tentativas — avisa e deixa o main decidir o que fazer.
        print("Erro: não foi possível reconectar à câmera.")
        return None

    def get_roi(self, frame, side):
        """
        MELHORIA 2: recorta a ROI do frame para o lado pedido.

        Antes, o recorte era feito manualmente em fut_models_main.py
        com indexação direta: frame[y1:y2, x1:x2].
        Agora está encapsulado aqui — o main não precisa saber das coordenadas.

        Args:
            frame: frame BGR completo capturado pela câmera
            side:  'Left' ou 'Right'

        Returns:
            numpy.ndarray: sub-imagem recortada correspondente à ROI
        """
        if side == "Left":
            x1, y1, x2, y2 = self.left_roi
        elif side == "Right":
            x1, y1, x2, y2 = self.right_roi
        else:
            raise ValueError(f"Side deve ser 'Left' ou 'Right', recebeu: '{side}'")

        # Indexação numpy: [linhas, colunas] → [y1:y2, x1:x2]
        return frame[y1:y2, x1:x2]

    def draw_rois(self, frame):
        """
        MELHORIA 2: desenha as ROIs e instruções no frame.

        Antes estava em fut_models_main.py com coordenadas hardcoded.
        Agora usa os atributos calculados em _calculate_rois().

        Args:
            frame: frame BGR onde os elementos visuais serão desenhados
        """
        x1l, y1l, x2l, y2l = self.left_roi
        x1r, y1r, x2r, y2r = self.right_roi

        # Retângulos azuis delimitando as áreas de cada mão
        cv2.rectangle(frame, (x1l, y1l), (x2l, y2l), (255, 0, 0), 2)
        cv2.rectangle(frame, (x1r, y1r), (x2r, y2r), (255, 0, 0), 2)

        # Labels de instrução para o usuário
        cv2.putText(frame, "LEFT HAND HERE",  (x1l + 10, y1l * 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "RIGHT HAND HERE", (x1r - 5,  y1r * 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

    def release(self):
        """
        MELHORIA 3: libera o recurso da câmera de forma explícita.
        Antes, cap.release() era chamado no final do main sem verificação.
        Agora está encapsulado aqui para garantir limpeza correta.
        """
        if self._cap:
            self._cap.release()
            print("Câmera liberada.")

    def _calculate_rois(self):
        """
        MELHORIA 2: centraliza o cálculo das ROIs em um único lugar.

        Antes, as coordenadas eram calculadas em fut_models_main.py com
        comentários indicando os valores absolutos para 640x480:
            left_box_x2 = int(0.4375 * width)  # 280

        Agora estão organizadas aqui e são recalculadas automaticamente
        para qualquer resolução que a câmera retornar.

        Layout:
            [  LEFT ROI  ][  GAP  ][  RIGHT ROI  ]
            0%         43.75%  56.25%           100%  (largura)
            5.4%                              73.95%  (altura)
        """
        w, h = self.width, self.height

        self.left_roi = (
            int(0.0000 * w),  # x1: borda esquerda da tela
            int(0.0540 * h),  # y1: ~5% do topo (deixa espaço pro texto de debug)
            int(0.4375 * w),  # x2: ~44% da largura
            int(0.7395 * h),  # y2: ~74% da altura
        )
        self.right_roi = (
            int(0.5625 * w),  # x1: ~56% da largura (começa depois do gap central)
            int(0.0540 * h),  # y1: mesmo topo da ROI esquerda
            int(1.0000 * w),  # x2: borda direita da tela
            int(0.7395 * h),  # y2: mesma base da ROI esquerda
        )
