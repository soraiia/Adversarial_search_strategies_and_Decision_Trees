import numpy as np
import pygame
import sys
import math
from ConnectState import ConnectState
from mcts import MCTS
from id3_model import predict_id3_move


class GameMeta:
    PLAYERS = {'none': 0, 'one': 1, 'two': 2}
    OUTCOMES = {'none': 0, 'one': 1, 'two': 2, 'draw': 3}
    INF = float('inf')
    ROWS = 6
    COLS = 7

class Game:
    AZUL = (100, 149, 237)
    ROSA = (255, 182, 193)
    AMARELO = (255, 255, 153)
    BRANCO = (255, 255, 255)
    PRETO = (0,0,0)

    TAMANHO_QUADRADO = 100
    RAIO = int(TAMANHO_QUADRADO / 2 - 5)

    def __init__(self):
        self.estado = ConnectState()
        self.jogo_acabou = False
        self.modo = None
        self.mcts = MCTS(self.estado)
        pygame.init()
        self.grafico_largura = 600
        self.largura = GameMeta.COLS * self.TAMANHO_QUADRADO
        self.altura = (GameMeta.ROWS + 1) * self.TAMANHO_QUADRADO
        self.tela = pygame.display.set_mode((self.largura + self.grafico_largura, self.altura))
        self.fonte = pygame.font.SysFont("monospace", 65)
        self.fonte_pequena = pygame.font.SysFont("monospace", 20)
        self.fonte_menu = pygame.font.SysFont("monospace", 30)
        self.menu()

    def menu(self):
        self.tela.fill(self.BRANCO)
        pvp_text = self.fonte_menu.render("Player vs Player", True, self.PRETO)
        ai_text = self.fonte_menu.render("Player vs MCTS", True, self.PRETO)
        id3_text = self.fonte_menu.render("Player vs ID3", True, self.PRETO)

        self.tela.blit(pvp_text, (self.largura / 2 - pvp_text.get_width() / 2, 150))
        self.tela.blit(ai_text, (self.largura / 2 - ai_text.get_width() / 2, 250))
        self.tela.blit(id3_text, (self.largura / 2 - id3_text.get_width() / 2, 350))

        pygame.display.update()

        while self.modo is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 150 <= y <= 200:
                        self.modo = 'pvp'
                    elif 250 <= y <= 300:
                        self.modo = 'ai'
                    elif 350 <= y <= 400:
                        self.modo = 'id3'

        
        self.tela.fill(self.BRANCO)               
        self.desenhar_tabuleiro()

    def desenhar_tabuleiro(self):
        # Draw game board
        for c in range(GameMeta.COLS):
            for l in range(GameMeta.ROWS):
                pygame.draw.rect(self.tela, self.AZUL, (c * self.TAMANHO_QUADRADO, (l + 1) * self.TAMANHO_QUADRADO, self.TAMANHO_QUADRADO, self.TAMANHO_QUADRADO))
                pygame.draw.circle(self.tela, self.BRANCO, (int(c * self.TAMANHO_QUADRADO + self.TAMANHO_QUADRADO / 2), int((l + 1) * self.TAMANHO_QUADRADO + self.TAMANHO_QUADRADO / 2)), self.RAIO)

        # Draw pieces
        board = self.estado.get_board()
        for c in range(GameMeta.COLS):
            for l in range(GameMeta.ROWS):
                if board[l][c] == 1:
                    pygame.draw.circle(self.tela, self.ROSA, (int(c * self.TAMANHO_QUADRADO + self.TAMANHO_QUADRADO / 2), int((l + 1) * self.TAMANHO_QUADRADO + self.TAMANHO_QUADRADO / 2)), self.RAIO)
                elif board[l][c] == 2:
                    pygame.draw.circle(self.tela, self.AMARELO, (int(c * self.TAMANHO_QUADRADO + self.TAMANHO_QUADRADO / 2), int((l + 1) * self.TAMANHO_QUADRADO + self.TAMANHO_QUADRADO / 2)), self.RAIO)
        
        # Draw graph
        self.desenhar_estatisticas_mcts()
        pygame.display.update()
    
    def desenhar_estatisticas_mcts(self):
        if not hasattr(self, 'estatisticas_mcts') or not self.estatisticas_mcts:
            # Clear graph area if no statistics
            pygame.draw.rect(self.tela, self.BRANCO, (self.largura, 0, self.grafico_largura, self.altura))
            return

        graph_x_offset = self.largura + 50
        graph_top = 300
        bar_width = 35
        bar_spacing = 35
        max_bar_height = 200
        label_gap = 5
        text_height = 15

        # Clear graph area
        pygame.draw.rect(self.tela, self.BRANCO, (self.largura, 0, self.grafico_largura, self.altura))

        # Calculate max visits for scaling
        visits = [n for (n, q) in self.estatisticas_mcts.values()]
        max_visits = max(visits) if visits else 1

        # We always want to show all 7 possible columns
        moves_to_display = sorted(self.estatisticas_mcts.items(), key=lambda x: x[0])
        
        for i, (move, (n, q)) in enumerate(moves_to_display):
            # Calculate bar dimensions
            bar_height = int((n / max_visits) * max_bar_height) if max_visits > 0 else 0
            win_ratio = q / n if n > 0 else 0
            win_height = int(win_ratio * bar_height) if bar_height > 0 else 0

            # Calculate positions
            bar_x = graph_x_offset + i * (bar_width + bar_spacing)
            bar_y = graph_top + (max_bar_height - bar_height)

            # Draw total visit bar (blue)
            pygame.draw.rect(self.tela, self.AZUL, (bar_x, bar_y, bar_width, bar_height))

            # Draw win portion (red)
            pygame.draw.rect(self.tela, (255, 0, 0), (bar_x, bar_y + bar_height - win_height, bar_width, win_height))

            # Draw move number below bar (always visible)
            move_text = self.fonte_pequena.render(f"Col {move+1}", True, self.PRETO)
            text_x = bar_x + (bar_width - move_text.get_width()) // 2
            text_y = graph_top + max_bar_height + label_gap
            self.tela.blit(move_text, (text_x, text_y))

            # Draw statistics above the bar
            stats_y = bar_y - 40  # Position above the bar
            
            # Draw wins (W) above bar
            wins_text = self.fonte_pequena.render(f"W:{int(q)}", True, self.PRETO)
            wins_x = bar_x + (bar_width - wins_text.get_width()) // 2
            self.tela.blit(wins_text, (wins_x, stats_y))

            # Draw visits (V) above wins
            visits_text = self.fonte_pequena.render(f"T:{n}", True, self.PRETO)
            visits_x = bar_x + (bar_width - visits_text.get_width()) // 2
            self.tela.blit(visits_text, (visits_x, stats_y - text_height - 2))

            # Draw win percentage below the move label
            win_pct = f"{win_ratio*100:.1f}%" if n > 0 else "0%"
            pct_text = self.fonte_pequena.render(win_pct, True, self.PRETO)
            pct_x = bar_x + (bar_width - pct_text.get_width()) // 2
            pct_y = text_y + move_text.get_height() + 2
            self.tela.blit(pct_text, (pct_x, pct_y))

        # Add title and legend
        title_text = self.fonte_pequena.render("MCTS Move Statistics", True, self.PRETO)
        self.tela.blit(title_text, (graph_x_offset + (self.grafico_largura - 40 - title_text.get_width()) // 2, 20))

        # Add legend
        legend_y = graph_top + max_bar_height + 80
        pygame.draw.rect(self.tela, self.AZUL, (graph_x_offset, legend_y, 15, 15))
        legend_text = self.fonte_pequena.render("Total visits (T)", True, self.PRETO)
        self.tela.blit(legend_text, (graph_x_offset + 20, legend_y))

        pygame.draw.rect(self.tela, (255, 0, 0), (graph_x_offset, legend_y + 20, 15, 15))
        legend_text2 = self.fonte_pequena.render("Winning visits (W)", True, self.PRETO)
        self.tela.blit(legend_text2, (graph_x_offset + 20, legend_y + 20))
    def run(self):
        while not self.jogo_acabou:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    sys.exit()

                if evento.type == pygame.MOUSEMOTION:
                    # Only draw the preview in the game area (not the graph area)
                    if evento.pos[0] < self.largura-50:
                        pygame.draw.rect(self.tela, self.BRANCO, (0, 0, self.largura, self.TAMANHO_QUADRADO))
                        pos_x = evento.pos[0]
                        cor = self.ROSA if self.estado.to_play == 1 else self.AMARELO
                        pygame.draw.circle(self.tela, cor, (pos_x, int(self.TAMANHO_QUADRADO / 2)), self.RAIO)
                        pygame.display.update()

                if evento.type == pygame.MOUSEBUTTONDOWN:
                    # Only process clicks in the game area
                    if evento.pos[0] < self.largura:
                        pygame.draw.rect(self.tela, self.BRANCO, (0, 0, self.largura, self.TAMANHO_QUADRADO))
                        pos_x = evento.pos[0]
                        coluna = int(math.floor(pos_x / self.TAMANHO_QUADRADO))

                        if coluna in self.estado.get_legal_moves():
                            self.estado.move(coluna)
                            self.mcts.move(coluna)
                            self.desenhar_tabuleiro()

                            winner = self.estado.check_win()
                            if winner:
                                texto = self.fonte.render(f"Jogador {winner} venceu!", 1, self.ROSA if winner == 1 else self.AMARELO)
                                self.tela.blit(texto, (40, 10))
                                self.jogo_acabou = True
                            elif self.modo == 'ai' and not self.estado.game_over():
                                self.mcts.search(5)
                                self.estatisticas_mcts = self.mcts.move_statistics()
                                movimento_mcts = self.mcts.best_move()
                                self.estado.move(movimento_mcts)
                                self.mcts.move(movimento_mcts)
                                self.desenhar_tabuleiro()
                                winner = self.estado.check_win()
                                if winner:
                                    texto = self.fonte.render(f"Jogador {winner} venceu!", 1, self.ROSA if winner == 1 else self.AMARELO)
                                    self.tela.blit(texto, (40, 10))
                                    self.jogo_acabou = True
                            
                            elif self.modo == 'id3' and not self.estado.game_over():
                                from id3_model import predict_id3_move  # <-- função que você implementou
                                movimento_id3 = predict_id3_move(self.estado)
                                if movimento_id3 is not None:
                                    self.estado.move(movimento_id3)
                                    self.desenhar_tabuleiro()
                                    winner = self.estado.check_win()
                                    if winner:
                                        texto = self.fonte.render(f"Jogador {winner} venceu!", 1, self.ROSA if winner == 1 else self.AMARELO)
                                        self.tela.blit(texto, (40, 10))
                                        self.jogo_acabou = True


                            if self.jogo_acabou:
                                pygame.display.update()
                                pygame.time.wait(3000)

if __name__ == "__main__":
    game = Game()
    game.run()