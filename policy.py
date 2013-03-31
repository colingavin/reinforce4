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

    def __init__(self, color, track_grads=False):
        super(WeightedPolicy, self).__init__(color)
        self.weights = [0.0 for i in xrange(WeightedPolicy.FEATURES_COUNT)]
        self.track_grads = track_grads
        self.grads = []
        # These are some sets of learned weights that you can try if you don't want to go through the learning process.
        # self.weights = [-2.20597254474, -1.78571440414, -0.845539983565, 4.10251716516, -2.51825361545, -2.16505039348, -0.208659399836, 5.3094751307, -1.35595706971, -0.370561310822, 1.48504421281, 1.67516404883, 1.02282711843, -0.679025543009, -1.54835951836]

    def clear_gradients(self):
        self.grads = []

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

        return features, math.exp(score)

    def action(self, board):
        # Calculate scores for each action that's avaliable.
        scores = {}
        features = {}
        for action in board.legal_actions:
            features[action], scores[action] = self.calculate_score(board, action)

        # Normalize the scores into a probability distribution.
        total = 0
        for action in scores:
            total += scores[action]
        probits = {}
        for action in scores:
            probits[action] = scores[action] / total

        # Select a weighted sample from the actions -> probits dict.
        sorted_probits = list(reversed(sorted(probits.iteritems(), key=operator.itemgetter(1))))
        p = random.uniform(0, 1)
        running_total = 0
        selected_action = -1
        for action, probit in sorted_probits:
            running_total += probit
            if running_total >= p:
                selected_action = action
                break
        if selected_action < 0:
            selected_action = sorted_probits[-1][0]

        if not self.track_grads:
            return selected_action

        # calculate: grad log(pi(board, selected_action))
        grad = []
        for i in xrange(WeightedPolicy.FEATURES_COUNT):
            f_i = features[selected_action][i]
            prob = 0
            for a in board.legal_actions:
                prob += probits[a] * features[a][i]
            grad.append(f_i - prob)

        self.grads.append(grad)

        return selected_action
