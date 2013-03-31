import sys
from copy import copy
import math
import operator

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
            total_reward += 0.0
        else:
            total_reward -= 1.0
    return total_reward


def compute_gradient(policy, runs_to_estimate):
    grad = [0.0 for i in xrange(WeightedPolicy.FEATURES_COUNT)]
    total_reward = 0.0

    # Run several games and accumulate a gradient estimate.
    for j in xrange(runs_to_estimate):
        policy.clear_gradients()
        arbit = Arbiter(policy, BasicPolicy(Marker.BLACK), Board())
        result = arbit.run()
        # Draws don't contribute anything to the gradient.
        if result == Marker.VACANT:
            continue
        elif result == Marker.RED:
            total_reward += 1.0
        else:
            total_reward -= 1.0

        for pi_grad in policy.grads:
            if result == Marker.RED:
                grad = map(operator.add, grad, pi_grad)
            else:
                grad = map(operator.sub, grad, pi_grad)

    # Normalize the gradient estimate
    grad = map(lambda d: d / runs_to_estimate, grad)
    return total_reward / runs_to_estimate, grad


def main():
    if len(sys.argv) != 4:
        print "Usage: python gradient.py learning_rate stopping_condition runs_to_estimate"
        return

    learn = float(sys.argv[1])
    stopping = float(sys.argv[2])
    runs_to_estimate = int(sys.argv[3])

    policy = WeightedPolicy(Marker.RED, True)

    current_avg = 0.0
    while current_avg < stopping:
        # Compute the gradient and the current average reward.
        current_avg, gradient = compute_gradient(policy, runs_to_estimate)
        
        # Print debugging info as CSV.
        norm = math.sqrt(sum(map(lambda x: x**2, gradient)))
        print ", ".join(map(str, policy.weights + [norm, current_avg]))

        # Move the weights in the direction of the gradient, tempered by the learning rate.
        for feature_idx in xrange(WeightedPolicy.FEATURES_COUNT):
            policy.weights[feature_idx] += learn * gradient[feature_idx]


if __name__ == '__main__':
    main()
