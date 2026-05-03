import math


EMPTY = -1
PLAYER_A = 0 # Keep as 0 or 1 so we can invert it easier
PLAYER_B = 1
DRAW = 2
BOARD_SIZE = 9

REWARD_WIN = 1.0
REWARD_LOSS = 0.0
REWARD_DRAW = 0.01
REWARD_WIP = 0.5

PLAYER_A_STR = "A"
PLAYER_B_STR = "B"

class State:
    def __init__(self, board:list[int], check_for_winner:bool=False, parent_state=None):
        self.id = hash(tuple(board))
        self.board = board
        self.value = 0.5
        self.next_states: dict[State, State] = {}
        self.parent_state = parent_state
        if check_for_winner:
            self.value = self._calculate_value()

    def _calculate_value(self):
        winner = check_winner(self.board)
        if winner == PLAYER_A:
            return REWARD_WIN
        elif winner == PLAYER_B:
            return REWARD_LOSS
        elif winner == DRAW:
            return REWARD_DRAW
        else:
            return REWARD_WIP
        
    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if not isinstance(other, State):
            return NotImplemented
        return self.board == other.board

def get_possible_states(board:list[int], player:int, depth:int=1, parent_state:State=None, unique_states:dict[State, State]=None) -> list[State]:
    if unique_states is None:
        unique_states: dict[State, State] = {}

    winner = check_winner(board)
    if winner != EMPTY:
        return []  # No next states if the game is already won or drawn

    next_position_indices = [i for i, cell in enumerate(board) if cell == EMPTY]

    for perm in next_position_indices:
        new_board = board.copy()
        new_board[perm] = player
        state = State(new_board.copy(), check_for_winner=True, parent_state=parent_state)

        state_seen = state in unique_states

        if state in unique_states:
            state = unique_states[state] # Replace with existing explored alias
        else:
            unique_states[state] = state

        if parent_state is not None:
            parent_state.next_states[state] = state

        # Recursively get further states if depth > 0
        if depth > 0 and state.value == REWARD_WIP and not state_seen:
            get_possible_states(board=state.board,
                                player=int(not player),
                                depth=depth - 1,
                                parent_state=state,
                                unique_states=unique_states # data is saved to here
                                )
    
    return list(unique_states)

def check_winner(board):
    PLAYER = -2
    winning_lines = [
        # Rows
        [PLAYER, PLAYER, PLAYER, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, PLAYER, PLAYER, PLAYER, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PLAYER, PLAYER, PLAYER],
        # Columns
        [PLAYER, EMPTY, EMPTY, PLAYER, EMPTY, EMPTY, PLAYER, EMPTY, EMPTY],
        [EMPTY, PLAYER, EMPTY, EMPTY, PLAYER, EMPTY, EMPTY, PLAYER, EMPTY],
        [EMPTY, EMPTY, PLAYER, EMPTY, EMPTY, PLAYER, EMPTY, EMPTY, PLAYER],
        # Diagonals
        [PLAYER, EMPTY, EMPTY, EMPTY, PLAYER, EMPTY, EMPTY, EMPTY, PLAYER],
        [EMPTY, EMPTY, PLAYER, EMPTY, PLAYER, EMPTY, PLAYER, EMPTY, EMPTY]
    ]
    
    # Check for winner
    for player in [PLAYER_A, PLAYER_B]:
        for line in winning_lines:
            check_line = [player if x == PLAYER else x for x in line]
            if all(check_line[cell_idx] == EMPTY or board[cell_idx] == player for cell_idx in range(BOARD_SIZE)):
                return player
    
    # Check if board is full (draw)
    if EMPTY not in board:
        return DRAW
    
    return EMPTY

def print_board(board):
    symbols = {EMPTY: '.', PLAYER_A: PLAYER_A_STR, PLAYER_B: PLAYER_B_STR}
    board_step = math.sqrt(BOARD_SIZE)
    for i in range(0, BOARD_SIZE, int(board_step)):
        print(' '.join(symbols[board[j]] for j in range(i, i + int(board_step))))
    print("-" * 10)