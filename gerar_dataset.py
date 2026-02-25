
import csv
from tqdm import tqdm
from ConnectState import ConnectState
from mcts import MCTS
import os

NUM_SAMPLES = 1000
TIME_PER_MOVE = 0.2
dataset = []

def board_to_flat_list(board):
    """Transforma a matriz 6x7 em uma lista de 42 elementos (linha por linha)"""
    return [cell for row in board for cell in row]

pbar = tqdm(total=NUM_SAMPLES)

while len(dataset) < NUM_SAMPLES:
    estado = ConnectState()
    mcts = MCTS(estado)

    while not estado.game_over() and len(dataset) < NUM_SAMPLES:
        if estado.to_play != 2:
            # Jogador 1 joga aleatório ou MCTS curto
            mcts.search(0.1)
            move = mcts.best_move()
            estado.move(move)
            mcts.move(move)
            continue

        mcts.search(TIME_PER_MOVE)
        move = mcts.best_move()
        if move == -1:
            break

        board = estado.get_board()  # matriz 6x7
        flat_board = board_to_flat_list(board)  # lista com 42 valores
        dataset.append(flat_board + [move])  # adiciona a jogada sugerida como última coluna
        pbar.update(1)

        estado.move(move)
        mcts.move(move)

# Salvar CSV
header = [f'cell_{i}' for i in range(42)] + ['suggested_move']
with open("connect4_mcts_dataset.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(dataset)

print("Dataset gerado com sucesso.")
print("Dataset salvo em:", os.path.abspath("connect4_mcts_dataset_clean.csv"))
