import csv
from tqdm import tqdm
from ConnectState import ConnectState
from mcts import MCTS
import os

NUM_SAMPLES = 10000
TIME_PER_MOVE = 0.2
dataset = []

def board_to_flat_list(board):
    """Transforma a matriz 6x7 em uma lista de 42 valores (linha por linha)."""
    return [cell for row in board for cell in row]

pbar = tqdm(total=NUM_SAMPLES)

while len(dataset) < NUM_SAMPLES:
    estado = ConnectState()
    mcts = MCTS(estado)
    partida = []  # Aqui vamos guardar os (estado, jogada) do jogador 2

    while not estado.game_over():
        mcts.search(TIME_PER_MOVE)
        move = mcts.best_move()
        if move == -1:
            break

        if estado.to_play == 2:
            board = estado.get_board()
            flat_board = board_to_flat_list(board)
            partida.append(flat_board + [move])  # Armazena estado + jogada feita

        estado.move(move)
        mcts.move(move)

    # Após a partida, verifica se o jogador 2 venceu
    if estado.get_outcome() == 2:  # jogador 2 venceu
        for jogada in partida:
            if len(dataset) >= NUM_SAMPLES:
                break
            dataset.append(jogada)
            pbar.update(1)
    
    # Cabeçalho com 42 células + jogada sugerida
header = [f'cell_{i}' for i in range(42)] + ['suggested_move']

with open("connect4_mcts_dataset_filtered.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(dataset)

print("Dataset gerado com sucesso!")
print("Salvo em:", os.path.abspath("connect4_mcts_dataset_filtered.csv"))

