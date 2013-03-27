import random
from copy import deepcopy
import math
import operator

from simulator import Marker


class Policy(object):

    def __init__(self, color):
        super(Policy, self).__init__()
        self.color = color


class RandomPolicy(Policy):
    
    def action(self, board):
        return random.choice(board.legal_actions)


class BadPolicy(Policy):

    def action(self, board):
        return board.legal_actions[0]


class HumanPolicy(Policy):

    def action(self, board):
        print str(board) + "\n"
        resp = None
        while resp is None:
            try:
                resp = int(raw_input())
            except:
                print "err"
                pass
        return resp


class BasicPolicy(Policy):

    def __init__(self, color):
        super(Policy, self).__init__()
        self.color = color
        self.basePi = RandomPolicy(color)

    def action(self, board):
        for action in board.legal_actions:
            row = board.first_unfilled[action]
            for direction in Marker.DIRECTIONS:
                count_me = board.total_line_count(row, action, direction, self.color)
                count_other = board.total_line_count(row, action, direction, 1 - self.color)
                if count_me == 4 or count_other == 4:
                    return action
        return self.basePi.action(board)


class WeightedPolicy(Policy):

    # (all features are 0-1)
    # 4 options for max friendly line length
    # 4 options for max opponent line length
    # 7 options for action location
    FEATURES_COUNT = 4 + 4 + 7

    def __init__(self, color):
        super(WeightedPolicy, self).__init__(color)
        self.weights = [random.uniform(0, 1) for i in range(WeightedPolicy.FEATURES_COUNT)]
        # self.weights = [-5.284195075114471, -5.206252730734786, -3.4723720963180993, 9.815777835675522, -9.431058392028422, -6.286466298710774, -4.24712214500925, 5.820821440516879, -6.832007744620498, -2.5144216984399073, -1.7544759621762513, -1.7231133020853773, -3.710565318497305, -3.0034065478666254, -6.017781211813007]

    def calculate_score(self, board, action):
        row = board.first_unfilled[action]
        
        features = [0.0 for i in xrange(len(self.weights))]
        max_count_me = max(map(lambda direction: board.total_line_count(row, action, direction, self.color) - 1, Marker.DIRECTIONS))
        features[max_count_me] = 1.0
        
        max_count_other = max(map(lambda direction: board.total_line_count(row, action, direction, 1- self.color) - 1, Marker.DIRECTIONS))
        features[max_count_other + 4] = 1.0

        features[action + 8] = 1.0

        score = 0
        for idx in xrange(len(self.weights)):
            score += features[idx] * self.weights[idx]

        return math.exp(score)

    def action(self, board):
        # calculate scores for each action that's avaliable
        scores = {}
        for action in board.legal_actions:
            scores[action] = self.calculate_score(board, action)

        # normalize the scores into a probability distribution
        total = 0
        for action in scores:
            total += scores[action]
        for action in scores:
            scores[action] = scores[action] / total

        # select a weighted sample from the actions -> scores dict
        sorted_scores = list(reversed(sorted(scores.iteritems(), key=operator.itemgetter(1))))
        p = random.uniform(0, 1)
        running_total = 0
        for action, score in sorted_scores:
            running_total += score
            if running_total >= p:
                return action
        return sorted_scores[-1][0]
