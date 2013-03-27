from copy import deepcopy
import random

from simulator import Board, Marker


class Arbiter(object):
    def __init__(self, red, black, board):
        super(Arbiter, self).__init__()
        self.black_policy = black
        self.red_policy = red
        self.board = board

    def run(self):
        red_to_play = True
        while not self.board.terminal:
            if red_to_play:
                action = self.red_policy.action(self.board)
                self.board.play(action, Marker.RED)
            else:
                action = self.black_policy.action(self.board)
                self.board.play(action, Marker.BLACK)
            red_to_play = not red_to_play

        return self.board.winner
