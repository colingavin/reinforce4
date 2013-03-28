import sys
import policy
from arbiter import Arbiter
from simulator import Board, Marker


def lookup_policy(name):
    return getattr(policy, name)

def main():
    if len(sys.argv) != 4:
        print "Usage: main red_player black_player games"
        return
    
    red_player = lookup_policy(sys.argv[1])
    black_player = lookup_policy(sys.argv[2])
    games = int(sys.argv[3])

    red_wins = 0
    draws = 0
    for count in xrange(games):
        arbiter = Arbiter(red_player(Marker.RED), black_player(Marker.BLACK), Board())
        result = arbiter.run()
        if result == Marker.RED:
            red_wins += 1
        elif result == Marker.VACANT:
            draws += 1

    print "Red wins: %i" % red_wins
    print "Black wins: %i" % (games - (red_wins + draws))
    print "Draws: %i" % draws


if __name__ == '__main__':
    main()
