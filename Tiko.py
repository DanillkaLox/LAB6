import tkinter as tk
from tkinter import messagebox
import math
import random

class TicoGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tico Game")
        self.difficulty = None
        self.difficulty_levels = {"Easy": 1, "Normal": 2, "Hard": 3}
        self.create_ui()
        self.choose_difficulty()

    def init_game(self):
        self.clear_controls()
        self.clear_board()

        self.board_size = 5
        self.cell_size = 80
        self.players = ["Black", "Red"]
        self.current_player = 1
        self.moves = 0
        self.max_moves = 8
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]

        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.moving_phase = False
        self.selected_piece = None
        self.highlight_rect = None

        self.new_game_button = tk.Button(self.controls_frame, text="New Game", command=self.choose_difficulty)
        self.new_game_button.pack(pady=10)

    def clear_controls(self):
        for widget in self.controls_frame.winfo_children():
            widget.destroy()

    def create_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()

        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.grid(row=0, column=0)

        self.controls_frame = tk.Frame(self.main_frame)
        self.controls_frame.grid(row=0, column=1, padx=10)

        self.canvas = tk.Canvas(self.canvas_frame, width=400, height=400)
        self.canvas.pack()

        self.new_game_button = tk.Button(self.controls_frame, text="New Game", command=self.choose_difficulty)
        self.new_game_button.pack(pady=10)

    def draw_board(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", width="2", fill="white")

    def clear_board(self):
        self.canvas.delete("all")

    def draw_board(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=2, fill="white")

    
    def handle_click(self, event):
        if self.current_player == 0:
            return 

        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if self.moving_phase:
            if self.selected_piece:
                if (row, col) == self.selected_piece:
                    self.deselect_piece()
                    return
                if self.is_valid_move(self.selected_piece, (row, col)):
                    self.move_piece(self.selected_piece, (row, col))
                    self.deselect_piece()
                    if self.check_winner():
                        messagebox.showinfo("Tico Game", "You win!")
                        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
                        self.choose_difficulty()
                    self.current_player = 0
                    self.ai_move()
                else:
                    messagebox.showwarning("Invalid Move", "You cannot move there!")
            elif self.board[row][col] == self.current_player:
                self.select_piece((row, col))
        else:
            if self.board[row][col] is not None:
                return

            self.place_piece(row, col, self.current_player)

            if self.check_winner():
                messagebox.showinfo("Tico Game", "You win!")
                self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
                self.choose_difficulty()
            else:

                self.moves += 1

                self.current_player = 0
                self.ai_move()

    def ai_move(self):
        if self.moving_phase:
            best_move = self.minimax(self.board, self.difficulty, -math.inf, math.inf, True)[1]
            if best_move and self.difficulty == 1 and random.random() < 0.3:  
                all_moves = self.get_all_moves(self.board, 0)
                best_move = random.choice(all_moves) if all_moves else best_move
            elif best_move and self.difficulty == 2 and random.random() < 0.1: 
                all_moves = self.get_all_moves(self.board, 0)
                best_move = random.choice(all_moves) if all_moves else best_move

            if best_move:
                self.move_piece(best_move[0], best_move[1])
        else:
            best_placement = self.minimax_placement(self.board, self.difficulty, -math.inf, math.inf, True)[1]
            if best_placement and self.difficulty == 1 and random.random() < 0.3:  
                empty_cells = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if self.board[r][c] is None]
                best_placement = random.choice(empty_cells) if empty_cells else best_placement
            elif best_placement and self.difficulty == 2 and random.random() < 0.1: 
                empty_cells = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if self.board[r][c] is None]
                best_placement = random.choice(empty_cells) if empty_cells else best_placement

            if best_placement:
                row, col = best_placement
                self.place_piece(row, col, 0)
                self.moves += 1
                if self.moves == self.max_moves:
                    messagebox.showinfo("Tico Game", "Starting movement phase!")
                    self.moving_phase = True

        if self.check_winner():
            messagebox.showinfo("Tico Game", "AI wins!")
            self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
            self.choose_difficulty()
        else:

            self.current_player = 1

    def minimax_placement(self, board, depth, alpha, beta, maximizing):
        if self.check_winner(board) or depth == 0:
            return self.evaluate_board(board, depth), None

        if maximizing:
            max_eval = -math.inf
            best_placement = None
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if board[row][col] is None:
                        new_board = [row[:] for row in board]
                        new_board[row][col] = 0
                        eval = self.minimax_placement(new_board, depth - 1, alpha, beta, False)[0]
                        if eval > max_eval:
                            max_eval = eval
                            best_placement = (row, col)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
            return max_eval, best_placement
        else:
            min_eval = math.inf
            best_placement = None
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if board[row][col] is None:
                        new_board = [row[:] for row in board]
                        new_board[row][col] = 1
                        eval = self.minimax_placement(new_board, depth - 1, alpha, beta, True)[0]
                        if eval < min_eval:
                            min_eval = eval
                            best_placement = (row, col)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
            return min_eval, best_placement

    def minimax(self, board, depth, alpha, beta, maximizing):
        if self.check_winner(board) or depth == 0:
            return self.evaluate_board(board, depth), None

        if maximizing:
            max_eval = -math.inf
            best_move = None
            for move in self.get_all_moves(board, 0):
                new_board = self.make_move(board, move[0], move[1])
                eval = self.minimax(new_board, depth - 1, alpha, beta, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            best_move = None
            for move in self.get_all_moves(board, 1):
                new_board = self.make_move(board, move[0], move[1])
                eval = self.minimax(new_board, depth - 1, alpha, beta, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_board(self, board, depth):
        def check_winner(board, player):
            def check_line(start_row, start_col, d_row, d_col):
                count = 0
                for i in range(4):
                    r = start_row + i * d_row
                    c = start_col + i * d_col
                    if 0 <= r < self.board_size and 0 <= c < self.board_size and board[r][c] == player:
                        count += 1
                    else:
                        count = 0
                    if count == 4:
                        return True
                return False

            def check_square():
                for row in range(self.board_size - 1):
                    for col in range(self.board_size - 1):
                        if (board[row][col] == player and
                            board[row + 1][col] == player and
                            board[row][col + 1] == player and
                            board[row + 1][col + 1] == player):
                            return True
                return False

            for row in range(self.board_size):
                for col in range(self.board_size):
                    if board[row][col] == player:
                        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                        if any(check_line(row, col, d_row, d_col) for d_row, d_col in directions) or check_square():
                            return True
            return False

        if check_winner(board, 1):
            return -3000 - depth*100000
        if check_winner(board, 0):
            return 30000 + depth*10 
        score = 0
        for row in range(self.board_size):
            for col in range(self.board_size):
                for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    player_count = 0
                    opponent_count = 0
                    for i in range(4):
                        r, c = row + dr * i, col + dc * i
                        if 0 <= r < self.board_size and 0 <= c < self.board_size:
                            if board[r][c] == 0: 
                                player_count += 1
                            elif board[r][c] == 1: 
                                opponent_count += 1
                    if player_count > 0 and opponent_count == 0:
                        score += 10 ** player_count
                    if opponent_count > 0 and player_count == 0:
                        score -= 10 ** opponent_count

        for row in range(self.board_size - 1):
            for col in range(self.board_size - 1):
                square = [
                    board[row][col], board[row + 1][col],
                    board[row][col + 1], board[row + 1][col + 1]
                ]
                if square.count(0) == 4:
                    score += 100
                if square.count(1) == 4:
                    score -= 100

        return score


    def get_all_moves(self, board, player):
        moves = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if board[r][c] == player:
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            if 0 <= r + dr < self.board_size and 0 <= c + dc < self.board_size and board[r + dr][c + dc] is None:
                                moves.append(((r, c), (r + dr, c + dc)))
        return moves

    def make_move(self, board, start, end):
        new_board = [row[:] for row in board]
        new_board[end[0]][end[1]] = new_board[start[0]][start[1]]
        new_board[start[0]][start[1]] = None
        return new_board

    def place_piece(self, row, col, player):
        player_color = "black" if player == 0 else "red"
        self.canvas.create_oval(
            col * self.cell_size + 10, row * self.cell_size + 10,
            (col + 1) * self.cell_size - 10, (row + 1) * self.cell_size - 10,
            fill=player_color
        )
        self.board[row][col] = player

    def is_valid_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        if self.board[end_row][end_col] is not None:
            return False
        return abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1

    def move_piece(self, start, end):
        start_row, start_col = start
        end_row, end_col = end

        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = self.current_player

        player_color = "black" if self.current_player == 0 else "red"
        self.canvas.create_rectangle(
            start_col * self.cell_size + 2, start_row * self.cell_size + 2,
            (start_col + 1) * self.cell_size - 2, (start_row + 1) * self.cell_size - 2,
            width="0", fill="white"
        )
        self.canvas.create_oval(
            end_col * self.cell_size + 10, end_row * self.cell_size + 10,
            (end_col + 1) * self.cell_size - 10, (end_row + 1) * self.cell_size - 10,
            fill=player_color
        )

        self.animate_move(start, end, player_color)

    def select_piece(self, position):
        row, col = position
        self.selected_piece = position
        x1 = col * self.cell_size + 2
        y1 = row * self.cell_size + 2
        x2 = (col + 1) * self.cell_size - 2 
        y2 = (row + 1) * self.cell_size - 2 
        self.highlight_rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)
    
    def deselect_piece(self):
        if self.highlight_rect:
            self.canvas.delete(self.highlight_rect)
            self.highlight_rect = None
        self.selected_piece = None

    def check_winner(self, board=None):
        if board is None:
            board = self.board 

        def check_line(start_row, start_col, d_row, d_col):
            count = 0
            for i in range(-3, 4):
                r = start_row + i * d_row
                c = start_col + i * d_col
                if 0 <= r < self.board_size and 0 <= c < self.board_size and board[r][c] == self.current_player:
                    count += 1
                    if count == 4:
                        return True
                else:
                    count = 0
            return False

        def check_square():
            for row in range(self.board_size - 1):
                for col in range(self.board_size - 1):
                    if (board[row][col] == self.current_player and
                        board[row + 1][col] == self.current_player and
                        board[row][col + 1] == self.current_player and
                        board[row + 1][col + 1] == self.current_player):
                        return True
            return False

        for row in range(self.board_size):
            for col in range(self.board_size):
                if board[row][col] == self.current_player:
                    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                    if any(check_line(row, col, d_row, d_col) for d_row, d_col in directions) or check_square():
                        return True
        return False

    def run(self):
        self.root.mainloop()

    def choose_difficulty(self):
        self.clear_board()

        for widget in self.controls_frame.winfo_children():
            widget.destroy()

        tk.Label(self.controls_frame, text="Select Difficulty:", font=("Arial", 14)).pack(pady=10)
        for level in self.difficulty_levels.keys():
            tk.Button(self.controls_frame, text=level, font=("Arial", 12),
                      command=lambda lvl=level: self.start_game(lvl)).pack(pady=5)
                    
    def start_game(self, level):
        self.difficulty = self.difficulty_levels[level]
        self.init_game()

    def animate_move(self, start, end, player_color):
        start_row, start_col = start
        end_row, end_col = end

        x1_start = start_col * self.cell_size + 10
        y1_start = start_row * self.cell_size + 10
        x2_start = (start_col + 1) * self.cell_size - 10
        y2_start = (start_row + 1) * self.cell_size - 10

        x1_end = end_col * self.cell_size + 10
        y1_end = end_row * self.cell_size + 10
        x2_end = (end_col + 1) * self.cell_size - 10
        y2_end = (end_row + 1) * self.cell_size - 10

        steps = 10
        dx1 = (x1_end - x1_start) / steps
        dy1 = (y1_end - y1_start) / steps
        dx2 = (x2_end - x2_start) / steps
        dy2 = (y2_end - y2_start) / steps

        piece = self.canvas.create_oval(x1_start, y1_start, x2_start, y2_start, fill=player_color)

        def step_animation(step=0):
            if step < steps:
                self.canvas.move(piece, dx1, dy1)
                self.root.after(50, step_animation, step + 1)
            else:
                self.canvas.delete(piece)
                self.canvas.create_oval(x1_end, y1_end, x2_end, y2_end, fill=player_color)

        step_animation()

if __name__ == "__main__":
    game = TicoGame()
    game.run()