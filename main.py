from knots import *
import random

# BUG: AI DOESN'T WIN AS FAST AS POSSIBLE
# BUG: AI DOESN'T LEARN TO BLOCK OPPONENT'S WINNING MOVES


def choose_reinforced_move(state:State, greed:float) -> State:
    highest_value_state = max(state.next_states, key=lambda s: s.value)
    greed_step = random.random() < greed
    if greed_step: # Exploitation step
        return highest_value_state
    else: # Exploration step
        return choose_random_move(state)

def choose_random_move(state:State) -> State:
    choice = random.choice(list(state.next_states.values()))
    return choice

def assign_rewards(epoch_states:list[State], player:int):
    winner = check_winner(epoch_states[-1].board)
    reward = REWARD_WIN if winner == player else REWARD_LOSS
    for state in epoch_states:
        state.value += (reward - state.value) * LEARNING_RATE
        state.value = max(min(state.value, REWARD_WIN), REWARD_LOSS)  # Ensure value stays within bounds

def play(initial_state:State, greed:float, show:bool=False) -> list[State]:
    state = initial_state
    epoch_states = []
    while True:
        state = choose_reinforced_move(state, greed)
        winner = check_winner(state.board)
        epoch_states.append(state)
        
        if winner == EMPTY:
            state = choose_random_move(state)
            winner = check_winner(state.board)
            epoch_states.append(state)

        if winner != EMPTY:
            break

    if show:
        print("AGENT == " + (PLAYER_A_STR if AGENT == PLAYER_A else PLAYER_B_STR))
        print_board(initial_state.board)
        for state in epoch_states:
            print_board(state.board)

    return epoch_states

# Train
AGENT = PLAYER_A
OPPONENT = PLAYER_B

STARTING_PLAYER = PLAYER_A
EPOCHS = 10000
MAX_GREED = 0.7
LEARNING_RATE = 0.01

empty_state = State([EMPTY] * BOARD_SIZE)
state_tree:list[State] = get_possible_states(empty_state.board, STARTING_PLAYER, depth=BOARD_SIZE, parent_state=empty_state)

for epoch in range(EPOCHS):
    if epoch % (EPOCHS // 10) == 0: # Every 10% of epochs, print progress
        print(f"Epoch {epoch+1}/{EPOCHS}")

    greed = MAX_GREED * epoch / EPOCHS  # Decrease greed over time
    
    random_starting_state = random.choice(list(empty_state.next_states.values()))
    state = random_starting_state

    epoch_states = play(state, greed)

    assign_rewards(epoch_states, AGENT)

# Verify
VERIFICATION_EPOCHS = 100
wins = 0

for i in range(VERIFICATION_EPOCHS):
    random_starting_state = random.choice(list(empty_state.next_states.values()))
    state = random_starting_state

    epoch_states = play(state, 1, show=(i == VERIFICATION_EPOCHS - 1))

    winner = check_winner(epoch_states[-1].board)
    if winner == AGENT:
        wins += 1

print(f"Winner: {'Agent' if winner == AGENT else 'Opponent' if winner == OPPONENT else 'Draw'}")
print(f"Agent win rate: {wins / VERIFICATION_EPOCHS:.2%}")
