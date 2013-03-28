import sys
from copy import copy
import math

from simulator import Board, Marker
from arbiter import Arbiter
from policy import BasicPolicy, WeightedPolicy

# Used by compute_gradient to preform the trial runs, assumes policy is playing RED.
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

    # To compute the gradient, the partials are of the form (f(x_1,...,x_j + e,...,x_n) - f(x_1,...,x_n)) / e.
    # We first need to compute the base value of f with the current weights
    base_avg = preform_runs(policy, runs_per_parameter) / runs_per_parameter

    # For each weight, compute the average reward over several runs with the weight perturbed.
    # Then use this average to compute the partial of the reward with respect to the weight.
    for feature_idx in xrange(WeightedPolicy.FEATURES_COUNT):
        weights = copy(original_weights)
        weights[feature_idx] += epsilon
        policy.weights = weights
        
        total_reward = preform_runs(policy, runs_per_parameter)
        avg_reward = total_reward / runs_per_parameter
        partial = (avg_reward - base_avg) / epsilon
        gradient.append(partial)

    # Set the weights back to the original values.
    policy.weights = original_weights

    return base_avg, gradient


def main():
    if len(sys.argv) != 5:
        print "Usage: python gradient.py learning_rate stopping_condition runs_per_parameter epsilon"
        return

    learn = float(sys.argv[1])
    stopping = float(sys.argv[2])
    runs_per_parameter = int(sys.argv[3])
    epsilon = float(sys.argv[4])

    policy = WeightedPolicy(Marker.RED)

    current_avg = 0.0
    while current_avg < stopping:
        # Compute the gradient and the current average reward.
        current_avg, gradient = compute_gradient(policy, runs_per_parameter, epsilon)
        
        # Print debugging info as CSV.
        norm = math.sqrt(sum(map(lambda x: x**2, gradient)))
        print ", ".join(map(str, policy.weights + [norm, current_avg]))

        # Move the weights in the direction of the gradient, tempered by the learning rate.
        for feature_idx in xrange(WeightedPolicy.FEATURES_COUNT):
            policy.weights[feature_idx] += learn * gradient[feature_idx]


if __name__ == '__main__':
    main()
