from copy import copy, deepcopy

class Marker(object):
    DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]
    VACANT = -1
    RED = 0
    BLACK = 1

    def __init__(self, ty):
        super(Marker, self).__init__()
        self.ty = ty
        self.line_counts = dict([(d, 0) for d in Marker.DIRECTIONS])

    def __eq__(self, other):
        return isinstance(other, Marker) and self.ty == other.ty and self.lines == other.lines

    def clone(self):
        cpy = Marker(self.ty)
        cpy.line_counts = copy(self.line_counts)
        return cpy

    @property
    def is_vacant(self):
        return self.ty == Marker.VACANT

    @classmethod
    def vacant(cls):
        return cls(Marker.VACANT)

    @classmethod
    def red(cls):
        return cls(Marker.RED)

    @classmethod
    def black(cls):
        return cls(Marker.BLACK)

    @classmethod
    def of_type(cls, to_clone):
        return cls(to_clone.ty)

    def __str__(self):
        if self.ty == Marker.RED:
            return "*"
        elif self.ty == Marker.BLACK:
            return "#"
        else:
            return " "

    def __repr__(self):
        return str(self) + ": " + str(self.line_counts)


class Board(object):
    WIN_COUNT = 4

    def __init__(self, w=7, h=6):
        super(Board, self).__init__()
        self.w = w
        self.h = h
        self.first_unfilled = dict([(col, 0) for col in range(w)])
        self.board = [[Marker.vacant() for col in range(w)] for row in range(h)]
        self.terminal = False
        self.neighbors = [[[] for col in range(w)] for row in range(h)]
        self.winner = Marker.VACANT
        deltas = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        for row in xrange(self.h):
            for col in xrange(self.w):
                for delta in deltas:
                    n = (row + delta[0], col + delta[1])
                    if self.on_board(n):
                        self.neighbors[row][col].append(n)
        self.stack = []

    def push(self):
        board_copy = [[self.board[row][col].clone() for col in range(self.w)] for row in range(self.h)]
        self.stack.append((copy(self.first_unfilled), board_copy, self.terminal, self.winner))

    def pop(self):
        if len(self.stack) == 0:
            raise Exception("Cannot pop with empty stack.")

        self.first_unfilled, self.board, self.terminal, self.winner = self.stack.pop()

    def __repr__(self):
        def row_repr(pair):
            idx, row = pair
            pieces = " ".join(map(str, row))
            return "%i %s" % (idx, pieces)

        row_idxs = " ".join([str(i) for i in range(0, self.w)])
        return "\n".join(map(row_repr, reversed(list(enumerate(self.board))))) + "\n  " + row_idxs

    def on_board(self, pt):
        return pt[0] >= 0 and pt[1] >= 0 and pt[0] < self.h and pt[1] < self.w

    @property
    def legal_actions(self):
        return filter(lambda col: self.first_unfilled[col] is not None, self.first_unfilled)

    def line_counts(self, row, col, direction, ty):
        if self.on_board((row, col)):
            m = self.board[row][col]
            if m.ty == ty:
                return m.line_counts[direction]
        return 0

    def total_line_count(self, row, col, direction, ty):
        pos_count = self.line_counts(row + direction[0], col + direction[1], direction, ty)
        neg_count = self.line_counts(row - direction[0], col - direction[1], direction, ty)
        return pos_count + neg_count + 1


    def update_line_counts(self, row, col):
        for direction in Marker.DIRECTIONS:
            
            ty = self.board[row][col].ty
            updated = self.total_line_count(row, col, direction, ty)
            
            self.update_line_counts_in_direction(row, col, direction, updated, 1)
            self.update_line_counts_in_direction(row, col, direction, updated, -1)
            if updated >= Board.WIN_COUNT:
                self.terminal = True
                self.winner = self.board[row][col].ty

    def update_line_counts_in_direction(self, row, col, direction, updated, flip):
        self.board[row][col].line_counts[direction] = updated
        next_row = row + flip*direction[0]
        next_col = col + flip*direction[1]
        
        if self.on_board((next_row, next_col)) and self.board[next_row][next_col].ty == self.board[row][col].ty:
                self.update_line_counts_in_direction(next_row, next_col, direction, updated, flip)

    def play(self, col, color):
        row = self.first_unfilled[col]
        if row is None:
            raise Exception("Attempt to play in filled column.")
        # place the marker and expand the lines
        new_marker = Marker(color)
        self.board[row][col] = new_marker
        self.update_line_counts(row, col)
        # keep track of the top of the stacks
        row += 1
        if row == self.h:
            row = None
        self.first_unfilled[col] = row
        if len(self.legal_actions) == 0:
            self.terminal = True


if __name__ == '__main__':
    b = Board()
    b.play(0, Marker.BLACK)
    b.play(1, Marker.BLACK)
    #b.play(1, Marker.BLACK)
    b.play(2, Marker.BLACK)
    b.play(3, Marker.BLACK)
    print b
    print repr(b.board[0][0])
    print repr(b.board[0][2])
    print b.terminal
    print repr(b.board[1][3])
