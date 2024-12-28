# game.py

import math

# 定义常量
MAX_PLAYER = 1    # AI 玩家
MIN_PLAYER = -1   # 对手（人类玩家）
EMPTY = 0

BOARD_SIZE = 15    # 五子棋标准尺寸
WIN_COUNT = 5      # 连成五子获胜

class Board:
    def __init__(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.last_move = None  # 记录最后一次落子的位置（x, y, player）

    def make_move(self, x, y, player):
        """
        在指定位置落子。
        """
        if self.is_valid_move(x, y):
            self.board[x][y] = player
            self.last_move = (x, y, player)
            return True
        else:
            print(f"Invalid move attempted at ({x}, {y}) by player {player}.")
            return False

    def is_valid_move(self, x, y):
        """
        检查一个位置是否可以落子。
        """
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and self.board[x][y] == EMPTY

    def get_legal_moves(self):
        """
        生成所有可能的合法落子位置。
        优化：只考虑离已有棋子一定距离内的位置。
        """
        moves = set()
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.board[x][y] != EMPTY:
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.board[nx][ny] == EMPTY:
                            moves.add((nx, ny))
        if not moves:
            # 棋盘为空时，从中心开始
            center = BOARD_SIZE // 2
            return [(center, center)]
        return list(moves)

    def is_full(self):
        """
        检查棋盘是否已满。
        """
        for row in self.board:
            if EMPTY in row:
                return False
        return True

    def check_win(self, player):
        """
        检查指定玩家是否已获胜。
        """
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.board[x][y] != player:
                    continue
                # 检查横向
                if y + WIN_COUNT <= BOARD_SIZE and all(self.board[x][y + i] == player for i in range(WIN_COUNT)):
                    return True
                # 检查纵向
                if x + WIN_COUNT <= BOARD_SIZE and all(self.board[x + i][y] == player for i in range(WIN_COUNT)):
                    return True
                # 检查斜向
                if x + WIN_COUNT <= BOARD_SIZE and y + WIN_COUNT <= BOARD_SIZE and all(self.board[x + i][y + i] == player for i in range(WIN_COUNT)):
                    return True
                # 检查反斜向
                if x + WIN_COUNT <= BOARD_SIZE and y - WIN_COUNT >= -1 and all(self.board[x + i][y - i] == player for i in range(WIN_COUNT)):
                    return True
        return False

    def evaluate(self, player):
        """
        评估当前棋盘的状态。
        正数表示对 player 有利，负数表示对手有利。
        """
        score = 0
        opponent = MIN_PLAYER if player == MAX_PLAYER else MAX_PLAYER

        # 定义评分规则
        scoring_patterns = {
            "open_two": 10,
            "semi_open_two": 5,
            "open_three": 100,
            "semi_open_three": 50,
            "broken_three": 150,
            "open_four": 1000,
            "semi_open_four": 500,
            "broken_four": 300,
            "double_open_three": 800,
            "double_open_four": 1500,
            "five": 100000
        }

        # 计算AI的得分
        score += self.count_sequences(player, 2, "open_two") * scoring_patterns["open_two"]
        score += self.count_sequences(player, 2, "semi_open_two") * scoring_patterns["semi_open_two"]
        score += self.count_sequences(player, 3, "open_three") * scoring_patterns["open_three"]
        score += self.count_sequences(player, 3, "semi_open_three") * scoring_patterns["semi_open_three"]
        score += self.count_sequences(player, 3, "broken_three") * scoring_patterns["broken_three"]
        score += self.count_sequences(player, 4, "open_four") * scoring_patterns["open_four"]
        score += self.count_sequences(player, 4, "semi_open_four") * scoring_patterns["semi_open_four"]
        score += self.count_sequences(player, 4, "broken_four") * scoring_patterns["broken_four"]
        score += self.count_sequences(player, 3, "double_open_three") * scoring_patterns["double_open_three"]
        score += self.count_sequences(player, 4, "double_open_four") * scoring_patterns["double_open_four"]
        score += self.count_sequences(player, 5, "five") * scoring_patterns["five"]

        # 计算对手的得分，减去
        score -= self.count_sequences(opponent, 2, "open_two") * scoring_patterns["open_two"]
        score -= self.count_sequences(opponent, 2, "semi_open_two") * scoring_patterns["semi_open_two"]
        score -= self.count_sequences(opponent, 3, "open_three") * scoring_patterns["open_three"]
        score -= self.count_sequences(opponent, 3, "semi_open_three") * scoring_patterns["semi_open_three"]
        score -= self.count_sequences(opponent, 3, "broken_three") * scoring_patterns["broken_three"]
        score -= self.count_sequences(opponent, 4, "open_four") * scoring_patterns["open_four"]
        score -= self.count_sequences(opponent, 4, "semi_open_four") * scoring_patterns["semi_open_four"]
        score -= self.count_sequences(opponent, 4, "broken_four") * scoring_patterns["broken_four"]
        score -= self.count_sequences(opponent, 3, "double_open_three") * scoring_patterns["double_open_three"]
        score -= self.count_sequences(opponent, 4, "double_open_four") * scoring_patterns["double_open_four"]
        score -= self.count_sequences(opponent, 5, "five") * scoring_patterns["five"]

        # 增加多重威胁检测
        opponent_open_fours = self.count_sequences(opponent, 4, "open_four")
        if opponent_open_fours >= 2:
            score -= 20000  # 高额惩罚，迫使AI优先阻止多重威胁

        return score

    def count_sequences(self, player, length, pattern_type):
        """
        计算指定玩家在棋盘上特定模式的连子数。

        参数:
        - player: 玩家标识 (MAX_PLAYER 或 MIN_PLAYER)
        - length: 连子的长度
        - pattern_type: 模式类型 ("open_two", "semi_open_two", "open_three", "semi_open_three", "broken_four", "broken_three", "double_open_three", "double_open_four", "open_four", "semi_open_four", "five")

        返回:
        - int: 特定模式的连子数
        """
        count = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.board[x][y] != player:
                    continue
                for dx, dy in directions:
                    if self.check_sequence(x, y, dx, dy, player, length, pattern_type):
                        count += 1
        return count

    def check_sequence(self, x, y, dx, dy, player, length, pattern_type):
        """
        检查从 (x, y) 开始，方向 (dx, dy) 是否存在指定模式的连子。

        参数:
        - x, y: 起始位置
        - dx, dy: 方向
        - player: 玩家标识
        - length: 连子的长度
        - pattern_type: 模式类型

        返回:
        - bool: 是否存在指定模式的连子
        """
        if pattern_type == "five":
            # 五子连珠，直接判断
            for i in range(length):
                nx = x + i * dx
                ny = y + i * dy
                if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE):
                    return False
                if self.board[nx][ny] != player:
                    return False
            return True

        # 对于其他模式，进行更复杂的检查
        # 定义一个滑动窗口来检测模式
        window_size = length + 2  # 两端各一个
        window = []
        for i in range(-1, length + 1):
            nx = x + i * dx
            ny = y + i * dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                window.append(self.board[nx][ny])
            else:
                window.append(None)  # 表示边界

        # 根据 pattern_type 进行匹配
        if pattern_type == "open_two":
            return window == [EMPTY] + [player] * length + [EMPTY]
        elif pattern_type == "semi_open_two":
            return (window == [EMPTY] + [player] * length + [MIN_PLAYER] or
                    window == [MIN_PLAYER] + [player] * length + [EMPTY])
        elif pattern_type == "open_three":
            return window == [EMPTY] + [player] * length + [EMPTY]
        elif pattern_type == "semi_open_three":
            return (window == [EMPTY] + [player] * length + [MIN_PLAYER] or
                    window == [MIN_PLAYER] + [player] * length + [EMPTY])
        elif pattern_type == "open_four":
            return window == [EMPTY] + [player] * length + [EMPTY]
        elif pattern_type == "semi_open_four":
            return (window == [EMPTY] + [player] * length + [MIN_PLAYER] or
                    window == [MIN_PLAYER] + [player] * length + [EMPTY])
        elif pattern_type == "broken_four":
            # 检查是否存在中间缺子的四子，例如 X X _ X X
            # 允许一个空位出现在四个连续棋子中间
            # 这里以长度为4为例
            for gap in range(1, length):
                temp_sequence = []
                for i in range(length):
                    if i == gap:
                        temp_sequence.append(EMPTY)
                    else:
                        temp_sequence.append(player)
                # 构建完整的窗口
                expected_window = [EMPTY] + temp_sequence + [EMPTY]
                if window == expected_window:
                    return True
            return False
        elif pattern_type == "broken_three":
            # 检查是否存在中间缺子的三子，例如 X _ X
            # 允许一个空位出现在三个连续棋子中间
            # 这里以长度为3为例
            for gap in range(1, length):
                temp_sequence = []
                for i in range(length):
                    if i == gap:
                        temp_sequence.append(EMPTY)
                    else:
                        temp_sequence.append(player)
                # 构建完整的窗口
                expected_window = [EMPTY] + temp_sequence + [EMPTY]
                if window == expected_window:
                    return True
            return False
        elif pattern_type == "double_open_three":
            # 双活三，需要检查窗口中有两个开放三子
            count = 0
            for i in range(len(window) - 4):
                sub_window = window[i:i+5]
                if sub_window == [EMPTY, player, player, player, EMPTY]:
                    count += 1
            return count >= 2
        elif pattern_type == "double_open_four":
            # 双活四，类似双活三的逻辑
            count = 0
            for i in range(len(window) - 5):
                sub_window = window[i:i+6]
                if sub_window == [EMPTY, player, player, player, player, EMPTY]:
                    count += 1
            return count >= 2
        return False

    def clone(self):
        """
        返回棋盘的一个深拷贝。
        """
        new_board = Board()
        new_board.board = [row.copy() for row in self.board]
        new_board.last_move = self.last_move
        return new_board

    def print_board(self):
        """
        打印棋盘（仅用于调试）。
        """
        for row in self.board:
            print(' '.join(['●' if cell == MAX_PLAYER else '○' if cell == MIN_PLAYER else '·' for cell in row]))
        print()

    # 其他游戏相关的方法可以在这里添加
