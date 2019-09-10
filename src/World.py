from src.base.Math import *
import copy
class Snake:
    def __init__(self, id):
        self.id = id
        self.head = None
        self.body = []
        self.name = ''
        self.lenght = 0

    def get_body(self):
        return self.body

    def add_body(self, pos):
        self.body.append(pos)

    def get_head(self):
        return self.head

    def set_head(self, pos):
        self.head = pos

    def get_id(self):
        return self.id

    def reset(self, name):
        self.head = None
        # self.body.clear()
        self.name = name

    def manage_body(self, lp):
        if len(lp) == 3:
            if Vector2D(1, 3) in lp and Vector2D(1,2) in lp and Vector2D(1,1) in lp:
                self.body = [Vector2D(1, 3), Vector2D(1, 2), Vector2D(1, 1)]
            elif Vector2D(1, 26) in lp and Vector2D(1,27) in lp and Vector2D(1,28) in lp:
                self.body = [Vector2D(1, 26), Vector2D(1, 27), Vector2D(1, 28)]
            elif Vector2D(28, 3) in lp and Vector2D(28, 2) in lp and Vector2D(28, 1) in lp:
                self.body = [Vector2D(28, 3), Vector2D(28, 2), Vector2D(28, 1)]
            elif Vector2D(28, 26) in lp and Vector2D(28, 27) in lp and Vector2D(28, 28) in lp:
                self.body = [Vector2D(28, 26), Vector2D(28, 27), Vector2D(28,28)]
            else:
                self.body.insert(0, copy.deepcopy(self.head))
                del self.body[-1]
            self.lenght = 3
            return
        if len(lp) == self.lenght:
            self.body.insert(0, copy.deepcopy(self.head))
            del self.body[-1]
        else:
            self.body.insert(0, copy.deepcopy(self.head))
        self.lenght = len(lp)


class World:
    def __init__(self):
        self.board = None
        self.cycle = None
        self.self_id = None
        self.goal_id = None
        self.goal_position = None
        self.snakes = {}
        for s in range(1, 5):
            self.snakes[s] = Snake(s)
        self.walls = []

    def set_id(self, self_id, goal_id):
        self.self_id = self_id
        self.goal_id = goal_id

    def update(self, message):
        self.board = message.world['board']
        self.cycle = message.cycle
        self.walls.clear()
        n = 0
        for s in self.snakes:
            self.snakes[s].reset(list(message.score.keys())[n])
            n += 1

        tmp_snake = [[], [], [], [], []]
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == self.goal_id:
                    self.goal_position = Vector2D(i, j)
                elif self.board[i][j] > 0:
                    tmp_snake[self.board[i][j]].append(Vector2D(i, j))
                elif self.board[i][j] == -1:
                    self.walls.append(Vector2D(i, j))

        for s in self.snakes:
            id = message.name_id[self.snakes[s].name]
            self.snakes[id].set_head(Vector2D(message.world['heads'][self.snakes[s].name][0], message.world['heads'][self.snakes[s].name][1]))

        for s in [1, 2, 3, 4]:
            self.snakes[s].manage_body(tmp_snake[s])

    def get_self(self):
        return self.snakes[self.self_id]

    def get_snake(self, id):
        return self.snakes[id]

    def get_walls(self):
        return self.walls

    def print(self):
        pass
        # print('------------------------------------')
        # print('cycle: {}'.format(self.cycle))
        # for f in self.board:
        #     print(f)
        # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        # for s in self.snakes:
        #     print(self.snakes[s].get_id(), self.snakes[s].get_head(), self.snakes[s].get_body())
        # print('------------------------------------')