import sys
import random
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
                if resp == -1:
                    sys.exit()
            except:
                print "Invalid input."
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

    # (all features are boolean 0-1)
    # 4 options for max friendly line length
    # 5 options for number of friendly lines
    # 4 options for max opponent line length
    # 5 options for number of opponent lines
    # 7 options for action location
    FEATURES_COUNT = 4 + 5 + 4 + 5 + 7

    def __init__(self, color):
        super(WeightedPolicy, self).__init__(color)
        self.weights = [0.0 for i in xrange(WeightedPolicy.FEATURES_COUNT)]
        # These are some sets of learned weights that you can try if you don't want to go through the learning process.
        # self.weights = [-5.284195075114471, -5.206252730734786, -3.4723720963180993, 9.815777835675522, 0, 0, 0, 0, 0, -9.431058392028422, -6.286466298710774, -4.24712214500925, 5.820821440516879, 0, 0, 0, 0, 0, -6.832007744620498, -2.5144216984399073, -1.7544759621762513, -1.7231133020853773, -3.710565318497305, -3.0034065478666254, -6.017781211813007]
        # self.weights = [-2.50730262701, -1.73460366173, -1.87900162028, 4.27363290065, -0.0549986656126, 1.43578587553, 1.07313216239, -0.87508185094, 0.404725704846, -5.97279824667, -4.30222902037, 2.97796548134, 3.44873225841, -3.89321483256, -2.13815889091, -2.27193058551, -1.41235930388, -2.76515103195, 0.783887192604, 0.33308592891, 4.9213409194, 1.17903335738, 3.939832346, 2.12609854352, -1.40198196604]
        # self.weights = [2.34269737299, 4.41539633827, 2.94599837972, 8.04863290065, 2.52000133439, 1.31078587553, -1.90186783761, -2.40008185094, 4.25472570485, -7.24779824667, -9.85222902037, 4.57796548134, 10.5987322584, -1.19321483256, -1.71315889091, 0.67806941449, 0.23764069612, 1.00984896805, -2.3911128074, 2.88308592891, 9.1213409194, 3.55403335738, 5.714832346, 1.82609854352, -1.12698196604]

    def line_features(self, board, row, col, color):
        max_len = 0
        line_count = 0
        for direction in Marker.DIRECTIONS:
            length = board.total_line_count(row, col, direction, color) - 1
            if length > 0:
                line_count += 1
            if length > max_len:
                max_len = length
        return max_len, line_count

    # Scores are exp(f(s, a) . w) where f(s, a) is the features vector for the given state and action
    # and w is the weights vector. The exp serves to add non-linearity, which speeds up learning.
    # Because exp is increasing, it preserves the ordering of actions, but spreads them out.
    def calculate_score(self, board, action):
        row = board.first_unfilled[action]
        
        features = [0.0 for i in xrange(len(self.weights))]
        max_len_me, line_count_me = self.line_features(board, row, action, self.color)
        features[max_len_me] = 1.0
        features[line_count_me + 4] = 1.0

        max_len_other, line_count_other = self.line_features(board, row, action, 1 - self.color)
        features[max_len_other + 9] = 1.0
        features[line_count_other + 13] = 1.0

        features[action + 18] = 1.0

        score = 0
        for idx in xrange(len(self.weights)):
            score += features[idx] * self.weights[idx]

        return math.exp(score)

    def action(self, board):
        # Calculate scores for each action that's avaliable.
        scores = {}
        for action in board.legal_actions:
            scores[action] = self.calculate_score(board, action)

        # Normalize the scores into a probability distribution.
        total = 0
        for action in scores:
            total += scores[action]
        for action in scores:
            scores[action] = scores[action] / total

        # Select a weighted sample from the actions -> scores dict.
        sorted_scores = list(reversed(sorted(scores.iteritems(), key=operator.itemgetter(1))))
        p = random.uniform(0, 1)
        running_total = 0
        for action, score in sorted_scores:
            running_total += score
            if running_total >= p:
                return action
        return sorted_scores[-1][0]
