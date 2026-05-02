from knots import *
import math
import random

def choose_agent_move(state:State, greed:float) -> State:
    highest_value_state = max(state.next_states, key=lambda s: s.value)
    greed_step = random.random() < greed
    if greed_step: # Exploitation step
        return highest_value_state
    else: # Exploration step
        valid_states = [s for s in state.next_states if s.value > REWARD_LOSS] # Don't choose losing states
        return random.choice(valid_states)

def choose_random_empty(state:State, player:int=PLAYER_B) -> State:
    # Choose a random empty position on the board
    next_position_indices = [i for i, cell in enumerate(state.board) if cell == EMPTY]
    choice = random.choice(next_position_indices)

    # Create a copy to find in the state tree
    find_board = state.board.copy()
    find_board[choice] = player  # Place the specified player's move on the board

    # Find the board in the state tree
    found_board = next((s for s in state_tree if s.board == find_board), None)
    if found_board is None:
        raise ValueError("Board state not found in state tree")
    return found_board

def assign_rewards(epoch_states:list[State], player:int):
    winner = check_winner(epoch_states[-1].board)
    reward = REWARD_WIN if winner == player else REWARD_LOSS
    for state in epoch_states:
        state.value += (reward - state.value) * LEARNING_RATE
        state.value = max(min(state.value, REWARD_WIN), REWARD_LOSS)  # Ensure value stays within bounds

# Train
AGENT = PLAYER_A
OPPONENT = PLAYER_B

STARTING_PLAYER = PLAYER_A
EPOCHS = 100
STARTING_GREED = 0.5
LEARNING_RATE = 0.1

empty_board = [EMPTY] * BOARD_SIZE
state_tree:list[State] = get_possible_states(empty_board, STARTING_PLAYER, depth=BOARD_SIZE)
starting_state = state_tree[0].board

for epoch in range(EPOCHS):
    if epoch % (EPOCHS // 10) == 0: # Every 10% of epochs, print progress
        print(f"Epoch {epoch+1}/{EPOCHS}")

    greed = STARTING_GREED * (0.95 ** epoch)  # Decrease greed over time
    state = starting_state
    epoch_states = []
    while True:
        state = choose_agent_move(state, greed)
        winner = check_winner(state)
        
        if winner == EMPTY:
            state = choose_random_empty(state)
            winner = check_winner(state)
        
        epoch_states.append(state)
        if winner != EMPTY:
            assign_rewards(epoch_states, AGENT)

# Verify
while True:
    state = choose_agent_move(state, 1)
    print_board(state.board)
    
    winner = check_winner(state)
    if winner == EMPTY:
        state = choose_random_empty(state)
        print_board(state.board)
        winner = check_winner(state)

    if winner != EMPTY:
        print(f"Winner: {'Agent' if winner == AGENT else 'Opponent' if winner == OPPONENT else 'Draw'}")
        break
    