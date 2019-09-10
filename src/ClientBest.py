from src.World import *
from copy import copy

max_i = 0
max_j = 0


def set_max(world: World):
    global max_i, max_j
    max_i = len(world.board) - 1
    max_j = len(world.board[0]) -1
    
    
def is_valid(point: Vector2D):
    if point.i < 0 or point.i > max_i:
        return False
    if point.j < 0 or point.j > max_j:
        return False
    return True


def get_nearest_pos(start: Vector2D):
    ret = []
    ret.append(start + Vector2D(1,  0))
    ret.append(start + Vector2D(-1, 0))
    ret.append(start + Vector2D(0,  1))
    ret.append(start + Vector2D(0, -1))
    return ret


def get_nearest_path(world: World, start: Vector2D, target: Vector2D, id):
    board = copy(world.board)
    dist_table = [[0 for _ in range(len(board[0]))] for __ in range(len(board))]
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == -1:
                dist_table[i][j] = -1000  # Wall
            elif board[i][j] > 0 and board[i][j] != 5:
                dist_table[i][j] = -1  # snakes
            elif board[i][j] in [0, 5]:
                dist_table[i][j] = -2000  # Free
    for s in [1, 2, 3, 4]:
        e = -world.get_snake(s).lenght
        for p in world.get_snake(s).get_body():
            dist_table[p.i][p.j] = e
            e += 1
    # for i in dist_table:
    #     print(i)
    dist_table[start.i][start.j] = 0
    candidates = [start]
    n = 0
    find = False
    last_dist = 0
    while find is False:
        if n == len(candidates):
            break
        candid = candidates[n]
        if dist_table[candid.i][candid.j] > last_dist:
            last_dist = dist_table[candid.i][candid.j]
            for I in range(len(dist_table)):
                for J in range(len(dist_table[I])):
                    if dist_table[I][J] > -1000 and dist_table[I][J] < 0:
                        dist_table[I][J] += 1
                        if dist_table[I][J] == 0:
                            dist_table[I][J] = -2000
        dist = dist_table[candid.i][candid.j]
        actions = get_nearest_pos(candid)
        for action in actions:
            if is_valid(action) is False:
                continue
            if action == target:
                find = True
                dist_table[action.i][action.j] = dist + 1
                break
            if dist_table[action.i][action.j] == -2000:
                dist_table[action.i][action.j] = dist + 1
                candidates.append(action)
        n += 1
    # print(find)
    # for i in dist_table:
    #     print(i)
    if find:
        find = False
        path_table = [[0 for _ in range(len(board[0]))] for __ in range(len(board))]
        last = target
        dir_number = 0
        while find is False:
            actions = get_nearest_pos(last)
            dir_number = 1
            for action in actions:
                if is_valid(action) is False:
                    continue
                if dist_table[action.i][action.j] == dist_table[last.i][last.j] - 1:
                    path_table[action.i][action.j] = dir_number
                    last = action
                if action == start:
                    find = True
                    break
                dir_number += 1
        dir_dic = ['u', 'd', 'l', 'r']
        # for i in path_table:
        #     print(i)
        return dist_table[target.i][target.j], dir_dic[dir_number - 1]
    return 1000, 'n'


def get_snakes_dist_to_goal(world: World):
    res = []
    for i in [1, 2, 3, 4]:
        head_pos = world.get_snake(i).get_head()
        dist_action = get_nearest_path(world, head_pos, world.goal_position, i)
        res.append(dist_action)
    return res


def get_eval_free_pos(snakes, free: Vector2D):
    array = [[0 for _ in range(max_i)] for _ in range(max_i)]
    q = []
    for s in range(3):
        q.append(snakes[s])
        array[q[-1].i][q[-1].j] = s + 1
    q.append(free)
    array[q[-1].i][q[-1].j] = 4
    while len(q) > 0:
        l = len(q)
        for i in range(l):
            p = q[i]
            nears = get_nearest_pos(p)
            for n in nears:
                if n.i >= max_i or n.i < 0:
                    continue
                if n.j >= max_j or n.j < 0:
                    continue
                if array[n.i][n.j] != 0:
                    continue
                q.append(n)
                array[n.i][n.j] = array[p.i][p.j]
        for i in range(l):
            del q[0]

    sum = 0
    for i in array:
        for j in i:
            if j == 4:
                sum += 1
    return sum


def go_to(world: World, target: Vector2D):
    head_pos = world.get_self().get_head()
    my_next_heads = get_nearest_pos(head_pos)  # [d, u, r, l]
    next_head_wall = [False for _ in range(4)]
    next_head_snake = [False for _ in range(4)]
    next_head_phead = [False for _ in range(4)]
    next_head_target = [False for _ in range(4)]
    next_head_dist = [0 for _ in range(4)]
    action_eval = [0 for _ in range(4)]

    h = 0
    for nhead in my_next_heads:
        if world.board[nhead.i][nhead.j] == -1:
            next_head_wall[h] = True
        if world.board[nhead.i][nhead.j] in [1, 2, 3, 4]:
            next_head_snake[h] = True
        if world.board[nhead.i][nhead.j] == 5:
            next_head_target[h] = True
        other_snake_phead = []
        for i in [1, 2, 3, 4]:
            if i == world.self_id:
                continue
            res = get_nearest_pos(world.get_snake(i).get_head())
            for r in res:
                other_snake_phead.append(r)
        if nhead in other_snake_phead:
            next_head_phead[h] = True
        next_head_dist[h] = get_nearest_path(world, nhead, target, world.self_id)
        h += 1

    best_action_number = 0
    best_action_eval = 1000000
    for a in range(4):
        action_eval[a] = next_head_dist[a][0]
        if next_head_target[a]:
            action_eval[a] = 0
        action_eval[a] += 1
        if next_head_wall[a] or next_head_snake[a]:
            action_eval[a] *= 1000
        if next_head_phead[a]:
            action_eval[a] *= 100

        if action_eval[a] < best_action_eval:
            best_action_eval = action_eval[a]
            best_action_number = a
        # print(my_next_heads[a], next_head_wall[a], next_head_snake[a], next_head_phead[a], next_head_dist[a],
        #       next_head_target[a], action_eval[a])

    actions = ['d', 'u', 'r', 'l']
    # print('best action:', best_action_number, actions[best_action_number])
    return actions[best_action_number]


def get_action(world: World):
    set_max(world)
    # for s in [1,2,3,4]:
    #     print(world.get_snake(s).body)
    dists_to_goal = get_snakes_dist_to_goal(world)
    # print('dist to goal=', dists_to_goal)
    dist_action = dists_to_goal[world.self_id - 1]
    mindist = 10000
    for da in dists_to_goal:
        if mindist > da[0]:
            mindist = da[0]
    near_snake = 0
    for da in dists_to_goal:
        if mindist == da[0]:
            near_snake += 1

    if dist_action[0] == mindist and near_snake == 1:
        # print('want to target')
        return go_to(world, world.goal_position)
    else:  # GO OTHER POS
        free_pos = []
        free_pos.append(Vector2D(6, 6))
        free_pos.append(Vector2D(6, 14))
        free_pos.append(Vector2D(6, 23))
        free_pos.append(Vector2D(14, 6))
        free_pos.append(Vector2D(14, 14))
        free_pos.append(Vector2D(14, 23))
        free_pos.append(Vector2D(23, 6))
        free_pos.append(Vector2D(23, 14))
        free_pos.append(Vector2D(23, 23))
        snake_heads = []
        for s in [1, 2, 3, 4]:
            if s == world.self_id:
                continue
            snake_heads.append(world.get_snake(s).get_head())
        best_free = None
        best_eval = 0
        for f in free_pos:
            e = get_eval_free_pos(snake_heads, f)
            if world.board[f.i][f.j] != 0:
                continue
            if e > best_eval:
                best_eval = e
                best_free = f

        # print('want to best free:', best_free)
        return go_to(world, best_free)
