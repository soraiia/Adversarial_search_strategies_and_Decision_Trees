import pandas as pd
import math
import random
from collections import Counter
from ConnectState import ConnectState

# === Carregar dataset e construir árvore ===
data = pd.read_csv("connect4_mcts_dataset_clean.csv")
features = [f'col_{i}' for i in range(7)]
target_attribute = 'suggested_move'

# === Entropia ===
def entropy(labels):
    total = len(labels)
    counts = Counter(labels)
    return -sum((count / total) * math.log2(count / total) for count in counts.values() if count > 0)

# === Ganho de informação ===
def information_gain(data, split_attribute, target_attribute='suggested_move'):
    total_entropy = entropy(data[target_attribute])
    values = data[split_attribute].unique()
    subset_entropy = 0.0
    for value in values:
        subset = data[data[split_attribute] == value]
        weight = len(subset) / len(data)
        subset_entropy += weight * entropy(subset[target_attribute])
    return total_entropy - subset_entropy

# === Algoritmo ID3 ===
def id3(data, features, target_attribute='suggested_move'):
    labels = data[target_attribute]
    if len(set(labels)) == 1:
        return labels.iloc[0]
    if len(features) == 0:
        return labels.mode()[0]
    gains = [(attr, information_gain(data, attr, target_attribute)) for attr in features]
    best_attr = max(gains, key=lambda x: x[1])[0]
    tree = {best_attr: {}}
    for value in data[best_attr].unique():
        subset = data[data[best_attr] == value]
        if subset.empty:
            tree[best_attr][value] = labels.mode()[0]
        else:
            remaining_features = [f for f in features if f != best_attr]
            subtree = id3(subset, remaining_features, target_attribute)
            tree[best_attr][value] = subtree
    return tree

# === Classificação ===
def classify(tree, example):
    if not isinstance(tree, dict):
        return tree
    attribute = next(iter(tree))
    value = example.get(attribute)
    if value in tree[attribute]:
        return classify(tree[attribute][value], example)
    else:
        return None

# === Conversão do tabuleiro para formato do dataset ===
def board_to_columns(board):
    return {
        f'col_{c}': "".join(str(board[r][c]) for r in range(5, -1, -1)) for c in range(7)
    }

# === Treinar a árvore (feito uma vez ao carregar o módulo) ===
decision_tree = id3(data, features, target_attribute)

# === Função a ser usada no Game.run() ===
def predict_id3_move(state: ConnectState):
    board = state.get_board()
    example = board_to_columns(board)
    move = classify(decision_tree, example)

    # Fallback caso jogada não seja válida
    legal = state.get_legal_moves()
    if move in legal:
        return move
    elif legal:
        return random.choice(legal)
    else:
        return None
