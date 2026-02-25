import math, time, random
from ConnectState import ConnectState


EXPLORATION = math.sqrt(2)
PLAYERS = {'none': 0, 'one': 1, 'two': 2}
OUTCOMES = {'none': 0, 'one': 1, 'two': 2, 'draw': 3}
INF = float('inf')
ROWS = 6
COLS = 7

class Node:
    def __init__(self,move,parent):
        self.move = move #jogada para chegar a este nó(estado do jogo)
        self.parent = parent #nó pai- estado do jogo antes da ultima jogada
        self.N=0 #numero de vezes que este nó foi visitado
        self.Q=0 #numero de vezes que venceu
        self.children = {} #guarda os filhos do nó
        self.outcome = PLAYERS['none'] #resultado do jogo após esta jogada - continua, alguém ganhou ou empate

    
    def add_children (self, children : dict)-> None : #adiciona os filhos do nó atual
        for child in children:
            self.children[child.move]=child
    
    def value (self, explore : float = EXPLORATION): # retorna o valor do UCT, utilizando c=raiz de 2
        if self.N == 0:
            return 0 if explore==0 else INF
        else:
            return self.Q / self.N + explore* math.sqrt(math.log(self.parent.N)/ self.N)


class MCTS:
    def __init__(self, state = ConnectState()):
        self.root_state = state.clone() #clona o estado iniciak do jogo
        self.root = Node (None,None) #cria uma árvore
        self.run_time = 0  #inicializa as variaveis temporais
        self.node_count = 0
        self.num_rollouts = 0
    
    def select_node(self) -> tuple:  #retorna o nó com UCT maior - mais promissor
        node = self.root
        state = self.root_state.clone()

        while len(node.children) !=0:
            children = node.children.values()
            max_value = max(children, key = lambda n : n.value()).value() #calcula o valor mazimo de UCT
            max_nodes = [n for n in children if n.value() == max_value] #seleciona os nós dos nós filhos com a maior UCT

            node = random.choice(max_nodes)
            state.move(node.move)

            if node.N == 0:
                return node,state  #se um nó nunca tiver sido visitado, o select_node devolve essse nó
        if self.expand (node , state): #se o nó não for terminal, é expandido
            node = random.choice(list(node.children.values()))
            state.move(node.move)
        return node, state
    
    def expand (self, parent : Node, state : ConnectState) -> bool: #cria todos os nós filhos possíveis para o estado atual do tabuleiro. Tendo em conta os movimentos permitidos no momento
        if state.game_over():
            return False
        children = [Node(move,parent)for move in state.get_legal_moves()] #cria todos os filhos originados a partir do nó pai + legal moves
        parent.add_children(children)
        return True
    
    def roll_out (self , state : ConnectState)-> int: #simula uma partida com jogadas aleatorias até ao fim. retorna o vencedor
        while not state.game_over():
            state.move(random.choice(state.get_legal_moves()))
        return state.get_outcome()
    
    def back_propagate (self,node : Node, turn: int, outcome:int)-> None : 
        reward = 0 if outcome == turn else 1
        while node is not None:
            node.N +=1 #atualiza as estatisticas
            node.Q +=reward
            node = node.parent
            if outcome==OUTCOMES['draw']:
                reward = 0  #empate
            else:
                reward = 1-reward

    def search(self, time_limit : int):
        start_time = time.process_time()
        num_rollouts =0
        while time.process_time() - start_time < time_limit:
            node, state = self.select_node()
            outcome = self.roll_out(state)
            self.back_propagate(node,self.root_state.to_play, outcome)
            num_rollouts+=1
        self.run_time = time.process_time()-start_time
        self.num_rollouts = num_rollouts

    def best_move(self): #devolve o melhor mov a fazer
        if self.root_state.game_over():
            return -1
        max_value = max(self.root.children.values(), key = lambda n:n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N==max_value]
        best_child = random.choice(max_nodes)
        return best_child.move
    
    def move(self, move):
        if move in self.root.children:
            self.root_state.move(move) 
            self.root = self.root.children[move] #atualiza o nó
            return
        self.root_state.move(move)
        self.root = Node(None,None)

    def statistics(self)-> tuple: #retorna total de simulaçaoes e tempo gasto
        return self.num_rollouts, self.run_time
    
    def move_statistics(self): # retorna {jogada: (visitas, vitórias)} para todos os filhos da raiz.
        return {move: (child.N, child.Q) for move, child in self.root.children.items()}

