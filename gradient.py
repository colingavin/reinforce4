import sys
from copy import copy

from simulator import Board, Marker
from arbiter import Arbiter
from policy import BasicPolicy, WeightedPolicy

def preform_runs(policy, runs):
    total_reward = 0.0
    for run_idx in xrange(runs):
        arbit = Arbiter(policy, BasicPolicy(Marker.BLACK), Board())
        result = arbit.run()
        if result == Marker.RED:
            total_reward += 1.0
        elif result == Marker.VACANT:
            total_reward += 0.5
    return total_reward


def compute_gradient(policy, runs_per_parameter, epsilon):
    original_weights = copy(policy.weights)
    gradient = []

    base_avg = preform_runs(policy, runs_per_parameter) / runs_per_parameter
    print "Base average: " + str(base_avg)

    for feature_idx in xrange(WeightedPolicy.FEATURES_COUNT):
        weights = copy(original_weights)
        weights[feature_idx] += epsilon
        policy.weights = weights
        
        total_reward = preform_runs(policy, runs_per_parameter)
        avg_reward = total_reward / runs_per_parameter
        partial = (avg_reward - base_avg) / epsilon
        gradient.append(partial)

    policy.weights = original_weights
    return base_avg, gradient


def main():
    if len(sys.argv) != 5:
        print "Usage: python gradient.py learn stopping runs_per_parameter epsilon"

    learn = float(sys.argv[1])
    stopping = float(sys.argv[2])
    runs_per_parameter = int(sys.argv[3])
    epsilon = float(sys.argv[4])

    policy = WeightedPolicy(Marker.RED)

    current_avg = 0.0
    while current_avg < stopping:
        print "Current weights:" + str(policy.weights)
        
        current_avg, gradient = compute_gradient(policy, runs_per_parameter, epsilon)
        print "Gradient: " + str(gradient)

        for feature_idx in xrange(WeightedPolicy.FEATURES_COUNT):
            policy.weights[feature_idx] += gradient[feature_idx]

    print "Final weights:" + str(policy.weights)

if __name__ == '__main__':
    main()
