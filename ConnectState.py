import numpy as np
from copy import deepcopy

class GameMeta:  # Define o jogo, isto é, as constantes usadas pelo jogo: jogadores, resultados, dimensões do tabuleiro...
    PLAYERS = {'none': 0, 'one': 1, 'two': 2} 
    OUTCOMES = {'none': 0, 'one': 1, 'two': 2, 'draw': 3} #Define o estado do jogo: 'none' se o jogo ainda não tiver acabado, 'one' se o jogador 1 ganhou, 'two' se o jogador 2 ganhou e 'draw' se empataram
    INF = float('inf')
    ROWS = 6
    COLS = 7

class ConnectState:
    def __init__(self):
        self.board = [[0] * GameMeta.COLS for _ in range(GameMeta.ROWS)] #inicializa o tabuleiro 6*7 com '0' em todas as posiçoes. A board numera as celulas de cima para baixo e da direita para a esquerda.
        self.to_play = GameMeta.PLAYERS['one'] #começa o jogador 1 a jogar
        self.height = [GameMeta.ROWS - 1] * GameMeta.COLS #guarda a linha disponível mais alta de cada coluna
        self.last_played = [] #guarda o último movimento feito

    def get_board(self): #retorna uma copia do tabuleiro
        return deepcopy(self.board)

    def move(self, col):  #Aplica o movimento ao tabuleiro existente 
        self.board[self.height[col]][col] = self.to_play #atualiza o tabuleiro: a linha mais baixa da coluna selecionada passa de '0' para '1' ou '2', dependendo de quem está a jogar
        self.last_played = [self.height[col], col] #guarda o movimento no last_played como último mov
        self.height[col] -= 1 #atualiza a 'altura' da coluna em que jogou
        self.to_play = GameMeta.PLAYERS['two'] if self.to_play == GameMeta.PLAYERS['one'] else GameMeta.PLAYERS['one'] #Passa a vez para o outro jogador

    def get_legal_moves(self):  #Retorna as colunas onde é possível jogar, ou seja, colunas cuja última linha='0'(primeira linha da matriz vazia)
        return [col for col in range(GameMeta.COLS) if self.board[0][col] == 0]

    def check_win(self): #retorna o jogador que ganhou se houver vitória
        if len(self.last_played) > 0 and self.check_win_from(self.last_played[0], self.last_played[1]):
            return self.board[self.last_played[0]][self.last_played[1]]   #retorna o jogador que ganhou, ou seja, o numero presente na celula da ultima jogada.
        return 0

    def check_win_from(self, row, col): #verifica se na celula (row, col) há algum 4 em linha do jogador que está a jogar, verificando a vertical, a horizontal e as diagonais que passam nessa celula. Se o numero de peças alinhadas (verticalmente, horizontalmente ou diagonalmente) for >=4, o check_win_from retorna true, ou seja, o jogador ganhou
        player = self.board[row][col]

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in [1, -1]:
                r, c = row, col
                while True:
                    r += i * dr
                    c += i * dc
                    if 0 <= r < GameMeta.ROWS and 0 <= c < GameMeta.COLS and self.board[r][c] == player:
                        count += 1
                    else:
                        break
            if count >= 4:
                return True
        return False
    
    def game_over(self):  #Verifica se o jogo acabou, ou seja,  verifica se alguém ganhou ou se já não há mais jogadas possíveis
        return self.check_win() or len(self.get_legal_moves()) == 0

    def get_outcome(self): #Retorna o jogador que ganhou ou empate
        if len(self.get_legal_moves()) == 0 and self.check_win() == 0: #se não há jogadas possíveis e não houve nenhum vencedor até ao memento, retorna empate
            return GameMeta.OUTCOMES['draw']
        return GameMeta.OUTCOMES['one'] if self.check_win() == GameMeta.PLAYERS['one'] else GameMeta.OUTCOMES['two']
    
    def clone(self): #clona o estado atual do tabuleiro
        new_state = ConnectState()
        new_state.board = [row[:] for row in self.board]
        new_state.to_play = self.to_play
        return new_state


    def print(self): #faz o print do tabuleiro no terminal, x - 1 e o - 2
        print('=============================')
        for row in range(GameMeta.ROWS):
            for col in range(GameMeta.COLS):
                print('| {} '.format('X' if self.board[row][col] == 1 else 'O' if self.board[row][col] == 2 else ' '), end='')
            print('|')
        print('=============================')
