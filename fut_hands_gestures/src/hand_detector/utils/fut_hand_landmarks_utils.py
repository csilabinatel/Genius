# Creation Date: 2024-06-07
# Authors Murilo Cruz Lopes, Ludwing Ferney Marenco Camacho
# Developed by: Inatel Competence Center
# Copyright 2024, INATEL.
# All rights are reserved. Reproduction in whole or part is prohibited without the written consent of the copyright owner

class SLIHandLandMarks:


    def __init__(self, handLandmarks):
        self.thumb_x1, self.thumb_y1 = handLandmarks[4][1], handLandmarks[4][2]
        self.index_x1, self.index_y1 = handLandmarks[8][1], handLandmarks[8][2]
        self.middle_x1, self.middle_y1 = handLandmarks[12][1], handLandmarks[12][2]
        self.ring_x1, self.ring_y1 = handLandmarks[16][1], handLandmarks[16][2]
        self.pink_x1, self.pink_y1 = handLandmarks[20][1], handLandmarks[20][2]

        self.index_mcp_x1, self.index_mcp_y1 = handLandmarks[5][1], handLandmarks[5][2]
        self.middle_mcp_x1, self.middle_mcp_y1 = handLandmarks[9][1], handLandmarks[9][2]
        self.ring_mcp_x1, self.ring_mcp_y1 = handLandmarks[13][1], handLandmarks[13][2]
        self.pink_mcp_x1, self.pink_mcp_y1 = handLandmarks[17][1], handLandmarks[17][2]
        self.thumb_mcp_x1, self.thumb_mcp_y1 = handLandmarks[1][1], handLandmarks[1][2]

        self.wirst_x1, self.wirst_y1 = handLandmarks[0][1], handLandmarks[0][2]

        self.ring_pip_x1, self.ring_pip_y1 = handLandmarks[14][1], handLandmarks[14][2]
        self.index_finger_pip_x1, self.index_finger_pip_y1 = handLandmarks[6][1], handLandmarks[6][2]

        self.middle_dip_x1, self.middle_dip_y1 = handLandmarks[11][1], handLandmarks[11][2]
        self.index_finder_dip_x1, self.index_finder_dip_y1 = handLandmarks[7][1], handLandmarks[7][2]