# boyi.py

import math
from game import Board, MAX_PLAYER, MIN_PLAYER, EMPTY

def alpha_beta_search(board, depth, alpha, beta, maximizing_player):
    """
    实现基于博弈树的α-β剪枝搜索算法。

    参数:
    - board: 当前棋盘状态（Board 对象）。
    - depth: 搜索深度。
    - alpha: 当前的α值（初始为负无穷）。
    - beta: 当前的β值（初始为正无穷）。
    - maximizing_player: 布尔值，指示当前是否为最大化玩家（AI）。

    返回:
    - tuple: (评估分数, 最佳移动位置)
    """
    # 基本情况：达到搜索深度、棋盘满、或者有玩家获胜
    if depth == 0 or board.is_full() or board.check_win(MAX_PLAYER) or board.check_win(MIN_PLAYER):
        eval_score = board.evaluate(MAX_PLAYER)  # 从AI（MAX_PLAYER）的角度评估
        return eval_score, None

    legal_moves = board.get_legal_moves()

    # 移动排序：优先考虑中心附近和有潜在威胁的移动
    legal_moves = sort_moves(board, legal_moves, MAX_PLAYER)

    best_move = None

    if maximizing_player:
        max_eval = -math.inf
        for move in legal_moves:
            new_board = board.clone()
            new_board.make_move(move[0], move[1], MAX_PLAYER)
            eval, _ = alpha_beta_search(new_board, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # β剪枝
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in legal_moves:
            new_board = board.clone()
            new_board.make_move(move[0], move[1], MIN_PLAYER)
            eval, _ = alpha_beta_search(new_board, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break  # α剪枝
        return min_eval, best_move

def find_best_move(board, depth=3):
    """
    寻找AI的最佳落子位置。

    参数:
    - board: 当前棋盘状态（Board 对象）。
    - depth: 搜索深度（默认值为4）。

    返回:
    - tuple 或 None: 最佳移动位置 (x, y)，如果没有可行的移动则返回 None。
    """
    _, move = alpha_beta_search(board, depth, -math.inf, math.inf, True)
    return move

def sort_moves(board, moves, player):
    """
    对移动进行排序，优先考虑得分高的移动。

    参数:
    - board: 当前棋盘状态（Board 对象）。
    - moves: 移动列表。
    - player: 当前评估的玩家。

    返回:
    - list: 排序后的移动列表。
    """
    scored_moves = []
    for move in moves:
        x, y = move
        temp_board = board.clone()
        temp_board.make_move(x, y, player)
        score = temp_board.evaluate(player)
        scored_moves.append((score, move))
    scored_moves.sort(reverse=True)  # 从高到低排序
    sorted_moves = [move for score, move in scored_moves]
    return sorted_moves

if __name__ == "__main__":
    # 示例：初始化棋盘并查找最佳落子
    board = Board()
    # 假设AI先手，可以在中心落子
    board.make_move(7, 7, MAX_PLAYER)
    best_move = find_best_move(board, depth=4)
    print(f"AI最佳落子位置: {best_move}")
